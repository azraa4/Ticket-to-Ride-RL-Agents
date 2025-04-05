import os
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# Use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#########################################
# PPO Actor-Critic Network & Rollout Buffer
#########################################
class PPOActorCritic(nn.Module):
    def __init__(self, input_size, output_size):
        super(PPOActorCritic, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.action_head = nn.Linear(128, output_size)
        self.value_head = nn.Linear(128, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        action_logits = self.action_head(x)
        state_value = self.value_head(x)
        return action_logits, state_value

class RolloutBuffer:
    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.is_terminals = []
        self.state_values = []

    def clear(self):
        self.states.clear()
        self.actions.clear()
        self.log_probs.clear()
        self.rewards.clear()
        self.is_terminals.clear()
        self.state_values.clear()

#########################################
# Line Game Service (with fixed turns & Reset)
#########################################
class LineGameService:
    """
    In this game, an agent starts at position 0 and must reach position 20.
    Valid actions (as performed by the environment):
      - "move_right": Move 1 step to the right.
      - "move_left": Move 1 step to the left.
      - "jump_right": Move 2 steps right. If overshooting the goal, incur a penalty.
      - "jump_left": Move 2 steps left. If not possible (at position <2), incur a penalty.
      - "stay": Do nothing.
    Each episode lasts a fixed number of turns.
    """
    def __init__(self, goal=20):
        self.goal = goal
        self.reset()

    def reset(self):
        self.position = 0

    def update_player_state(self):
        return {"points": self.position, "remaining_train_cars": self.goal - self.position}

    def get_game_state(self):
        player_state = self.update_player_state()
        return {
            "players": [player_state],
            "position": self.position
        }

    def get_current_player_state(self):
        # Provide a dummy claimable_routes if not at goal.
        claimable = [{"dummy": True}] if self.position < self.goal else []
        return {
            "current score": self.position,
            "remaining_train_cars": self.goal - self.position,
            "claimable_routes": claimable,
            "train_cards": [],
            "destination_cards": []
        }

    def get_available_actions(self, color):
        # Although the agent has five movement actions, the environment always permits all moves.
        return ["move_right", "move_left", "jump_right", "jump_left", "stay"]

    def perform_action(self, action, action_params):
        # Execute the requested move.
        if action == "move_right":
            # Standard move right.
            if self.position < self.goal:
                self.position += 1
                print(f"[LineGame] Moved right to position {self.position}")
                reward = 1
                if self.position == self.goal:
                    reward += 10  # bonus for reaching the goal
                return reward
            else:
                return 0
        elif action == "move_left":
            if self.position > 0:
                self.position -= 1
                print(f"[LineGame] Moved left to position {self.position}")
                return -1
            else:
                print("[LineGame] Already at position 0, cannot move left.")
                return -1
        elif action == "jump_right":
            # Jump two steps to the right if possible.
            if self.position <= self.goal - 2:
                self.position += 2
                print(f"[LineGame] Jumped right to position {self.position}")
                return 2  # higher reward for a jump
            else:
                # If overshooting, apply penalty.
                print(f"[LineGame] Jump right overshot the goal. Penalty applied.")
                return -3
        elif action == "jump_left":
            if self.position >= 2:
                self.position -= 2
                print(f"[LineGame] Jumped left to position {self.position}")
                return -2
            else:
                print("[LineGame] Not enough room to jump left. Penalty applied.")
                return -2
        elif action == "stay":
            print(f"[LineGame] Stayed at position {self.position}")
            return 0
        else:
            return 0

    def pass_the_turn(self):
        pass

    def get_destination_tickets_list_at_the_start_of_the_game(self):
        return []

    def get_availability_of_blind_pick(self):
        return True

    def change_status_text(self, text):
        print("[Status]", text)

    def log(self, text):
        print("[Log]", text)

    def pass_draw_second_train_card(self):
        pass

    def compute_shortest_path_between_cities(self, city1, city2, unclaimed_routes, claimed_routes):
        return []

#########################################
# LineGamePPOAgent (Using PPO Logic for Line Game with More Actions)
#########################################
class LineGamePPOAgent:
    def __init__(self, color, game_service, lr=0.001, batch_size=64, update_timestep=5, clip_param=0.2, K_epochs=4, gamma=0.99):
        self.color = color
        self.game_service = game_service
        self.gamma = gamma
        self.batch_size = batch_size
        self.update_timestep = update_timestep  # number of moves before an update
        self.clip_param = clip_param
        self.K_epochs = K_epochs

        self.state_size = 11  # as expected by the network

        # New action space with five movement choices plus terminal action.
        self.action_space = ["move_right", "move_left", "jump_right", "jump_left", "stay", "end_of_game"]

        self.model = PPOActorCritic(self.state_size, len(self.action_space)).to(device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)

        self.filename = "linegame_ppoagent.pth"
        self.load_model()

        self.buffer = RolloutBuffer()
        self.timestep = 0

        self.first_turn = True
        self.total_episode_reward = 0

        self.log_file = "linegame_ppo_training_loss.txt"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("episode,timestep,loss\n")
        self.episode_count = 0
        self.timestep_count = 0

        # For plotting
        self.last_loss = 0.0

    def get_action_mask(self):
        # Only allow the five movement actions during play (exclude "end_of_game").
        valid_actions = ["move_right", "move_left", "jump_right", "jump_left", "stay"]
        valid_indices = [self.action_space.index(a) for a in valid_actions]
        mask = torch.full((len(self.action_space),), -1e9, device=device)
        for idx in valid_indices:
            mask[idx] = 0.0
        return mask.unsqueeze(0)

    def get_state(self):
        # State is an 11-dimensional vector: first element is normalized position, rest are fixed constants.
        position = self.game_service.get_game_state()["players"][0]["points"]
        norm_pos = position / self.game_service.goal
        state_vector = [norm_pos] + [0.5] * 10
        state_tensor = torch.tensor(state_vector, dtype=torch.float32, device=device).unsqueeze(0)
        action_mask = self.get_action_mask()
        return state_tensor, action_mask

    def get_available_actions_for_dqn(self):
        # Return the five movement actions.
        return ["move_right", "move_left", "jump_right", "jump_left", "stay"]

    def choose_action(self):
        state, action_mask = self.get_state()
        action_logits, state_value = self.model(state)
        masked_logits = action_logits + action_mask
        action_probs = torch.softmax(masked_logits, dim=-1)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        if log_prob.dim() == 0:
            log_prob = log_prob.unsqueeze(0)
        self.buffer.states.append(state)
        self.buffer.actions.append(action)
        self.buffer.log_probs.append(log_prob)
        self.buffer.state_values.append(state_value)
        chosen_action = self.action_space[action.item()]
        return chosen_action

    def execute_action(self, action):
        if action in ["move_right", "move_left", "jump_right", "jump_left", "stay"]:
            reward = self.game_service.perform_action(action, {})
        else:
            reward = 0
        next_state = self.get_state()
        done = (self.game_service.position >= self.game_service.goal)
        return reward, next_state, done

    def perform_action(self):
        if self.first_turn:
            self.first_turn = False
            print("[LineGameAgent] Starting new episode...")
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

        print("################## AGENT INFO ##################")
        print("Chosen action:", action)
        print("Reward:", reward)
        print("Current Position:", self.game_service.position)
        print("################################################\n")

        if self.timestep >= self.update_timestep or done:
            self.update()
            self.timestep = 0

    def update(self):
        if len(self.buffer.rewards) == 0:
            return

        states = torch.cat(self.buffer.states)
        actions = torch.tensor([a.item() for a in self.buffer.actions], dtype=torch.long, device=device)
        old_log_probs = torch.stack([lp if lp.dim() > 0 else lp.unsqueeze(0) for lp in self.buffer.log_probs]).detach()
        state_values = torch.cat(self.buffer.state_values).squeeze(-1).detach()

        rewards = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(self.buffer.rewards), reversed(self.buffer.is_terminals)):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            rewards.insert(0, discounted_reward)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=device)
        if rewards.numel() > 1 and rewards.std() > 1e-5:
            rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-5)
        else:
            rewards = rewards - rewards.mean()

        advantages = rewards - state_values

        total_loss = 0
        for _ in range(self.K_epochs):
            action_logits, state_vals = self.model(states)
            action_probs = torch.softmax(action_logits, dim=-1)
            dist = torch.distributions.Categorical(action_probs)
            new_log_probs = dist.log_prob(actions)
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

        avg_loss = total_loss / self.K_epochs
        self.last_loss = avg_loss

        with open(self.log_file, "a") as f:
            f.write(f"{self.episode_count},{self.timestep_count},{avg_loss}\n")
        self.buffer.clear()

    def load_model(self):
        print("LOADING MODEL...")
        model_filename = self.filename
        if not os.path.exists(model_filename):
            print("⚠️ No saved model found. Starting fresh.")
            return
        try:
            checkpoint = torch.load(model_filename, map_location=device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print(f"✅ Model {model_filename} loaded successfully.")
        except Exception as e:
            print(f"⚠️ Could not load {model_filename}: {e}")

    def save_model(self):
        print("SAVING MODEL...")
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
        with open("linegame_scores.txt", "a") as file:
            file.write(str(self.total_episode_reward) + ",")

    def apply_final_reward(self, final_reward):
        last_state, _ = self.get_state()
        done = True
        action_idx = self.action_space.index("end_of_game")
        self.buffer.states.append(last_state)
        self.buffer.actions.append(torch.tensor(action_idx, device=device))
        self.buffer.log_probs.append(torch.tensor([0.0], device=device))
        self.buffer.state_values.append(torch.zeros((1, 1), device=device))
        self.buffer.rewards.append(final_reward)
        self.buffer.is_terminals.append(done)
        self.update()
        self.total_episode_reward += final_reward

#########################################
# Tournament Panel (Multiple Episodes with Fixed Turns)
#########################################
class TournamentPanel:
    def __init__(self, num_episodes=200, max_turns_per_episode=25):
        self.game_service = LineGameService(goal=20)  # Harder goal
        self.agent = LineGamePPOAgent("red", self.game_service)
        self.num_episodes = num_episodes
        self.max_turns_per_episode = max_turns_per_episode

        # For plotting:
        self.episode_rewards = []
        self.episode_losses = []

    def run_game(self):
        print("=== Starting Tournament ===")
        for episode in range(self.num_episodes):
            print(f"\n=== Episode {episode + 1} ===")
            turn = 0
            self.game_service.reset()
            self.agent.first_turn = True
            self.agent.total_episode_reward = 0
            # Play fixed number of turns per episode.
            while turn < self.max_turns_per_episode and self.game_service.position < self.game_service.goal:
                self.agent.perform_action()
                turn += 1
            # If the agent didn't reach the goal, apply a punishment.
            if self.game_service.position < self.game_service.goal:
                punishment = -5
                print(f"Episode {episode + 1} did not reach goal. Applying punishment: {punishment}")
                self.agent.apply_final_reward(punishment)
            else:
                bonus = 20
                print(f"Episode {episode + 1} reached the goal. Applying bonus: {bonus}")
                self.agent.apply_final_reward(bonus)
            print(f"Episode {episode + 1} ended at position {self.game_service.position} with total reward {self.agent.total_episode_reward}")
            self.episode_rewards.append(self.agent.total_episode_reward)
            self.episode_losses.append(self.agent.last_loss if hasattr(self.agent, 'last_loss') else 0.0)
            self.agent.episode_count += 1
        print("=== Tournament Ended ===")
        self.agent.save_model()
        self.plot_results()

    def plot_results(self):
        episodes = np.arange(1, self.num_episodes + 1)
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.plot(episodes, self.episode_rewards, marker='o', label='Cumulative Reward')
        plt.xlabel("Episode")
        plt.ylabel("Cumulative Reward")
        plt.title("Cumulative Reward per Episode")
        plt.legend()
        plt.grid(True)

        plt.subplot(1, 2, 2)
        plt.plot(episodes, self.episode_losses, marker='o', color='orange', label='Avg Batch Loss')
        plt.xlabel("Episode")
        plt.ylabel("Loss")
        plt.title("Average Batch Loss per Episode")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()

#########################################
# Main Entry Point
#########################################
if __name__ == "__main__":
    tournament = TournamentPanel(num_episodes=1000, max_turns_per_episode=25)
    tournament.run_game()
