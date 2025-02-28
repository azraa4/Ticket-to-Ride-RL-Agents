import os
from collections import deque
import torch
import torch.nn.functional as F
import torch.optim as optim

import global_vars
from Model.DQNModel.dqn import DQN
from Model.DQNModel.replay_memory import ReplayMemory
import random
import heapq

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #GPU


class DDQNAgent:
    def __init__(self, color, game_service, gamma=0.99, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.995, lr=0.001,
                 memory_size=100000, batch_size=128):
        self.color = color
        self.game_service = game_service

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.model_filename = f"ddqn_model_1_0_5.pth"  # Model file for saving/loading

        # Define fixed state size and action space
        self.state_size = 10  # Fixed number of state features
        self.action_space = ["claim_route", "draw_blind", "draw_red_card", "draw_blue_card", "draw_yellow_card",
                             "draw_green_card", "draw_pink_card", "draw_orange_card", "draw_white_card",
                             "draw_black_card", "draw_joker_card", "end_of_game"]  # Fixed action space

        # Neural Networks
        self.model = DQN(self.state_size, len(self.action_space)).to(device)
        self.target_model = DQN(self.state_size, len(self.action_space)).to(device)
        self.target_model.load_state_dict(self.model.state_dict())  # Copy weights
        self.target_model.eval()

        # Optimizer and memory
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.memory = ReplayMemory(memory_size)

        # Try loading an existing model if available
        self.load_model()

        #Agent specific
        self.first_turn = True
        self.routes_needed_to_claim = []

        self.total_episode_reward = 0

        #print loss
        self.log_file = "training_loss.txt"
        # Optionally, clear or create a new file at the start
        with open(self.log_file, "w") as f:
            f.write("episode,batch,loss\n")  # CSV header line

        self.episode_count = 0
        self.batch_count = 0


        '''
        print("Model is on device:", next(self.model.parameters()).device)

        print("PyTorch version:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("Number of GPUs:", torch.cuda.device_count())
            print("Current device index:", torch.cuda.current_device())
            print("Device name:", torch.cuda.get_device_name(0))
        '''


    def get_state(self):
        """
        An expanded state representation for Ticket to Ride.
        Feel free to adjust the features based on your training experiments.
        """
        game_state = self.game_service.get_game_state()
        current_player_state = self.game_service.get_current_player_state()

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
        elif min_cars <= 6:
            car_state = 1

        state_vector = [
            max_length_of_claimable_routes/6,
            car_state,
            needed_red/6,
            needed_blue/6,
            needed_green/6,
            needed_yellow/6,
            needed_orange/6,
            needed_pink/6,
            needed_white/6,
            needed_black/6,
        ]

        print(state_vector)
        print("NEEDED COLORS: ",needed_colors)

        return torch.tensor(state_vector, dtype=torch.float32, device=device).unsqueeze(0)


    def choose_action(self):
        """
        Selects an action using an epsilon-greedy policy, ensuring only valid actions are chosen.
        """
        available_actions = self.get_available_actions_for_dqn()

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)  # Random exploration within available actions
        else:
            state = self.get_state()
            with torch.no_grad():
                q_values = self.model(state)  # Get Q-values for all actions

            # Convert action names to indices (action space mapping)
            action_indices = [self.action_space.index(action) for action in available_actions]
            print(action_indices)

            # Get the best Q-value action among the available ones
            best_action_index = max(action_indices, key=lambda idx: q_values[0, idx].item())

            for idx in action_indices:
                print(f"Q[{idx}] = {q_values[0, idx].item()}")

            print(f"Selected action: index: {best_action_index}, action: {self.action_space[best_action_index]}, q value: {q_values[0, best_action_index].item()}")
            print(q_values)


            return self.action_space[best_action_index]

    def perform_action(self):
        """
        Execute an action, store experience, and train the model.
        """

        if self.first_turn:
            #console print(f"It is the first turn of {self.color}ed DeepQNetworkAgent")
            self.first_turn = False
            action_params = {
                "selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()[:2]}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.get_available_actions_for_dqn()
        if not available_actions:
            self.game_service.pass_the_turn()
            return
        
        print("available actions:", available_actions)

        action = self.choose_action()
        state = self.get_state()
        reward, next_state, done = self.execute_action(action)

        print("THIS IS THE REWARD: ", reward)

        # Store experience in replay memory
        # NEW - store action as an integer index
        action_idx = self.action_space.index(action)
        self.memory.push(state, action_idx, reward, next_state, done)

        # Train the model
        self.replay()

    def execute_action(self, action):
        """
        Executes the chosen action and returns (reward, next_state, done).
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

        self.total_episode_reward += reward

        return reward, next_state, done

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        self.batch_count += 1

        batch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        # Concatenate states and next_states. E.g. each is a single Tensor [1, 24], so we do:
        states = torch.cat(states).to(device)  # shape: [batch_size, 24]
        next_states = torch.cat(next_states).to(device)  # shape: [batch_size, 24]
        actions = torch.tensor(actions, dtype=torch.long, device=device)  # shape: [batch_size]
        rewards = torch.tensor(rewards, dtype=torch.float32, device =device)  # shape: [batch_size]
        dones = torch.tensor(dones, dtype=torch.float32, device=device)  # shape: [batch_size]

        # 1) Current Q-values
        q_values = self.model(states)  # shape: [batch_size, num_actions]
        q_values_for_actions = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # 2) Target Q-values for Double DQN
        with torch.no_grad():
            # Use the online network to select the best next action
            next_q_values_online = self.model(next_states)
            next_actions = next_q_values_online.argmax(dim=1, keepdim=True)

            # Use the target network to evaluate the chosen action
            next_q_values_target = self.target_model(next_states).gather(1, next_actions).squeeze(1)

            target = rewards + (1 - dones) * self.gamma * next_q_values_target


        # 3) Loss only for the chosen actions
        loss = F.mse_loss(q_values_for_actions, target)

        # 4) Backprop
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Write loss to a file
        with open(self.log_file, "a") as f:
            f.write(f"{self.episode_count},{self.batch_count},{loss.item()}\n")

        self.soft_update_target(tau=0.005)


    #HARD UPDATE
    def update_target_model(self):
        """
        Periodically update target network, for example at the end of each game.
        """
        self.target_model.load_state_dict(self.model.state_dict())
        print("✅ Target model updated.")

    #SOFT UPDATE
    def soft_update_target(self, tau=0.005):
        """Soft update target network parameters.

        Args:
            tau (float): interpolation parameter, with 0 < tau < 1.
        """
        for target_param, local_param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(tau * local_param.data + (1 - tau) * target_param.data)


    def load_model(self):
        """
        Load model weights, optimizer state, epsilon, and replay buffer
        so training can continue seamlessly next game.
        """
        if not os.path.exists(self.model_filename):
            print("⚠️ No saved model found. Starting with fresh model and empty replay buffer.")
            return

        try:
            checkpoint = torch.load(self.model_filename, map_location=device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']


            # Rebuild replay buffer from saved transitions
            saved_memory = checkpoint.get('memory', [])
            self.memory.memory = deque(saved_memory, maxlen=self.memory.memory.maxlen)

            print(f"✅ Model {self.model_filename} loaded successfully.")
            print(f"Replay buffer size after load: {len(self.memory)}")
            print("Epsilon: ", self.epsilon)


        except Exception as e:
            print(f"⚠️ Could not load {self.model_filename}: {e}")
            raise

    def save_model(self):
        """
        Save model weights, optimizer state, epsilon, and replay buffer
        so training can continue seamlessly next game.
        """

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'memory': list(self.memory.memory)
        }

        print("While saving epsilon: ", self.epsilon)

        # Create a temporary filename
        temp_filename = self.model_filename + ".tmp"

        # Write the checkpoint to the temp file
        with open(temp_filename, 'wb') as f:
            torch.save(checkpoint, f)
            f.flush()               # Flush Python-level buffers
            os.fsync(f.fileno())    # Force the OS to flush to disk

        # Atomically replace the old file with the new one
        os.replace(temp_filename, self.model_filename)

        print(f"✅ Model saved as {self.model_filename}. Replay buffer size: {len(self.memory)}")

        with open("scores.txt", "a") as file:
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
        Called once at end of game to store a terminal transition in replay buffer
        with big final reward that includes route points, completed tickets,
        penalty for uncompleted tickets, etc.
        """
        last_state = self.get_state()
        done = True
        print("Final Reward Applied ", done)

        action_idx = self.action_space.index("end_of_game")

        self.memory.push(last_state, action_idx, final_reward, last_state, True)
        self.replay()

        self.total_episode_reward += final_reward

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            print("Epsilon decayed to:", self.epsilon)

        self.episode_count += 1

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
        if not self.routes_needed_to_claim:
            print("routes_needed_to_claim is empty!")
            return needed_colors

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

        for color in ["red", "blue", "green", "yellow", "orange", "pink", "black", "white"]:
            needed_colors[color] = max(0, needed_colors[color] - inventory[color] - inventory["joker"])

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