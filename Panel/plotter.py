import matplotlib
matplotlib.use("TkAgg")  # Fix for PyCharm Matplotlib issue
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog

class Plotter:
    def __init__(self):
        """Initialize without scores. Scores will be loaded from a selected file."""
        self.scores = self.load_scores_from_file()

    def load_scores_from_file(self):
        """Opens a file dialog for the user to select a score file and loads the data safely."""
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window

        file_path = filedialog.askopenfilename(title="Select Score File",
                                               filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])

        if not file_path:  # If user cancels file selection
            print("No file selected. Exiting...")
            exit()

        # Read and process scores
        with open(file_path, "r") as file:
            raw_data = file.read().strip()

            # Ensure there is data to process
            if not raw_data:
                print("Error: Selected file is empty!")
                exit()

            # Split, filter out empty values, and convert to integers
            scores = [int(value) for value in raw_data.split(",") if value.strip().lstrip("-").isdigit()]

        if not scores:
            print("Error: No valid scores found in the file!")
            exit()

        print(f"Loaded {len(scores)} scores from: {file_path}")
        return scores

    def plot_rewards(self):
        """Plots cumulative reward per episode."""
        plt.figure(figsize=(10, 5))
        plt.plot(self.scores, marker="o", linestyle="-", color="b", alpha=0.7, label="Cumulative Reward")
        plt.axhline(y=0, color="r", linestyle="--", label="Zero Line")  # Helps visualize negative scores

        # Labels and title
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Cumulative Reward per Episode")
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_rewards_with_moving_avg(self, window_size1=5, window_size2=20):
        """Plots cumulative rewards with two moving averages."""

        # Moving averages for both window sizes
        moving_avg1 = np.convolve(self.scores, np.ones(window_size1) / window_size1, mode='valid')
        moving_avg2 = np.convolve(self.scores, np.ones(window_size2) / window_size2, mode='valid')

        plt.figure(figsize=(10, 5))

        # Plot original scores
        plt.plot(self.scores, marker="o", linestyle="-", color="b", alpha=0.5, label="Cumulative Reward")

        # Plot first moving average (Red)
        plt.plot(range(window_size1 - 1, len(self.scores)), moving_avg1, marker="", linestyle="-", color="r",
                 linewidth=2, label=f"Moving Avg ({window_size1} episodes)")

        # Plot second moving average (Green)
        plt.plot(range(window_size2 - 1, len(self.scores)), moving_avg2, marker="", linestyle="-", color="g",
                 linewidth=2, label=f"Moving Avg ({window_size2} episodes)")

        plt.axhline(y=0, color="black", linestyle="--", label="Zero Line")

        # Labels and title
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("Cumulative Reward per Episode with Two Moving Averages")
        plt.legend()
        plt.grid(True)
        plt.show()


# Create a Plotter object and call methods
plotter = Plotter()
plotter.plot_rewards()  # Plot without moving average
plotter.plot_rewards_with_moving_avg(5, 20)  # Plot with moving average
