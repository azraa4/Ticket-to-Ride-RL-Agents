import gc
import os
import torch
import time

class PersistentModelManager:
    def __init__(self):
        self.checkpoint_data = None
        #self.filename = 'ddqn_model_1_4_5.pth'
        self.filename = 'empty.pth'

    def store_data(self, checkpoint: dict):
        """Save the dictionary in memory (RAM)."""
        self.checkpoint_data = checkpoint

    def load_data(self):
        """Return the stored checkpoint dictionary (or None if empty)."""
        return self.checkpoint_data

    def save_model(self):
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

            del self.checkpoint_data
            self.checkpoint_data = None

            gc.collect()
            torch.cuda.empty_cache()
            time.sleep(30)
        except Exception as e:
            print(f"Error saving model to {self.filename}: {e}")
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def load_model(self):
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