import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random


class PPOAgent:
    def __init__(self, color, game_service, input_dim=20, action_dim=3, hidden_dim=128, lr=0.001):
        self.color = color
        self.game_service = game_service
        self.input_dim = input_dim  # Adjust this according to state representation
        self.action_dim = action_dim  # Adjust based on possible actions
        self.hidden_dim = hidden_dim

        # PPO Hyperparameters
        self.gamma = 0.99
        self.epsilon = 0.2  # PPO clip parameter
        self.lr = lr
        self.batch_size = 32
        self.update_steps = 5

        # Define policy and value networks
        self.policy_net = self.build_model()
        self.value_net = self.build_model(output_dim=1)
        self.optimizer_policy = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.optimizer_value = optim.Adam(self.value_net.parameters(), lr=self.lr)

        # Experience buffers
        self.memory = []

    def build_model(self, output_dim=None):
        """Creates a simple neural network for policy/value function"""
        if output_dim is None:
            output_dim = self.action_dim  # Default to policy output

        return nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, output_dim),
            nn.Softmax(dim=-1) if output_dim == self.action_dim else nn.Identity()
        )

    def get_state_representation(self):
        """Extract relevant state information from the game"""
        game_state = self.game_service.get_game_state()
        player_state = self.game_service.get_current_player_state()

        # Convert game state into a numerical array
        state_vector = np.zeros(self.input_dim)

        # Example: Encode the number of train cars, destination tickets, and claimed routes
        state_vector[0] = player_state["remaining_train_cars"]
        state_vector[1] = len(player_state["train_cards"])
        state_vector[2] = len(player_state["destination_cards"])
        state_vector[3] = len(game_state["claimed_routes"])

        return state_vector

    def select_action(self, state):
        """Selects an action using the policy network"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs = self.policy_net(state_tensor)
        action = torch.multinomial(action_probs, 1).item()
        return action

    def perform_action(self):
        """Perform an action based on policy"""
        if self.game_service.get_game_state()["game_ended"]:
            return

        print(f"------------{self.color} COLORED PPO AGENT PERFORMING ACTION---------------")

        state = self.get_state_representation()
        action_index = self.select_action(state)

        available_actions = self.game_service.get_available_actions(self.color)
        if not available_actions:
            self.game_service.pass_the_turn()
            return

        action = available_actions[action_index % len(available_actions)]  # Ensure valid action index

        print(f"AI: {self.color} COLORED AGENT SELECTED THIS ACTION: {action}")

        # Perform the chosen action
        if action == 'draw_train_card':
            self.draw_train_card()
        elif action == 'draw_destination_ticket':
            self.draw_destination_ticket()
        elif action == 'claim_route':
            self.claim_route()

    def draw_train_card(self):
        """PPO Agent draws a train card"""
        action_params = {"selected_card": "select_blind"}
        self.game_service.perform_action("draw_train_card", action_params)

    def draw_destination_ticket(self):
        """PPO Agent draws destination tickets"""
        destination_cards = self.game_service.perform_action("draw_destination_ticket", None)
        selected_cards = random.sample(destination_cards, min(len(destination_cards), 2))
        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)

    def claim_route(self):
        """PPO Agent claims a route"""
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]
        if claimable_routes:
            random_route = random.choice(claimable_routes)
            action_params = {"selected_route": random_route, "use_this_color": None}
            self.game_service.perform_action("claim_route", action_params)

    def store_experience(self, state, action, reward, next_state, done):
        """Stores experiences for training"""
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > self.batch_size:
            self.train()

    def train(self):
        """Train the agent using PPO"""
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones).unsqueeze(1)

        # Compute value targets
        value_targets = rewards + self.gamma * self.value_net(next_states).detach() * (1 - dones)

        # Compute advantages
        values = self.value_net(states)
        advantages = value_targets - values

        # Compute policy loss
        action_probs = self.policy_net(states).gather(1, actions)
        ratios = action_probs / (action_probs.detach() + 1e-8)
        clipped_ratios = torch.clamp(ratios, 1 - self.epsilon, 1 + self.epsilon)
        policy_loss = -torch.min(ratios * advantages, clipped_ratios * advantages).mean()

        # Compute value loss
        value_loss = nn.MSELoss()(values, value_targets.detach())

        # Update policy network
        self.optimizer_policy.zero_grad()
        policy_loss.backward()
        self.optimizer_policy.step()

        # Update value network
        self.optimizer_value.zero_grad()
        value_loss.backward()
        self.optimizer_value.step()

        # Clear memory
        self.memory = []
