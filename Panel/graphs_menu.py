import matplotlib
matplotlib.use("TkAgg")
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter

class GraphsMenu:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.attributes("-topmost", True)
        self.window.title("Graphs Menu")
        self.window.geometry("600x350")  # increased height for more rows

        # Reward file selection (row 0)
        self.reward_file = None
        tk.Label(self.window, text="Reward File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.reward_file_label = tk.Label(self.window, text="No file selected", width=40, anchor="w")
        self.reward_file_label.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Select Reward File", command=self.select_reward_file).grid(row=0, column=2, padx=5, pady=5)

        # Loss file selection (row 1)
        self.loss_file = None
        tk.Label(self.window, text="Loss File:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.loss_file_label = tk.Label(self.window, text="No file selected", width=40, anchor="w")
        self.loss_file_label.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Select Loss File", command=self.select_loss_file).grid(row=1, column=2, padx=5, pady=5)

        # Q Values file selection (row 2)
        self.q_values_file = None
        tk.Label(self.window, text="Q Values File:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.q_values_file_label = tk.Label(self.window, text="No file selected", width=40, anchor="w")
        self.q_values_file_label.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Select Q Values File", command=self.select_q_values_file).grid(row=2, column=2, padx=5, pady=5)

        # TD Errors file selection (row 3)
        self.td_errors_file = None
        tk.Label(self.window, text="TD Errors File:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.td_errors_file_label = tk.Label(self.window, text="No file selected", width=40, anchor="w")
        self.td_errors_file_label.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Select TD Errors File", command=self.select_td_errors_file).grid(row=3, column=2, padx=5, pady=5)

        # Actions Log file selection (row 4)
        self.actions_file = None
        tk.Label(self.window, text="Actions Log File:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.actions_file_label = tk.Label(self.window, text="No file selected", width=40, anchor="w")
        self.actions_file_label.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(self.window, text="Select Actions Log File", command=self.select_actions_file).grid(row=4, column=2, padx=5, pady=5)

        # Moving Average window size input (row 5)
        tk.Label(self.window, text="Moving Average Window Size:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.ma_entry = tk.Entry(self.window)
        self.ma_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Apply button (row 6)
        tk.Button(self.window, text="Apply", command=self.apply_plots).grid(row=6, column=1, padx=5, pady=10)

    def select_reward_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Reward File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.reward_file = file_path
            self.reward_file_label.config(text=file_path.split("/")[-1])

    def select_loss_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Loss File",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.loss_file = file_path
            self.loss_file_label.config(text=file_path.split("/")[-1])

    def select_q_values_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Q Values File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.q_values_file = file_path
            self.q_values_file_label.config(text=file_path.split("/")[-1])

    def select_td_errors_file(self):
        file_path = filedialog.askopenfilename(
            title="Select TD Errors File",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.td_errors_file = file_path
            self.td_errors_file_label.config(text=file_path.split("/")[-1])

    def select_actions_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Actions Log File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.actions_file = file_path
            self.actions_file_label.config(text=file_path.split("/")[-1])

    def apply_plots(self):
        # Determine moving average window size if provided
        ma_input = self.ma_entry.get().strip()
        window_size = None
        if ma_input != "":
            try:
                window_size = int(ma_input)
                if window_size <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive integer for moving average window size.")
                return

        # Process Reward file if selected
        if self.reward_file:
            try:
                with open(self.reward_file, "r") as file:
                    raw_data = file.read().strip()
                    if not raw_data:
                        messagebox.showerror("Error", "The selected reward file is empty!")
                        return
                    scores = [int(value) for value in raw_data.split(",") if value.strip().lstrip("-").isdigit()]
                    if not scores:
                        messagebox.showerror("Error", "No valid scores found in the reward file!")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"Error reading reward file: {e}")
                return

            # Plot raw reward graph
            plt.figure(figsize=(10, 5))
            plt.plot(scores, marker="o", linestyle="-", color="b", alpha=0.7, label="Cumulative Reward")
            plt.axhline(y=0, color="r", linestyle="--", label="Zero Line")
            plt.xlabel("Episode")
            plt.ylabel("Reward")
            plt.title("Cumulative Reward per Episode (Raw)")
            plt.legend()
            plt.grid(True)
            plt.show(block=False)

            # Plot reward moving average if window size is provided and data is sufficient
            if window_size and len(scores) >= window_size:
                moving_avg = np.convolve(scores, np.ones(window_size) / window_size, mode="valid")
                plt.figure(figsize=(10, 5))
                plt.plot(scores, marker="o", linestyle="-", color="b", alpha=0.5, label="Cumulative Reward")
                plt.plot(range(window_size - 1, len(scores)), moving_avg, linestyle="-", color="r",
                         linewidth=2, label=f"Moving Avg ({window_size} episodes)")
                plt.axhline(y=0, color="black", linestyle="--", label="Zero Line")
                plt.xlabel("Episode")
                plt.ylabel("Reward")
                plt.title("Cumulative Reward per Episode with Moving Average")
                plt.legend()
                plt.grid(True)
                plt.show(block=False)

        # Process Loss file if selected
        if self.loss_file:
            try:
                with open(self.loss_file, "r") as file:
                    lines = file.readlines()
                    if not lines or len(lines) < 2:
                        messagebox.showerror("Error", "Not enough data in the selected loss file!")
                        return
                    losses = []
                    for line in lines[1:]:
                        parts = line.strip().split(",")
                        if len(parts) >= 3:
                            try:
                                loss_value = float(parts[2])
                                losses.append(loss_value)
                            except ValueError:
                                continue
                    if not losses:
                        messagebox.showerror("Error", "No valid loss values found in the loss file!")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"Error reading loss file: {e}")
                return

            # Plot raw loss graph
            plt.figure(figsize=(10, 5))
            plt.plot(range(len(losses)), losses, label="Raw Loss")
            plt.xlabel("Replay Calls")
            plt.ylabel("Loss")
            plt.title("Loss Over Time (Raw)")
            plt.legend()
            plt.grid(True)
            plt.show(block=False)

            # Plot loss moving average if window size is provided and data is sufficient
            if window_size and len(losses) >= window_size:
                moving_avg_loss = np.convolve(losses, np.ones(window_size) / window_size, mode="valid")
                plt.figure(figsize=(10, 5))
                plt.plot(range(len(losses)), losses, label="Raw Loss")
                plt.plot(range(window_size - 1, len(losses)), moving_avg_loss, label=f"Moving Avg ({window_size} steps)")
                plt.xlabel("Replay Calls")
                plt.ylabel("Loss")
                plt.title("Loss Over Time with Moving Average")
                plt.legend()
                plt.grid(True)
                plt.show(block=False)

        # Process Q Values file if selected
        if self.q_values_file:
            try:
                with open(self.q_values_file, "r") as file:
                    raw_data = file.read().strip()
                    if not raw_data:
                        messagebox.showerror("Error", "The selected Q Values file is empty!")
                        return
                    q_values = [float(x) for x in re.split(r"[\n,]+", raw_data) if x.strip() != ""]
                    if not q_values:
                        messagebox.showerror("Error", "No valid Q values found in the Q Values file!")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"Error reading Q Values file: {e}")
                return

            # Plot raw Q values graph
            plt.figure(figsize=(10, 5))
            plt.plot(q_values, marker="o", linestyle="-", color="m", alpha=0.7, label="Q Values")
            plt.xlabel("Step")
            plt.ylabel("Average Q Value")
            plt.title("Average Q Values per Step (Raw)")
            plt.legend()
            plt.grid(True)
            plt.show(block=False)

            # Plot Q values moving average if window size is provided and data is sufficient
            if window_size and len(q_values) >= window_size:
                moving_avg_q = np.convolve(q_values, np.ones(window_size) / window_size, mode="valid")
                plt.figure(figsize=(10, 5))
                plt.plot(q_values, marker="o", linestyle="-", color="m", alpha=0.5, label="Q Values")
                plt.plot(range(window_size - 1, len(q_values)), moving_avg_q, linestyle="-", color="c",
                         linewidth=2, label=f"Moving Avg ({window_size} steps)")
                plt.xlabel("Step")
                plt.ylabel("Average Q Value")
                plt.title("Average Q Values per Step with Moving Average")
                plt.legend()
                plt.grid(True)
                plt.show(block=False)

        # Process TD Errors file if selected
        if self.td_errors_file:
            try:
                with open(self.td_errors_file, "r") as file:
                    lines = file.readlines()
                    if not lines:
                        messagebox.showerror("Error", "The selected TD Errors file is empty!")
                        return
                    td_errors = []
                    for line in lines:
                        parts = line.strip().split(",")
                        if len(parts) >= 2:
                            try:
                                td_error = float(parts[1])
                                td_errors.append(td_error)
                            except ValueError:
                                continue
                    if not td_errors:
                        messagebox.showerror("Error", "No valid TD error values found in the TD Errors file!")
                        return
            except Exception as e:
                messagebox.showerror("Error", f"Error reading TD Errors file: {e}")
                return

            # Plot raw TD errors graph
            plt.figure(figsize=(10, 5))
            plt.plot(range(1, len(td_errors) + 1), td_errors, marker="o", linestyle="-", color="g", label="TD Errors")
            plt.xlabel("Batch")
            plt.ylabel("TD Error")
            plt.title("TD Errors per Batch (Raw)")
            plt.legend()
            plt.grid(True)
            plt.show(block=False)

            # Plot TD errors moving average if window size is provided and data is sufficient
            if window_size and len(td_errors) >= window_size:
                moving_avg_td = np.convolve(td_errors, np.ones(window_size) / window_size, mode="valid")
                plt.figure(figsize=(10, 5))
                plt.plot(range(1, len(td_errors) + 1), td_errors, marker="o", linestyle="-", color="g", alpha=0.5, label="TD Errors")
                plt.plot(range(window_size, len(td_errors) + 1), moving_avg_td, linestyle="-", color="orange",
                         linewidth=2, label=f"Moving Avg ({window_size} batches)")
                plt.xlabel("Batch")
                plt.ylabel("TD Error")
                plt.title("TD Errors per Batch with Moving Average")
                plt.legend()
                plt.grid(True)
                plt.show(block=False)

        # Process Actions Log file if selected (only create overall bar plot)
        if self.actions_file:
            try:
                with open(self.actions_file, "r") as file:
                    lines = [line.strip() for line in file if line.strip() != ""]
                    if not lines:
                        messagebox.showerror("Error", "The selected actions file is empty!")
                        return
                valid_actions = ["claim_route", "draw_blind", "draw_red_card", "draw_blue_card", "draw_yellow_card",
                                 "draw_green_card", "draw_pink_card", "draw_orange_card", "draw_white_card",
                                 "draw_black_card", "draw_joker_card"]
                counter = Counter([action for action in lines if action in valid_actions])
                overall_counts = {action: counter.get(action, 0) for action in valid_actions}
            except Exception as e:
                messagebox.showerror("Error", f"Error reading actions log file: {e}")
                return

            # Plot overall bar plot for actions
            plt.figure(figsize=(12, 6))
            actions = list(overall_counts.keys())
            counts = list(overall_counts.values())
            plt.bar(actions, counts, color="skyblue")
            plt.xlabel("Action")
            plt.ylabel("Frequency")
            plt.title("Overall Frequency of Actions (Raw)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show(block=False)
