# persistent_model_manager.py
import os
import torch
from Controller.PersistentModel.dqn import DQN
from Controller.PersistentModel.replay_memory import PrioritizedReplayMemory

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class PersistentModelManager:
    def __init__(self, state_size, action_space, model_filename="ddqn_model_1_2_4.pth", lr=0.001, memory_size=50000):
        self.model_filename = model_filename
        self.state_size = state_size
        self.action_space = action_space

        # Create models and optimizer
        self.model = DQN(state_size, len(action_space)).to(device)
        self.target_model = DQN(state_size, len(action_space)).to(device)
        self.target_model.load_state_dict(self.model.state_dict())
        self.target_model.eval()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.memory = PrioritizedReplayMemory(memory_size)
        self.epsilon = 1.0  # start value
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995

        # Load if a checkpoint exists
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_filename):
            try:
                checkpoint = torch.load(self.model_filename, map_location=device, weights_only=False)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.target_model.load_state_dict(checkpoint['target_model_state_dict'])
                self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
                self.epsilon = checkpoint['epsilon']
                self.memory.memory = checkpoint.get('memory', [])
                saved_priorities = checkpoint.get('priorities', None)
                if saved_priorities is not None:
                    self.memory.priorities = saved_priorities
                self.memory.pos = checkpoint.get('pos', 0)
                print("✅ Persistent model loaded successfully.")
            except Exception as e:
                print("⚠️ Could not load persistent model:", e)
        else:
            print("⚠️ No persistent model found. Starting with a fresh model.")

    def save_model(self):
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'target_model_state_dict': self.target_model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'memory': self.memory.memory,
            'priorities': self.memory.priorities,
            'pos': self.memory.pos,
        }
        print("Saving model with epsilon:", self.epsilon)
        temp_filename = self.model_filename + ".tmp"
        with open(temp_filename, 'wb') as f:
            torch.save(checkpoint, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_filename, self.model_filename)
        print(f"Model saved as {self.model_filename}. Replay buffer size: {len(self.memory)}")

    def soft_update_target(self, tau=0.005):
        for target_param, local_param in zip(self.target_model.parameters(), self.model.parameters()):
            target_param.data.copy_(tau * local_param.data + (1 - tau) * target_param.data)
