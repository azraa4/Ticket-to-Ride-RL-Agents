# prioritized_replay_memory.py
import numpy as np
import global_vars


class PrioritizedReplayMemory:
    """
    A simple proportional Prioritized Experience Replay (PER) buffer
    as described in Schaul et al. (2016).

    Args
    ----
    capacity (int):  Max number of stored transitions.
    alpha    (float):Exponent that determines how much prioritisation is used
                     (0 = uniform replay, 1 = full prioritisation).
    """

    def __init__(self, capacity: int, alpha: float = 0.3):
        self.rng = np.random.RandomState()

        self.capacity   = capacity
        self.alpha      = alpha
        self.memory     = []                               # list[transition]
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.pos        = 0                                # next insert position

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #
    def push(
        self,
        state,
        action,
        reward,
        next_state,
        done,
        state_mask,
        next_state_mask,
    ):
        """
        Add a new transition.  New items are assigned *max priority* so they
        are guaranteed to be sampled at least once.
        """
        # Highest priority so far (or 1 for very first insert)
        if self.memory:
            valid_prios = self.priorities[: len(self.memory)]      # ⟵ CHANGED
            max_prio    = valid_prios.max()                       # ⟵ CHANGED
        else:
            max_prio = 1.0

        transition = (
            state, action, reward,
            next_state, done, state_mask, next_state_mask
        )

        if len(self.memory) < self.capacity:
            self.memory.append(transition)
        else:                                              # overwrite oldest
            self.memory[self.pos] = transition

        self.priorities[self.pos] = max_prio
        self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int, beta: float):
        """
        Sample a batch of transitions with importance-sampling (IS) weights.

        Args
        ----
        batch_size (int)
        beta       (float): IS exponent (0 = no correction, 1 = full correction)
        """
        prios = self.priorities[: len(self.memory)]

        # 1.  Compute sampling probabilities
        probs = prios ** self.alpha
        probs_sum = probs.sum()
        if probs_sum == 0:
            # All priorities were 0 → fall back to uniform
            probs[:] = 1.0 / len(probs)
        else:
            probs /= probs_sum

        # 2.  Draw sample WITHOUT replacement to avoid duplicates
        indices = self.rng.choice(                                 # ⟵ CHANGED
            len(self.memory),
            batch_size,
            p=probs,
            replace=False,
        )
        samples = [self.memory[i] for i in indices]

        # 3.  Importance-sampling weights
        weights = (len(self.memory) * probs[indices]) ** (-beta)
        weights /= weights.max()                          # normalise to 1

        return samples, indices, weights.astype(np.float32)

    def update_priorities(self, indices, priorities):
        """
        Update the priorities of sampled transitions.

        A small ε is added so priorities never hit exactly zero.
        """
        for idx, prio in zip(indices, priorities):
            self.priorities[idx] = float(prio) + 1e-6

    # ------------------------------------------------------------------ #
    #  Pythonic helpers
    # ------------------------------------------------------------------ #
    def __len__(self):
        return len(self.memory)