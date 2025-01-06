import os
import multiprocessing
from multiprocessing import Queue

import main_view

from panel_gui import PanelGUI
import tkinter as tk
from tkinter import ttk, messagebox

import shutil


class PanelController:
    def __init__(self, gui):
        self.gui = gui
        self.game_processes = []
        self.queues = {}
        self.agents = []

        self.move_logs_to_history()

    def add_player(self):
        agent_type = self.gui.agent_type_var.get()
        color = self.gui.color_var.get()

        if not agent_type or not color:
            messagebox.showwarning("Warning", "Please select both an agent type and a color.")
            return

        self.agents.append({
            'agent_type': agent_type,
            'color': color,
            'total_points': 0,
            'total_longest_route': 0,
            'total_cars_spent': 0,
            'total_turn_played': 0,
            'total_time_played': 0.0,
            'total_wins':0,
        })
        self.gui.tree_general_players_info.insert(
            "",
            tk.END,
            values=(agent_type, color, 0, 0, 0, 0, 0)  # Default
        )

        self.gui.available_colors.remove(color)
        self.gui.color_dropdown["values"] = self.gui.available_colors
        self.gui.color_var.set("")

    def start_games(self):
        try:
            num_games = int(self.gui.number_of_games_entry.get())
        except ValueError:
            print("Please enter a valid number of games.")
            return

        self.gui.stop_button.config(state=tk.NORMAL)
        self.gui.start_button.config(state=tk.DISABLED)

        console = self.gui.console_checkbox_var.get()
        visualize = self.gui.visual_checkbox_var.get()
        test_name = self.gui.test_name_entry.get()
        time_action = self.gui.time_between_actions_scale.get()
        time_turn = self.gui.time_between_turns_scale.get()

        for i in range(num_games):
            game_id = len(self.game_processes) + 1  # Assign a unique ID
            queue = Queue()
            self.queues[game_id] = queue
            process = multiprocessing.Process(target=self.run_game, args=(self.queues[game_id], game_id, console, self.agents, visualize, test_name, time_action, time_turn))
            process.start()
            self.game_processes.append((game_id, process))  # Store ID and process together
            self.gui.processes_listbox.insert(tk.END, game_id)

        self.move_logs_to_history()
        self.update_process_listbox()
        self.populate_log_files("../logs")

    @staticmethod
    def run_game(queue, game_id, console, number_of_ai, visualize, test_name, time_action, time_turn):
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        os.chdir(project_root)

        print(f"Starting game {game_id}...")
        from main_view import main, MainGameApp
        main_view.main(queue, game_id, True, console, number_of_ai, visualize, test_name, time_action, time_turn)

    def stop_games(self):
        for game_id, process in self.game_processes:
            if process.is_alive():
                print(f"stop_{game_id}")
                self.send_message_to_games(game_id,f"stop_{game_id}")
                try:
                    process.terminate()  # Terminate process
                    process.join()  # Wait for process to end
                    print(f"Game {game_id} stopped successfully.")
                except Exception as e:
                    print(f"Failed to stop game {game_id}: {e}")

        self.update_process_listbox()

        self.gui.start_button.config(state=tk.NORMAL)
        self.gui.stop_button.config(state=tk.DISABLED)


    def stop_selected_process(self):
        selected_index = self.gui.processes_listbox.curselection()
        if not selected_index:
            print("No process selected.")
            return

        selected_id = self.gui.processes_listbox.get(selected_index)  # Fazladan boşlukları temizle
        selected_process = next((process for game_id, process in self.game_processes if int(game_id) == int(selected_id)), None)

        if selected_process and selected_process.is_alive():
            try:
                print(f"Stopping selected process: {selected_id}")
                self.send_message_to_games(int(selected_id), f"stop_{selected_id}")
                selected_process.terminate()  # Terminate the selected process
                selected_process.join()  # Wait for the process to end
                print(f"Process {selected_id} stopped successfully.")
            except Exception as e:
                print(f"Failed to stop process {selected_id}: {e}")
        else:
            print(f"Process {selected_id} is not active or does not exist.")

        self.update_process_listbox()


    def send_message_to_games(self, game_id, message):
        self.queues[game_id].put(message)

    def run(self):
        self.gui.root.mainloop()

    def populate_log_files(self, directory):
        try:
            txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            self.gui.log_files_listbox.delete(0, tk.END)
            for file in txt_files:
                without_txt=file.replace(".txt", "")
                self.gui.log_files_listbox.insert(tk.END, without_txt)
        except Exception as e:
            print(f"ERROR: {e}")

    def populate_history_files(self, directory):
        try:
            txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            self.gui.history_listbox.delete(0, tk.END)
            for file in txt_files:
                without_txt = file.replace(".txt", "")
                self.gui.history_listbox.insert(tk.END, without_txt)
        except Exception as e:
            print(f"ERROR: {e}")

    def update_process_listbox(self):
        for idx, (game_id, process) in enumerate(self.game_processes):
            if process.is_alive():
                self.gui.processes_listbox.itemconfig(idx, bg="green")  # Çalışıyorsa yeşil
            else:
                self.gui.processes_listbox.itemconfig(idx, bg="red")  # Durdurulduysa kırmızı

    def update_log_content_listbox(self, event, listbox_type=None):
        """Update the log content listbox with the provided content."""
        selected_file = None
        if(listbox_type == "log"):
            selected_index = self.gui.log_files_listbox.curselection()
            if not selected_index:
                return
            selected_file = self.gui.log_files_listbox.get(selected_index)
        elif(listbox_type == "history"):
            selected_index = self.gui.history_listbox.curselection()
            if not selected_index:
                return
            selected_file = self.gui.history_listbox.get(selected_index)

        try:
            if(listbox_type=="log"):
                with open(f"../logs/{selected_file}.txt", "r", encoding="utf-8") as file:
                    content = file.readlines()
            elif(listbox_type == "history"):
                with open(f"../logs/history/{selected_file}.txt", "r", encoding="utf-8") as file:
                    content = file.readlines()
        except Exception as e:
            content = [f"Error reading file: {e}"]

        # Clear the listbox
        self.gui.log_content_listbox.delete(0, tk.END)

        # Define color mappings
        color_keywords = {
            "Red": "red",
            "Blue": "blue",
            "Green": "green",
            "Yellow": "yellow",
            "Black": "black"
        }

        # Add all lines to the listbox
        for idx, line in enumerate(content):
            stripped_line = line.strip()
            self.gui.log_content_listbox.insert(tk.END, stripped_line)

            # Check for matching colors
            matching_colors = [color for keyword, color in color_keywords.items() if keyword in stripped_line]
            if len(matching_colors) == 1:
                # If only one color matches, set the background color
                if matching_colors[0] == "black":
                    self.gui.log_content_listbox.itemconfig(idx, {'bg': "gray"})
                else:
                    self.gui.log_content_listbox.itemconfig(idx, {'bg': matching_colors[0]})
            elif len(matching_colors) > 1:
                # If more than one color matches, leave the background white (default)
                self.gui.log_content_listbox.itemconfig(idx, {'bg': 'white'})
        self.update_tree_players_info("history")

    def update_tree_players_info(self, listbox_type="log"):
        """Update the treeview with the last GAMESTATE information from the provided content."""
        selected_file = None
        if (listbox_type == "log"):
            selected_index = self.gui.log_files_listbox.curselection()
            if not selected_index:
                return
            selected_file = self.gui.log_files_listbox.get(selected_index)
        elif (listbox_type == "history"):
            selected_index = self.gui.history_listbox.curselection()
            if not selected_index:
                return
            selected_file = self.gui.history_listbox.get(selected_index)

        selected_file+=".txt"

        try:
            if(listbox_type=="log"):
                with open(f"../logs/{selected_file}", "r", encoding="utf-8") as file:
                    content = file.readlines()
            elif(listbox_type == "history"):
                with open(f"../logs/history/{selected_file}", "r", encoding="utf-8") as file:
                    content = file.readlines()
        except Exception as e:
            content = [f"Error reading file: {e}"]

        # Clear the table
        self.gui.tree_players_info.delete(*self.gui.tree_players_info.get_children())

        # Find the last GAMESTATE line
        last_gamestate = None
        for line in content:
            if line.startswith("GAMESTATE:"):
                last_gamestate = line.strip()

        # If there is a last GAMESTATE line, parse and populate the table
        if last_gamestate:
            # Parse GAMESTATE and populate Treeview
            parts = last_gamestate.split("|")  # Split the line by "|"
            for part in parts:
                if "Player" in part:
                    # Extract player details
                    details = part.split(", ")
                    name = details[0].split(": ")[1]
                    color = details[1].split(": ")[1]
                    points = details[2].split(": ")[1]
                    cars = details[3].split(": ")[1]

                    # Insert into Treeview
                    self.gui.tree_players_info.insert("", tk.END, values=(name, color, points, cars))

    def move_logs_to_history(self):
        logs_directory = os.path.join(os.getcwd(), "../logs")
        history_directory = os.path.join(logs_directory, "history")

        # Ensure the history directory exists
        if not os.path.exists(history_directory):
            os.makedirs(history_directory)

        # Iterate through .txt files in the logs directory
        for file in os.listdir(logs_directory):
            if file.endswith(".txt"):
                source = os.path.join(logs_directory, file)
                destination = os.path.join(history_directory, file)
                try:
                    shutil.move(source, destination)  # Move the file
                    print(f"Moved {file} to history directory.")
                except Exception as e:
                    print(f"Failed to move {file}: {e}")

    def refresh_game_summaries(self):
        """Refresh the TreeView with the latest log data."""
        logs_directory = "../logs"

        self.gui.tree_game_summaries.delete(*self.gui.tree_game_summaries.get_children())

        for log_file in os.listdir(logs_directory):
            if log_file.endswith(".txt"):
                log_path = os.path.join(logs_directory, log_file)
                try:
                    with open(log_path, "r", encoding="utf-8") as file:
                        lines = file.readlines()
                        if not lines:
                            continue

                        last_line = lines[-1].strip()

                        if last_line.startswith("RESULTS:"):
                            parts = last_line.replace("RESULTS:", "").split(", ")

                            player_amount = parts[0]
                            winner = parts[1]
                            longest_route = parts[2]
                            turns_played = parts[3]
                            time_played = parts[4]

                            game_name = os.path.splitext(log_file)[0]

                            self.gui.tree_game_summaries.insert("","end",values=(game_name, player_amount, winner, longest_route, turns_played, time_played))
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")

        self.refresh_general_agent_status_treeview()

    def update_agents_list(self):
        """Update the agents list by reading all log files."""
        logs_directory = "../logs"

        for agent in self.agents:
            agent['total_points'] = 0
            agent['total_longest_route'] = 0
            agent['total_cars_spent'] = 0
            agent['total_turn_played'] = 0
            agent['total_time_played'] = 0
            agent['total_wins']=0

        # Process each log file
        for log_file in os.listdir(logs_directory):
            if log_file.endswith(".txt"):
                log_path = os.path.join(logs_directory, log_file)
                try:
                    with open(log_path, "r", encoding="utf-8") as file:
                        lines = file.readlines()
                        if len(lines) < 2:
                            continue  # Skip files with insufficient lines

                        # Parse the second-to-last line
                        players_line = lines[-2].strip()
                        if players_line.startswith("PLAYERS:"):
                            player_tuples = self.parse_players_line(players_line)  # Parse the PLAYERS line

                            # Update existing agents in the agents list
                            for player in player_tuples:
                                color, points, longest_route, cars_spent, turns_played, time_played, winner = player

                                # Find the matching agent in the self.agents list
                                for agent in self.agents:
                                    if agent["color"] == color:
                                        # Update the agent's values
                                        agent["total_points"] += points
                                        agent["total_longest_route"] += 1 if longest_route else 0
                                        agent["total_cars_spent"] += cars_spent
                                        agent["total_turn_played"] += turns_played
                                        agent["total_time_played"] += time_played
                                        agent["total_wins"] += 1 if winner else 0
                                        break
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")

    def refresh_general_agent_status_treeview(self):
        """Refresh the TreeView with the updated agents list."""
        self.update_agents_list()

        # Clear the TreeView
        self.gui.tree_general_players_info.delete(*self.gui.tree_general_players_info.get_children())

        # Populate TreeView with updated agents list
        for agent in self.agents:
            self.gui.tree_general_players_info.insert(
                "", "end",
                values=(
                    agent["agent_type"],
                    agent["color"],
                    agent["total_points"],
                    agent["total_wins"],
                    agent["total_longest_route"],
                    agent["total_cars_spent"],
                    agent["total_turn_played"],
                    round(agent["total_time_played"], 2)
                )
            )

        mean_points = self.calculate_points_mean(self.agents)
        std_dev_points = self.calculate_points_std_dev(self.agents)

        try:
            most_winner = max(self.agents, key=lambda agent: agent.get("total_wins", 0))["color"]
        except ValueError:
            most_winner = "No winner available"  # Or handle this appropriately if no max is found

            # Get the agent with the longest route
        try:
            most_longest_route = max(self.agents, key=lambda agent: agent.get("total_longest_route", 0))["color"]
        except ValueError:
            most_longest_route = "No longest route available"  # Or handle this appropriately if no max is found
        self.gui.update_analysis_labels(mean_points, std_dev_points, most_winner, most_longest_route)

    def parse_players_line(self, players_line):
        """Parse the PLAYERS line into a list of tuples."""
        players_data = players_line.replace("PLAYERS:", "").split(";")
        player_tuples = []
        for player_data in players_data:
            if player_data.strip():
                parts = player_data.split(", ")
                player_tuples.append((
                    parts[0],  # Agent Color
                    int(parts[1]),  # Points
                    parts[2] == "True",  # Longest Route Achieved
                    int(parts[3]),  # Cars Spent
                    int(parts[4]),  # Turns Played
                    float(parts[5]),  # Time Played
                    parts[6] == "True"  # Winner
                ))
        return player_tuples

    def calculate_standard_deviation(self, data):
        if len(data) == 0:
            return 0
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return variance ** 0.5

    def calculate_points_std_dev(self, agents):
        total_points = [agent["total_points"] for agent in agents]
        return self.calculate_standard_deviation(total_points)

    def calculate_points_mean(self, agents):
        total_points = [agent["total_points"] for agent in agents]
        if(len(total_points)==0):
            return 0
        return sum(total_points) / len(total_points)

    def reset_agents(self):
        self.agents=[]
        self.refresh_general_agent_status_treeview()
        self.gui.reset_dropdown()

if __name__ == "__main__":
    root = tk.Tk()

    panel_controller = PanelController(None)

    gui = PanelGUI(root, panel_controller)
    panel_controller.gui = gui

    root.mainloop()