import os
from collections import deque
import torch
import torch.nn.functional as F
import torch.optim as optim
from Model.DQNModel.dqn import DQN
from Model.DQNModel.replay_memory import ReplayMemory
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #GPU


class DQNAgent:
    def __init__(self, color, game_service, gamma=0.99, epsilon=1.0, epsilon_min=0.05, epsilon_decay=0.999, lr=0.001,
                 memory_size=50000, batch_size=64):
        self.color = color
        self.game_service = game_service

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.model_filename = f"dqn_model_1_0.pth"  # Model file for saving/loading

        # Define fixed state size and action space
        self.state_size = 24  # Fixed number of state features
        self.action_space = ["claim_route_1", "claim_route_2", "claim_route_3", "claim_route_4", "claim_route_5",
                             "claim_route_6", "draw_blind", "draw_red_card", "draw_blue_card", "draw_yellow_card",
                             "draw_green_card", "draw_pink_card", "draw_orange_card", "draw_white_card",
                             "draw_black_card", "draw_joker_card", "draw_destination_ticket", "end_of_game"]  # Fixed action space

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

        self.first_turn = True

        self.total_episode_reward = 0

        print("Model is on device:", next(self.model.parameters()).device)

        print("PyTorch version:", torch.__version__)
        print("CUDA available:", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("Number of GPUs:", torch.cuda.device_count())
            print("Current device index:", torch.cuda.current_device())
            print("Device name:", torch.cuda.get_device_name(0))


    def get_state(self):
        """
        An expanded state representation for Ticket to Ride.
        Feel free to adjust the features based on your training experiments.
        """
        # Pull high-level game state
        game_state = self.game_service.get_game_state()
        # Pull info specific to the current player
        current_player_state = self.game_service.get_current_player_state()


        # 1. My current score
        my_score = current_player_state["current score"]

        # 2. My remaining train cars
        my_remaining_cars = current_player_state["remaining cars"]

        # 3. Number of routes I’ve claimed so far
        my_claimed_routes_count = len(current_player_state["claimed routes"])

        # 4. How many of each color train card do I have?
        #    We'll build a small dictionary or use a function to count them.
        train_cards_list = current_player_state["train_cards"]
        train_card_color_counts = self._count_train_cards_by_color(train_cards_list)
        # Choose which colors you care about—this example has 9 "colors," including joker.
        red_count    = train_card_color_counts.get("red", 0)
        blue_count   = train_card_color_counts.get("blue", 0)
        green_count  = train_card_color_counts.get("green", 0)
        yellow_count = train_card_color_counts.get("yellow", 0)
        black_count  = train_card_color_counts.get("black", 0)
        white_count  = train_card_color_counts.get("white", 0)
        pink_count   = train_card_color_counts.get("pink", 0)
        orange_count = train_card_color_counts.get("orange", 0)
        joker_count  = train_card_color_counts.get("joker", 0)

        # 5. How many destination tickets do I have in hand?
        my_destination_cards_count = len(current_player_state["destination_cards"])

        # 6. How many routes can I currently claim?
        current_claimable_routes_count = len(current_player_state["claimable_routes"])

        # 7. Is the game in the "last turn" phase?
        is_last_turn = 1 if game_state["is_the_next_turn_last_turn"] else 0

        # --- Face-up cards on the table ---
        table_cards = game_state["train_cards_on_the_table"]
        table_color_counts = self._count_train_cards_by_color(table_cards)

        table_red = table_color_counts.get("red", 0)
        table_blue = table_color_counts.get("blue", 0)
        table_green = table_color_counts.get("green", 0)
        table_yellow = table_color_counts.get("yellow", 0)
        table_black = table_color_counts.get("black", 0)
        table_white = table_color_counts.get("white", 0)
        table_pink = table_color_counts.get("pink", 0)
        table_orange = table_color_counts.get("orange", 0)
        table_joker = table_color_counts.get("joker", 0)

        # Assemble final feature vector
        state_vector = [
            my_score,
            my_remaining_cars,
            my_claimed_routes_count,
            red_count,
            blue_count,
            green_count,
            yellow_count,
            black_count,
            white_count,
            pink_count,
            orange_count,
            joker_count,
            my_destination_cards_count,
            current_claimable_routes_count,
            is_last_turn,

            # Face-up cards on the table
            table_red,
            table_blue,
            table_green,
            table_yellow,
            table_black,
            table_white,
            table_pink,
            table_orange,
            table_joker
        ]

        return torch.tensor(state_vector, dtype=torch.float32).unsqueeze(0)

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
                "selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.get_available_actions_for_dqn()
        if not available_actions:
            self.game_service.pass_the_turn()
            return
        
        print("AVAILABLE ACTIONS:", available_actions)

        action = self.choose_action()
        state = self.get_state()
        reward, next_state, done = self.execute_action(action)

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
        if action == "claim_route_1":
            reward = self.claim_route(1)
        elif action == "claim_route_2":
            reward = self.claim_route(2)
        elif action == "claim_route_3":
            reward = self.claim_route(3)
        elif action == "claim_route_4":
            reward = self.claim_route(4)
        elif action == "claim_route_5":
            reward = self.claim_route(5)
        elif action == "claim_route_6":
            reward = self.claim_route(6)
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
        elif action == "draw_destination_ticket":
            reward = self.draw_destination_ticket()
        else:
            reward = 0

        next_state = self.get_state()
        done = self.game_service.get_game_state()["game_ended"]

        self.total_episode_reward += reward

        return reward, next_state, done

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

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

        # ***GATHER only the Q-values corresponding to the chosen actions***
        # actions.unsqueeze(1) has shape [batch_size, 1], so gather returns shape [batch_size, 1]
        q_values_for_actions = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        # Now q_values_for_actions has shape [batch_size]

        # 2) Target Q-values
        with torch.no_grad():
            target_q_values = self.target_model(next_states)
            max_next_q = target_q_values.max(dim=1)[0]
            target = rewards + (1 - dones) * self.gamma * max_next_q


        # 3) Loss only for the chosen actions
        loss = F.mse_loss(q_values_for_actions, target)

        # 4) Backprop
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 5) Epsilon decay
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        print("States device:", states.device)
        print("Next states device:", next_states.device)
        print("Actions device:", actions.device)

    def update_target_model(self):
        """
        Periodically update target network, for example at the end of each game.
        """
        self.target_model.load_state_dict(self.model.state_dict())
        print("✅ Target model updated.")

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
            # Convert replay buffer (deque) to a list so it’s easily serializable
            'memory': list(self.memory.memory)
        }
        torch.save(checkpoint, self.model_filename)
        print(f"✅ Model saved as {self.model_filename}. Replay buffer size: {len(self.memory)}")

        with open("scores.txt", "a") as file:
            file.write(str(self.total_episode_reward) + ",")


    def get_available_actions_for_dqn(self):
        available_actions = self.game_service.get_available_actions(self.color)
        current_player_state = self.game_service.get_current_player_state()
        game_state = self.game_service.get_game_state()
        available_actions_in_detail = []

        if "claim_route" in available_actions:
            for route in current_player_state["claimable_routes"]:
                if route.length == 6:
                    available_actions_in_detail.append("claim_route_6")
                elif route.length == 5:
                    available_actions_in_detail.append("claim_route_5")
                elif route.length == 4:
                    available_actions_in_detail.append("claim_route_4")
                elif route.length == 3:
                    available_actions_in_detail.append("claim_route_3")
                elif route.length == 2:
                    available_actions_in_detail.append("claim_route_2")
                elif route.length == 1:
                    available_actions_in_detail.append("claim_route_1")

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

        if "draw_destination_ticket" in available_actions:
            available_actions_in_detail.append("draw_destination_ticket")

        #console print("AVAILABLE ACTIONS CALLED: ", list(set(available_actions_in_detail)))
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


    """ACTIONS PART"""

    def claim_route(self, length):
        """
        Selects and claims a route.
        """
        current_state = self.game_service.get_current_player_state()
        claimable_routes = [route for route in current_state["claimable_routes"] if route.length == length]

        train_cards_list = current_state["train_cards"]
        self.game_service.log(f"Having these train cards: {train_cards_list}")

        selected_route = random.choice(claimable_routes)
        action_params = {"selected_route": selected_route, "use_this_color": None}

        if selected_route.color == "gray":
            available_colors = self.game_service.perform_action("claim_route", action_params)
            action_params["use_this_color"] = random.choice(available_colors)

        self.game_service.perform_action("claim_route", action_params)

        self.game_service.log(
            f"{self.color}, Action: CLAIM COLORED ROUTE, {selected_route.city1} to {selected_route.city2}")

        return length * 2

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

        return 2  # Reward for drawing blind train cards

    def draw_colored(self, color):
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

        return 3

    def draw_joker(self):
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]
        for card in train_cards_on_the_table:
            if card.color == "joker":
                action_params = {"selected_card": card}
                self.game_service.perform_action("draw_train_card", action_params)
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {card.color}")
                break

        return 5

    def draw_destination_ticket(self):
        """
        Draws destination tickets.
        """
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)
        destination_card_list_without_none = []
        for card in draw_destination_card_list:
            if card is not None:
                destination_card_list_without_none.append(card)

        number_of_cards_to_select = random.randint(1, len(destination_card_list_without_none))
        selected_cards = random.sample(destination_card_list_without_none, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)

        log_message = f"{self.color}, Action: DESTINATION TICKET,"
        for ticket in action_params['selected_destination_tickets']:
            log_message += f" {ticket.city1} to {ticket.city2},"
        log_message = log_message.rstrip(',')
        self.game_service.log(log_message)

        return -15  # Reward for drawing destination tickets
