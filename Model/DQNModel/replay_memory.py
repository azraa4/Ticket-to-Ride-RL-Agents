import random
from collections import deque
import numpy as np

class ReplayMemory:
    def __init__(self, capacity):
        """
        Initialize replay buffer.
        :param capacity: Maximum size of the memory.
        """
        self.memory = deque([], maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        """
        Store experience tuple (s, a, r, s', done).
        """
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        """
        Sample a batch of experiences for training.
        """
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)
