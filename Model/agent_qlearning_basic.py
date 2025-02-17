import random
import numpy as np
import pickle


class QLearningAgent:
    def __init__(self, color, game_service, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.color = color
        self.game_service = game_service
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate

        self.q_table = {}  # Q-table stored as a dictionary {(state, action): Q-value}
        self.previous_state = None
        self.previous_action = None

        self.first_turn = True

    def get_state(self):
        """
        Convert the agent's own game state into a tuple (hashable format) to use in the Q-table.
        The state should only include information visible to the agent.
        """
        current_player_state = self.game_service.get_current_player_state()

        # Extract relevant information that the agent has access to
        state = (
            tuple(sorted([route.id for route in current_player_state["claimable_routes"]])),  # Claimable routes
            tuple(sorted([card.color for card in current_player_state["train_cards"]])),  # Agent's train cards
            tuple(sorted([ticket.id for ticket in current_player_state["destination_cards"]])),  # Destination tickets
        )

        return state

    def choose_action(self, available_actions):
        """
        Choose an action using epsilon-greedy strategy.
        """
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions)  # Explore
        else:
            return self.get_best_action(available_actions)  # Exploit

    def get_best_action(self, available_actions):
        """
        Select the best action based on current Q-values.
        """
        state = self.get_state()
        q_values = {action: self.q_table.get((state, action), 0) for action in available_actions}

        # Pick the action with the highest Q-value
        best_action = max(q_values, key=q_values.get)
        return best_action

    def update_q_value(self, reward):
        """
        Update Q-table based on the reward received.
        """
        if self.previous_state is not None and self.previous_action is not None:
            current_state = self.get_state()
            max_future_q = max([self.q_table.get((current_state, a), 0) for a in
                                ["claim_route", "draw_train_card", "draw_destination_ticket"]], default=0)

            old_q = self.q_table.get((self.previous_state, self.previous_action), 0)
            new_q = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)

            self.q_table[(self.previous_state, self.previous_action)] = new_q

    def perform_action(self):
        """
        Execute an action and update the Q-table.
        """
        if self.first_turn:
            self.load_q_table()
            print(f"It is the first turn of {self.color}ed QLearningAgent")
            self.first_turn = False
            action_params = {
                "selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.game_service.get_available_actions(self.color)
        if not available_actions:
            self.game_service.pass_the_turn()
            return

        chosen_action = self.choose_action(available_actions)

        # Store the previous state-action pair
        self.previous_state = self.get_state()
        self.previous_action = chosen_action

        # Perform the action and get a reward
        if chosen_action == "claim_route":
            reward = self.claim_route()
        elif chosen_action == "draw_train_card":
            reward = self.draw_train_card()
        elif chosen_action == "draw_destination_ticket":
            reward = self.draw_destination_ticket()
        else:
            reward = 0  # If no action was performed

        # Update Q-values
        self.update_q_value(reward)

    def claim_route(self):
        """
        Selects and claims a route.
        """
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]

        train_cards_list = current_state["train_cards"]
        self.game_service.log(
            f"Having these train cards: {train_cards_list}")

        if claimable_routes:
            selected_route = random.choice(claimable_routes)
            action_params = {"selected_route": selected_route, "use_this_color": None}

            if selected_route.color == "gray":
                available_colors = self.game_service.perform_action("claim_route", action_params)
                action_params["use_this_color"] = random.choice(available_colors)

            self.game_service.perform_action("claim_route", action_params)

            self.game_service.log(
                f"{self.color}, Action: CLAIM COLORED ROUTE, {selected_route.city1} to {selected_route.city2}")
            return 10  # Reward for claiming a route
        return -5  # Negative reward for failure

    def draw_train_card(self):
        """
        Draws a train card.
        """
        action_params = {"selected_card": "select_blind"}
        returned_item = self.game_service.perform_action("draw_train_card", action_params)
        self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD")

        current_state = self.game_service.get_current_player_state()
        train_cards_list = current_state["train_cards"]
        self.game_service.log(
            f"Having these train cards: {train_cards_list}")

        return 2  # Reward for drawing a train card

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

        return 2  # Reward for drawing destination tickets

    def save_q_table(self, filename="q_table_basic.pkl"):
        """
        Save the Q-table to a file.
        """
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)
            print("Q-Table is saved.")

    def load_q_table(self, filename="q_table_basic.pkl"):
        """
        Load the Q-table from a file.
        """
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
                print("Q-Table is loaded.")
        except FileNotFoundError:
            print("No saved Q-table found. Starting fresh.")
