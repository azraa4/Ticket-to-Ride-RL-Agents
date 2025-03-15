# prioritized_replay_memory.py
import random
import numpy as np


class PrioritizedReplayMemory:
    def __init__(self, capacity, alpha=0.6):
        """
        Initialize prioritized replay memory.
        :param capacity: Maximum number of transitions.
        :param alpha: How much prioritization is used (0 = no prioritization, 1 = full prioritization).
        """
        self.capacity = capacity
        self.alpha = alpha
        self.memory = []  # list of transitions
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.pos = 0

    def push(self, state, action, reward, next_state, done):
        """Store a new transition and assign it the maximum current priority."""
        max_priority = self.priorities.max() if self.memory else 1.0
        if len(self.memory) < self.capacity:
            self.memory.append((state, action, reward, next_state, done))
        else:
            self.memory[self.pos] = (state, action, reward, next_state, done)
        self.priorities[self.pos] = max_priority
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size, beta=0.4):
        if len(self.memory) == self.capacity:
            prios = self.priorities
        else:
            prios = self.priorities[:len(self.memory)]

        # Compute probabilities safely: if the sum is zero, fallback to uniform probabilities.
        total_priority = prios.sum()
        if total_priority == 0:
            probs = np.ones_like(prios) / len(prios)
        else:
            probs = prios ** self.alpha
            probs_sum = probs.sum()
            if probs_sum == 0:
                probs = np.ones_like(prios) / len(prios)
            else:
                probs /= probs_sum

        # Sample indices according to the computed probabilities.
        indices = np.random.choice(len(self.memory), batch_size, p=probs)
        samples = [self.memory[idx] for idx in indices]

        # Compute importance-sampling weights.
        total = len(self.memory)
        weights = (total * probs[indices]) ** (-beta)
        weights /= weights.max()  # Normalize for stability

        return samples, indices, np.array(weights, dtype=np.float32)

    def update_priorities(self, indices, priorities):
        """Update priorities for the sampled transitions."""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority

    def __len__(self):
        return len(self.memory)
