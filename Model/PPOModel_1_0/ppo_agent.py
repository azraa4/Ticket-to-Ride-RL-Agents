import os
import torch
import torch.nn as nn
import torch.optim as optim

from Model.PPOModel_1_0.actor_critic import PPOActorCritic
from Model.PPOModel_1_0.rollout_buffer import RolloutBuffer
import random
import global_vars

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #GPU


class PPOAgent:
    def __init__(self, color, game_service, lr=0.0005, update_timestep=2000, clip_param=0.1, K_epochs=6, gamma=0.99):
        torch.manual_seed(global_vars.random_seed())
        random.seed(global_vars.random_seed())

        self.color = color
        self.game_service = game_service
        self.gamma = gamma
        self.update_timestep = update_timestep    # Number of steps before an update
        self.clip_param = clip_param              # PPO clipping parameter
        self.K_epochs = K_epochs                  # Number of epochs per update

        # Define fixed state size and discrete action space
        self.state_size = 11  # same as before
        self.action_space = ["claim_route", "draw_blind", "draw_red_card", "draw_blue_card", "draw_yellow_card",
                             "draw_green_card", "draw_pink_card", "draw_orange_card", "draw_white_card",
                             "draw_black_card", "draw_joker_card", "end_of_game"]

        # Create PPO network and optimizer
        self.model = PPOActorCritic(self.state_size, len(self.action_space)).to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

        self.filename = "ppoagent_2.pth"
        self.load_model()

        # Initialize rollout buffer and timestep counter
        self.buffer = RolloutBuffer()
        self.timestep = 0

        # Agent–specific variables (same purpose as in DDQNAgent)
        self.first_turn = True
        self.routes_needed_to_claim = []
        self.total_episode_reward = 0

        # Logging
        self.log_file = "ppo_training_loss.txt"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("episode,timestep,loss\n")
        self.episode_count = 0
        self.timestep_count = 0


    def get_action_mask(self):
        """
        Returns a mask (shape: [1, num_actions]) where valid actions have 0 and invalid actions have a very low value.
        """
        available_actions = self.get_available_actions_for_dqn()
        valid_indices = [self.action_space.index(action) for action in available_actions]
        mask = torch.full((len(self.action_space),), -1e9, device=device)
        for idx in valid_indices:
            mask[idx] = 0.0
        return mask.unsqueeze(0)

    def get_state(self):
        """
        Builds the state tensor based on game state and player state.
        """
        game_state = self.game_service.get_game_state()
        current_player_state = self.game_service.get_current_player_state()

        # Example state features (same as in DDQNAgent)
        my_score = current_player_state["current score"]
        needed_colors = self.needed_colors()
        max_length_of_claimable_routes = self.get_length_of_max_claimable_route()
        needed_red = needed_colors["red"]
        needed_blue = needed_colors["blue"]
        needed_green = needed_colors["green"]
        needed_yellow = needed_colors["yellow"]
        needed_orange = needed_colors["orange"]
        needed_pink = needed_colors["pink"]
        needed_white = needed_colors["white"]
        needed_black = needed_colors["black"]

        car_state = 0
        min_cars = min(p["remaining_train_cars"] for p in game_state["players"])
        if 6 < min_cars <= 12:
            car_state = 0.5
        elif 2 < min_cars <= 6:
            car_state = 0.8
        elif min_cars <= 2:
            car_state = 1

        if self.routes_needed_to_claim:
            destinations_completed = 0
        else:
            destinations_completed = 1

        state_vector = [
            car_state * 3,
            destinations_completed * 1.5,
            max_length_of_claimable_routes/6 * 2,
            needed_red/6,
            needed_blue/6,
            needed_green/6,
            needed_yellow/6,
            needed_orange/6,
            needed_pink/6,
            needed_white/6,
            needed_black/6,
        ]
        state_tensor = torch.tensor(state_vector, dtype=torch.float32, device=device).unsqueeze(0)
        action_mask = self.get_action_mask()
        return state_tensor, action_mask

    def choose_action(self):
        """
        Samples an action from the PPO policy.
        """
        state, action_mask = self.get_state()
        action_logits, state_value = self.model(state)
        # Apply action mask so that invalid actions are set to very low probability
        masked_logits = action_logits + action_mask
        action_probs = torch.softmax(masked_logits, dim=-1)
        print("Action probabilities:", action_probs.cpu().detach().numpy())
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        if log_prob.dim() == 0:
            log_prob = log_prob.unsqueeze(0)
        # Save for later PPO update
        self.buffer.states.append(state)
        self.buffer.actions.append(action)
        self.buffer.log_probs.append(log_prob)
        self.buffer.state_values.append(state_value)
        chosen_action = self.action_space[action.item()]

        return chosen_action

    def perform_action(self):
        """
        Executes an action, stores the reward and terminal flag, and triggers PPO updates periodically.
        """
        if self.first_turn:
            self.first_turn = False
            action_params = {"selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()[:2]}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.get_available_actions_for_dqn()
        if not available_actions:
            self.game_service.pass_the_turn()
            return

        action = self.choose_action()
        reward, next_state, done = self.execute_action(action)
        self.buffer.rewards.append(reward)
        self.buffer.is_terminals.append(done)
        self.timestep += 1
        self.timestep_count += 1
        self.total_episode_reward += reward

        print("################## ⚔ PLAYER INFO ######################")
        print("#  AVAILABLE ACTIONS:", available_actions)
        print("#  SELECTED ACTION: ", action)
        print("#  THE REWARD: ", reward)
        print("########################################################")

        print("\n\n")

        # When enough timesteps are collected, update the policy
        if self.timestep >= self.update_timestep:
            self.update()
            self.timestep = 0

        with open("ppo_actions_log.txt", "a") as f:
            f.write(f"{action}\n")

    def execute_action(self, action):
        """
        Execute the chosen action and return (reward, next_state, done).
        """
        if action == "claim_route":
            reward = self.claim_route()
        elif action == "draw_blind":
            reward = self.draw_blind()
        elif action == "draw_red_card":
            reward = self.draw_colored("red")
        elif action == "draw_blue_card":
            reward = self.draw_colored("blue")
        elif action == "draw_yellow_card":
            reward = self.draw_colored("yellow")
        elif action == "draw_green_card":
            reward = self.draw_colored("green")
        elif action == "draw_pink_card":
            reward = self.draw_colored("pink")
        elif action == "draw_orange_card":
            reward = self.draw_colored("orange")
        elif action == "draw_white_card":
            reward = self.draw_colored("white")
        elif action == "draw_black_card":
            reward = self.draw_colored("black")
        elif action == "draw_joker_card":
            reward = self.draw_joker()
        else:
            reward = 0

        next_state = self.get_state()
        done = False
        return reward, next_state, done

    def update(self):
        """
        Updates the policy and value function using the PPO clipped objective.
        """
        # Convert collected lists to tensors
        states = torch.cat(self.buffer.states)
        actions = torch.tensor([a.item() for a in self.buffer.actions], dtype=torch.long, device=device)
        old_log_probs = torch.stack([lp if lp.dim() > 0 else lp.unsqueeze(0) for lp in self.buffer.log_probs]).detach()
        state_values = torch.cat(self.buffer.state_values).squeeze(-1).detach()

        # Compute discounted rewards
        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=device)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)

        # Compute advantages
        advantages = rewards - state_values

        total_loss = 0
        for _ in range(self.K_epochs):
            action_logits, state_vals = self.model(states)

            action_probs = torch.softmax(action_logits, dim=-1)

            dist = torch.distributions.Categorical(action_probs)
            new_log_probs = dist.log_prob(actions)
            # Calculate ratio (new probability / old probability)
            ratios = torch.exp(new_log_probs - old_log_probs)
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.clip_param, 1 + self.clip_param) * advantages
            loss_actor = -torch.min(surr1, surr2).mean()
            loss_critic = nn.MSELoss()(state_vals.squeeze(-1), rewards)
            loss = loss_actor + 0.5 * loss_critic

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()

        with open(self.log_file, "a") as f:
            f.write(f"{self.episode_count},{self.timestep_count},{total_loss / self.K_epochs}\n")
        self.buffer.clear()

    def load_model(self):
        print("LOADING...")
        model_filename = self.filename
        if not os.path.exists(model_filename):
            print("⚠️ No saved PPO model found. Starting with a fresh model.")
            return
        try:
            checkpoint = torch.load(model_filename, map_location=device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print(f"✅ PPO model {model_filename} loaded successfully.")
        except Exception as e:
            print(f"⚠️ Could not load {model_filename}: {e}")

    def save_model_ppo(self):
        print("SAVING...")
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }
        model_filename = self.filename
        temp_filename = model_filename + ".tmp"
        with open(temp_filename, 'wb') as f:
            torch.save(checkpoint, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_filename, model_filename)
        with open("ppo_scores.txt", "a") as file:
            file.write(str(self.total_episode_reward) + ",")

    def get_available_actions_for_dqn(self):
        available_actions = self.game_service.get_available_actions(self.color)
        current_player_state = self.game_service.get_current_player_state()
        game_state = self.game_service.get_game_state()
        available_actions_in_detail = []

        if "claim_route" in available_actions:
            available_actions_in_detail.append("claim_route")

        if "draw_train_card" in available_actions:
            if self.game_service.get_availability_of_blind_pick():
                available_actions_in_detail.append("draw_blind")
            for card in game_state["train_cards_on_the_table"]:
                if card.color == "yellow":
                    available_actions_in_detail.append("draw_yellow_card")
                elif card.color == "red":
                    available_actions_in_detail.append("draw_red_card")
                elif card.color == "blue":
                    available_actions_in_detail.append("draw_blue_card")
                elif card.color == "white":
                    available_actions_in_detail.append("draw_white_card")
                elif card.color == "orange":
                    available_actions_in_detail.append("draw_orange_card")
                elif card.color == "pink":
                    available_actions_in_detail.append("draw_pink_card")
                elif card.color == "black":
                    available_actions_in_detail.append("draw_black_card")
                elif card.color == "green":
                    available_actions_in_detail.append("draw_green_card")
                elif card.color == "joker":
                    available_actions_in_detail.append("draw_joker_card")

        return list(set(available_actions_in_detail))

    def apply_final_reward(self, final_reward):
        """
        Called at game end to apply a terminal reward.
        """
        last_state, last_state_mask = self.get_state()
        done = True
        action_idx = self.action_space.index("end_of_game")

        # Save final transition in the buffer
        self.buffer.states.append(last_state)
        self.buffer.actions.append(torch.tensor(action_idx, device=device))
        self.buffer.log_probs.append(torch.tensor([0.0], device=device))
        self.buffer.state_values.append(torch.zeros((1, 1), device=device))
        self.buffer.rewards.append(final_reward)
        self.buffer.is_terminals.append(done)

        self.update()
        self.total_episode_reward += final_reward
        self.episode_count += 1

        self.save_model_ppo()

    """ACTIONS PART"""
    def draw_blind(self):
        """
        Draws a train card.
        """
        action_params = {"selected_card": "select_blind"}
        returned_item = self.game_service.perform_action("draw_train_card", action_params)
        self.game_service.log(f"{self.color}, Action: DRAW BLIND CARDS")

        current_state = self.game_service.get_current_player_state()
        train_cards_list = current_state["train_cards"]
        self.game_service.log(f"Having these train cards: {train_cards_list}")

        return -1  # Reward for drawing blind train cards

    def draw_colored(self, color):
        needed_colors = self.needed_colors()
        needed_color_count = needed_colors[color]

        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]

        for card in train_cards_on_the_table:
            if card.color == color:
                action_params = {"selected_card": card}
                self.game_service.perform_action("draw_train_card", action_params)
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {card.color}")
                break

        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]

        print(train_cards_on_the_table)

        pass_bool = True
        needed_colors_list = [clr for clr, value in needed_colors.items() if value > 0]
        check_for_other_colors = True
        for clr in needed_colors_list:
            for card in train_cards_on_the_table:
                if card.color == clr:
                    action_params = {"selected_card": card}
                    self.game_service.perform_action("draw_train_card", action_params)
                    self.game_service.log(f"{self.color}, Action: DRAW SECOND TRAIN CARD, {card.color}")
                    pass_bool = False
                    check_for_other_colors = False
                    break
            if not check_for_other_colors:
                break

        if pass_bool:
            for card in train_cards_on_the_table:
                if card.color != "joker":
                    action_params = {"selected_card": card}
                    self.game_service.perform_action("draw_train_card", action_params)
                    self.game_service.log(f"{self.color}, Action: DRAW SECOND TRAIN CARD, {card.color}")
                    pass_bool = False
                    break

        if pass_bool:
            self.game_service.pass_draw_second_train_card()
            print("PASSED SECOND TRAIN CARD")

        if 0 < needed_color_count or not self.routes_needed_to_claim:
            return 1
        else:
            return -2

    def draw_joker(self):
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]
        for card in train_cards_on_the_table:
            if card.color == "joker":
                action_params = {"selected_card": card}
                self.game_service.perform_action("draw_train_card", action_params)
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {card.color}")
                break

        return 2

    def claim_route(self):
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]
        routes_available_to_claim = list(set(claimable_routes) & set(self.routes_needed_to_claim))
        routes_available_to_claim = sorted(routes_available_to_claim, key=lambda route: route.length)

        length_to_points = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

        if routes_available_to_claim:
            route = routes_available_to_claim[-1]
            if route.color == "gray":
                action_params = {"selected_route": route, "use_this_color": None}
                cards_can_be_used_to_claim_gray_route = self.game_service.perform_action("claim_route", action_params)

                self.game_service.change_status_text(f"{self.color} claiming a gray route.")

                use_random_color = random.choice(cards_can_be_used_to_claim_gray_route)
                action_params = {"selected_route": route, "use_this_color": use_random_color}
                self.game_service.perform_action("claim_route", action_params)
                self.game_service.change_status_text(f"{self.color} claimed a gray route with {use_random_color}")
                self.game_service.log(f"{self.color}, Action: CLAIM GRAY ROUTE, {route.city1} to {route.city2}, {use_random_color}")
            else:
                action_params = {"selected_route": route, "use_this_color": None}
                self.game_service.perform_action("claim_route", action_params)
                self.game_service.change_status_text(f"{self.color} claimed a colored route.")
                self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {route.city1} to {route.city2}")
            return length_to_points[route.length]
        else:
            return self.claim_route_random()

    def claim_route_random(self):
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]
        max_length_route = sorted(claimable_routes, key=lambda route: route.length)
        length_to_points = {1: 1, 2: 2, 3: 4, 4: 7, 5: 10, 6: 15}

        if claimable_routes:
            random_route = max_length_route[-1]

            if random_route.color == "gray":
                #console print("AI: A GRAY ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                cards_can_be_used_to_claim_gray_route = self.game_service.perform_action("claim_route", action_params)

                self.game_service.change_status_text(f"{self.color} claiming a gray route.")

                use_random_color = random.choice(cards_can_be_used_to_claim_gray_route)
                action_params = {"selected_route": random_route, "use_this_color": use_random_color}
                self.game_service.perform_action("claim_route", action_params)

                self.game_service.change_status_text(f"{self.color} claimed a gray route with {use_random_color}")
                self.game_service.log(f"{self.color}, Action: CLAIM GRAY ROUTE, {random_route.city1} to {random_route.city2}, {use_random_color}")


            else:
                #console print("AI: A COLORED ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                self.game_service.perform_action("claim_route", action_params)

                self.game_service.change_status_text(f"{self.color} claimed a colored route.")
                self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {random_route.city1} to {random_route.city2}")

            self.game_service.change_status_text("TURN CHANGED.")

            if self.routes_needed_to_claim:
                return -3
            else:
                return length_to_points[random_route.length]
        else:
            raise ValueError("CLAIMABLE ROUTE YOKKEN NASIL CLAIMLEMEYE CALISIYON!")

    def needed_colors(self):
        game_state = self.game_service.get_game_state()
        current_player_state = self.game_service.get_current_player_state()
        self.routes_needed_to_claim = []

        for dest_card in current_player_state["destination_cards"]:
            path = self.game_service.compute_shortest_path_between_cities(dest_card.city1, dest_card.city2, game_state["unclaimed_routes"], current_player_state["claimed routes"])
            if path is not None:
                self.routes_needed_to_claim.extend(path)

        self.routes_needed_to_claim = list(set(self.routes_needed_to_claim)-set(current_player_state["claimed routes"]))

        needed_colors = {
            "red": 0,
            "blue": 0,
            "green": 0,
            "yellow": 0,
            "orange": 0,
            "pink": 0,
            "black": 0,
            "white": 0,
        }

        for route in self.routes_needed_to_claim:
            if route.color!="gray":
                needed_colors[route.color] += route.length

        inventory = {
            "red": 0,
            "blue": 0,
            "green": 0,
            "yellow": 0,
            "orange": 0,
            "pink": 0,
            "black": 0,
            "white": 0,
            "joker": 0
        }

        for card in current_player_state["train_cards"]:
            inventory[card.color] += 1

        print("🎒 INVENTORY OF THE PLAYER:", inventory)

        if not self.routes_needed_to_claim:
            print("routes_needed_to_claim is empty! 6-inventory")
            for color in ["red", "blue", "green", "yellow", "orange", "pink", "black", "white"]:
                needed_colors[color] = max(0, 6 - inventory[color] - inventory["joker"])

            print("🎨 NEEDED COLORS:", needed_colors)

            return needed_colors

        for color in ["red", "blue", "green", "yellow", "orange", "pink", "black", "white"]:
            needed_colors[color] = max(0, needed_colors[color] - inventory[color] - inventory["joker"])

        print("🎨 NEEDED COLORS:", needed_colors)
        return needed_colors

    def get_length_of_max_claimable_route(self):
        current_player_state = self.game_service.get_current_player_state()
        if self.routes_needed_to_claim:
            claimable_routes = set(self.routes_needed_to_claim) & set(current_player_state["claimable_routes"])
            return max((route.length for route in claimable_routes), default = 0)

        claimable_routes = self.game_service.get_current_player_state()["claimable_routes"]
        if not claimable_routes:
            return 0
        return max(route.length for route in claimable_routes)

    '''
    def _count_train_cards_by_color(self, train_cards):
        """
        Helper function to count the agent's train cards by color.
        Input: A list of card objects, each presumably having a .color attribute.
        Returns: dict mapping color -> number of cards
        """
        color_counts = {}
        for card in train_cards:
            c = card.color.lower()
            color_counts[c] = color_counts.get(c, 0) + 1
        return color_counts
    '''