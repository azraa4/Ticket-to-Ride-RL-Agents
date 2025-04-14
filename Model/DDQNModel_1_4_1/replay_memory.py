# prioritized_replay_memory.py
import numpy as np
import global_vars

class PrioritizedReplayMemory:
    def __init__(self, capacity, alpha=0.6):
        """
        Initialize prioritized replay memory.
        :param capacity: Maximum number of transitions.
        :param alpha: How much prioritization is used (0 = no prioritization, 1 = full prioritization).
        """
        np.random.seed(global_vars.random_seed)

        self.capacity = capacity
        self.alpha = alpha
        self.memory = []  # list of transitions
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.pos = 0

    def push(self, state, action, reward, next_state, done, state_mask, next_state_mask):
        new_priority = 1.0
        transition = (state, action, reward, next_state, done, state_mask, next_state_mask)
        if len(self.memory) < self.capacity:
            self.memory.append(transition)
        else:
            self.memory[self.pos] = transition
        self.priorities[self.pos] = new_priority
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
