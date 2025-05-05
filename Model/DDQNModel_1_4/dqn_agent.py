import os
from collections import deque
import torch
import torch.nn.functional as F
import torch.optim as optim

import global_vars
from Model.DDQNModel_1_4.dqn import DQN
from Model.DDQNModel_1_4.replay_memory import PrioritizedReplayMemory
import random
import heapq
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #GPU

class DDQNAgent:
    def __init__(self, color, game_service, persistent_model=None, gamma=0.99, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.995, lr=0.001,
                 memory_size=50000, batch_size=128, train_mode=True):
        torch.manual_seed(global_vars.random_seed())
        random.seed(global_vars.random_seed())

        self.train_mode = train_mode
        self.color = color
        self.game_service = game_service
        self.persistent_model = persistent_model

        self.gamma = gamma
        self.epsilon = epsilon if train_mode else 0.0
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size

        # Define fixed state size and action space
        self.state_size = 11  # Fixed number of state features
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
        self.memory = PrioritizedReplayMemory(memory_size)

        self.not_use_persistent_model = True
        if self.not_use_persistent_model:
            self.filename = "ddqn_model_final_2.pth"
            self.checkpoint_data = None

        # Try loading an existing model if available
        self.load_model()

        #Agent specific
        self.first_turn = True
        self.routes_needed_to_claim = []

        self.total_episode_reward = 0

        #print loss
        self.log_file = "ddqn_training_loss.txt"

        # Only create/write header if file doesn't exist yet
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("episode,batch,loss\n")  # single header line, do this once

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

    def get_action_mask(self):
        # Get available actions from the game service (e.g., "claim_route", "draw_red_card", etc.)
        available_actions = self.get_available_actions_for_dqn()
        # Convert valid actions to indices in the fixed action space
        valid_indices = [self.action_space.index(action) for action in available_actions]
        # Create a mask of length equal to total actions: valid actions get 0, invalid get a very low value.
        mask = torch.full((len(self.action_space),), -1e9, device=device)
        for idx in valid_indices:
            mask[idx] = 0.0
        # Reshape mask to match Q-value output (batch_size, num_actions)
        return mask.unsqueeze(0)

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
        elif 2 < min_cars <= 6:
            car_state = 0.8
        elif min_cars <=2:
            car_state = 1

        if self.routes_needed_to_claim:
            destinations_completed = 0
        else:
            destinations_completed = 1

        state_vector = [
            car_state * 6,
            destinations_completed * 2,
            max_length_of_claimable_routes/6 * 4,
            needed_red/6,
            needed_blue/6,
            needed_green/6,
            needed_yellow/6,
            needed_orange/6,
            needed_pink/6,
            needed_white/6,
            needed_black/6,
        ]

        print("STATE VECTOR: ", state_vector)
        state_tensor = torch.tensor(state_vector, dtype=torch.float32, device=device).unsqueeze(0)
        # Get the action mask for the current state
        action_mask = self.get_action_mask()
        return state_tensor, action_mask


    def choose_action(self):
        """
        Selects an action using an epsilon-greedy policy, ensuring only valid actions are chosen.
        """
        available_actions = self.get_available_actions_for_dqn()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)  # Random exploration
        else:
            # Get both state tensor and action mask
            state, action_mask = self.get_state()
            with torch.no_grad():
                q_values = self.model(state)  # shape: [1, num_actions]
            # Add the mask so that invalid actions have very low Q-values
            masked_q_values = q_values + action_mask
            best_action_index = masked_q_values.argmax(dim=1).item()

            print(f"Selected action: index: {best_action_index}, action: {self.action_space[best_action_index]}, q value: {masked_q_values[0, best_action_index].item()}")

            avg_q_value = q_values.mean().item()
            with open("ddqn_q_values.txt", "a") as f:
                f.write(f"{avg_q_value}\n")

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
            self.game_service.change_status_text(f"{self.color} drawed destination tickets.")
            return

        available_actions = self.get_available_actions_for_dqn()
        if not available_actions:
            self.game_service.pass_the_turn()
            return

        action = self.choose_action()
        state, state_mask = self.get_state()
        reward, next_state, done = self.execute_action(action)
        next_state, next_state_mask = self.get_state()

        print("################## ⚔ PLAYER INFO ######################")
        print("#  AVAILABLE ACTIONS:", available_actions)
        print("#  SELECTED ACTION: ", action)
        print("#  THE REWARD: ", reward)
        print("########################################################")

        if self.train_mode:
            # Store experience in replay memory
            # NEW - store action as an integer index
            action_idx = self.action_space.index(action)
            self.memory.push(state.cpu(), action_idx, reward, next_state.cpu(), done, state_mask.cpu(), next_state_mask.cpu())

            # Train the model
            self.replay()

        with open("ddqn_actions_log.txt", "a") as f:
            f.write(f"{action}\n")
        print("\n\n")

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

        print("-> NEXT STATE ")
        next_state = self.get_state()
        done = False

        self.total_episode_reward += reward

        return reward, next_state, done

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        self.batch_count += 1

        # Now each transition contains 7 items: state, action, reward, next_state, done, state_mask, next_state_mask
        batch, indices, is_weights = self.memory.sample(self.batch_size)
        is_weights = torch.tensor(is_weights, dtype=torch.float32, device=device)

        is_weights /= is_weights.max() #new added normalization of weight to prevent loss explode

        states, actions, rewards, next_states, dones, state_masks, next_state_masks = zip(*batch)

        states = torch.cat(states).to(device)
        next_states = torch.cat(next_states).to(device)
        actions = torch.tensor(actions, dtype=torch.long, device=device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=device)
        dones = torch.tensor(dones, dtype=torch.float32, device=device)
        next_state_masks = torch.cat(next_state_masks).to(device)  # [batch_size, num_actions]

        q_values = self.model(states)
        q_values_for_actions = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_q_values_online = self.model(next_states)
            # Apply the stored mask for each next state to ensure only valid actions are considered
            masked_next_q_values_online = next_q_values_online + next_state_masks
            next_actions = masked_next_q_values_online.argmax(dim=1, keepdim=True)
            next_q_values_target = self.target_model(next_states).gather(1, next_actions).squeeze(1)
            target = rewards + (1 - dones) * self.gamma * next_q_values_target

        td_errors = torch.abs(q_values_for_actions - target).detach().cpu().numpy()
        clipped_td_errors = np.minimum(td_errors, 1.0)
        self.memory.update_priorities(indices, clipped_td_errors + 1e-5)

        loss = (is_weights * F.mse_loss(q_values_for_actions, target, reduction='none')).mean()

        self.optimizer.zero_grad()
        loss.backward()
        #torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0) #for preventing exploding gradients
        self.optimizer.step()

        self.soft_update_target(tau=0.005)

        with open(self.log_file, "a") as f:
            f.write(f"{self.episode_count},{self.batch_count},{loss.item()}\n")

        mean_td_error = td_errors.mean()
        with open("ddqn_td_errors.txt", "a") as f:
            f.write(f"{self.batch_count},{mean_td_error}\n")

    #HARD UPDATE
    def update_target_model(self):
        """
        Periodically update target network, for example at the end of each game.
        """
        self.target_model.load_state_dict(self.model.state_dict())
        print("✅ Target model updated.")

    #SOFT UPDATE
    def soft_update_target(self, tau=0.01):
        """Soft update target network parameters.

        Args:
            tau (float): interpolation parameter, with 0 < tau < 1.
        """
        for target_param, local_param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(tau * local_param.data + (1 - tau) * target_param.data)

    def load_model(self):
        """
        Loads model weights, optimizer, epsilon, replay memory, etc.
        from the in-memory persistent_model instead of from disk.
        """

        # Retrieve checkpoint data from memory
        if self.not_use_persistent_model:
            self.load_model_()
            checkpoint = self.checkpoint_data
        else:
            if self.persistent_model is None:
                print("No persistent model manager available; starting fresh.")
                return

            checkpoint = self.persistent_model.load_data()

        if not checkpoint:
            # Means the persistent_model might be empty
            print("No data in persistent_model; starting fresh.")
            return

        try:
            # Load the model/optimizer states, epsilon, memory, etc.
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.epsilon = checkpoint['epsilon']

            # Replay memory
            self.memory.memory = checkpoint.get('memory', [])
            saved_priorities = checkpoint.get('priorities', None)
            if saved_priorities is not None:
                self.memory.priorities = saved_priorities
            self.memory.pos = checkpoint.get('pos', 0)

            print("✅ Model loaded successfully from persistent_model.")
            print(f"Replay buffer size after load: {len(self.memory)}")
            print("Epsilon:", self.epsilon)
        except Exception as e:
            print(f"⚠️ Could not load from persistent_model: {e}")
            raise

    def save_model(self):
        """
        Saves model weights, optimizer, epsilon, replay memory, etc.
        into the in-memory persistent_model instead of to disk.
        """
        if self.persistent_model is None:
            print("No persistent model manager available; not saving.")
            return

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'memory': self.memory.memory,
            'priorities': self.memory.priorities,
            'pos': self.memory.pos
        }

        try:
            if self.not_use_persistent_model:
                self.checkpoint_data = checkpoint
                self.save_model_()
            else:
                self.persistent_model.store_data(checkpoint)
            print("✅ Model data saved to persistent_model in memory.")
            print("Replay buffer size:", len(self.memory))
            with open("ddqn_scores.txt", "a") as file:
                file.write(str(self.total_episode_reward) + ",")
        except Exception as e:
            print(f"⚠️ Could not save to persistent_model: {e}")

    #FOR NO PERSISTENT MODEL SAVING SYSTEM
    def save_model_(self):
        """
        Saves the current checkpoint data to the file on disk (self.filename).
        If checkpoint_data is None, it does not save and just prints a message.
        """
        if self.checkpoint_data is None:
            print("Checkpoint data is None. Skipping file save.")
            return

        if os.path.exists(self.filename):
            print(f"File '{self.filename}' already exists; overwriting with the current checkpoint data.")
        else:
            print(f"No file found at '{self.filename}'. Creating a new file with checkpoint data.")

        temp_filename = self.filename + ".tmp"
        try:
            with open(temp_filename, 'wb') as f:
                torch.save(self.checkpoint_data, f)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_filename, self.filename)
            print(f"Model saved successfully to {self.filename}.")
        except Exception as e:
            print(f"Error saving model to {self.filename}: {e}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def load_model_(self):
        """
        Loads the checkpoint data from the file on disk (self.filename) into memory.
        If the file doesn't exist, starts fresh (checkpoint_data = None).
        """
        if not os.path.exists(self.filename):
            print(f"No checkpoint file found at {self.filename}. Starting fresh.")
            self.checkpoint_data = None
            return

        try:
            print(f"Loading model from file: {self.filename}")
            checkpoint = torch.load(self.filename, map_location=torch.device("cpu"), weights_only=False)
            self.checkpoint_data = checkpoint
            print("Model loaded successfully into PersistentModelManager.")
        except Exception as e:
            print(f"Could not load {self.filename}: {e}")
            self.checkpoint_data = None
            raise

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
        if not self.train_mode:
            return

        last_state, last_state_mask = self.get_state()
        done = True
        print("Final Reward Applied ", done)

        action_idx = self.action_space.index("end_of_game")

        # Use the same last_state and mask for the terminal next state.
        self.memory.push(last_state.cpu(), action_idx, final_reward, last_state.cpu(), True, last_state_mask.cpu(), last_state_mask.cpu())
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

        self.game_service.change_status_text(f"{self.color} drawed train card from blind deck.")

        return -1  # Reward for drawing blind train cards

    def draw_colored(self, color):
        needed_colors = self.needed_colors()
        needed_color_count = needed_colors[color]

        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]
        choosen_cards_list_for_status_change = []

        for card in train_cards_on_the_table:
            if card.color == color:
                action_params = {"selected_card": card}
                self.game_service.perform_action("draw_train_card", action_params)
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {card.color}")
                choosen_cards_list_for_status_change.append(card.color)
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
                    choosen_cards_list_for_status_change.append(card.color)
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
                    choosen_cards_list_for_status_change.append(card.color)
                    pass_bool = False
                    break

        if pass_bool:
            self.game_service.pass_draw_second_train_card()
            print("PASSED SECOND TRAIN CARD")

        self.game_service.change_status_text(f"{self.color} drawed {choosen_cards_list_for_status_change} train cards from table.")

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

        self.game_service.change_status_text(f"{self.color} drawed joker train card from table.")

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
                self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {route.city1} to {route.city2}")
                self.game_service.change_status_text(f"{self.color} claim colored route: {route.city1} to {route.city2}")
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

                self.game_service.log(f"{self.color}, Action: CLAIM GRAY ROUTE, {random_route.city1} to {random_route.city2}, {use_random_color}")
                self.game_service.change_status_text(f"{self.color} claim gray route: {random_route.city1} to {random_route.city2}")


            else:
                #console print("AI: A COLORED ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                self.game_service.perform_action("claim_route", action_params)

                self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {random_route.city1} to {random_route.city2}")
                self.game_service.change_status_text(f"{self.color} claim colored route: {random_route.city1} to {random_route.city2}")


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