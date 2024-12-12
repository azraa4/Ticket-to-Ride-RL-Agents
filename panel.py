import tkinter as tk
from tkinter import ttk
import multiprocessing
import os
import signal
from multiprocessing import Queue

import main_view


class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tournament Panel")
        self.root.geometry("1280x720")

        # Create a frame to hold the two columns
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the left and right columns
        self.left_column = tk.Frame(self.main_frame, bd=2, relief="solid")
        self.right_column = tk.Frame(self.main_frame, bd=2, relief="solid")

        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # LEFT COLUMN
        self.frame1 = tk.Frame(self.left_column)
        self.frame1.pack(fill=tk.X, pady=5)

        self.number_of_games_entry_label = tk.Label(self.frame1, text="Number of Games: ")
        self.number_of_games_entry_label.pack(side=tk.LEFT, padx=5)
        self.number_of_games_entry = tk.Entry(self.frame1)
        self.number_of_games_entry.pack(side=tk.LEFT, padx=5)

        self.test_name_entry_label = tk.Label(self.frame1, text="Test Name: ")
        self.test_name_entry_label.pack(side=tk.LEFT, padx=5)
        self.test_name_entry = tk.Entry(self.frame1)
        self.test_name_entry.pack(side=tk.LEFT, padx=5)

        self.frame2 = tk.Frame(self.left_column)
        self.frame2.pack(fill=tk.X, pady=5)

        self.number_of_AI_entry_label = tk.Label(self.frame2, text="Number of AIs: ")
        self.number_of_AI_entry_label.pack(side=tk.LEFT, padx=5)
        self.number_of_AI_entry = tk.Entry(self.frame2)
        self.number_of_AI_entry.pack(side=tk.LEFT, padx=5)

        self.frame3 = tk.Frame(self.left_column)
        self.frame3.pack(fill=tk.X, pady=5)

        self.time_between_actions_label = tk.Label(self.frame3, text="Time to take an action: ")
        self.time_between_actions_label.pack(side=tk.LEFT)
        self.time_between_actions_scale = tk.Scale(self.frame3, from_=2, to=20, orient=tk.HORIZONTAL, length=100)
        self.time_between_actions_scale.pack(side=tk.LEFT, padx=5)

        self.time_between_turns_label = tk.Label(self.frame3, text="Time to go to next turn: ")
        self.time_between_turns_label.pack(side=tk.LEFT)
        self.time_between_turns_scale = tk.Scale(self.frame3, from_=2, to=20, orient=tk.HORIZONTAL, length=100)
        self.time_between_turns_scale.pack(side=tk.LEFT, padx=5)

        self.frame4 = tk.Frame(self.left_column)
        self.frame4.pack(fill=tk.X, pady=5)

        self.visual_checkbox_var = tk.BooleanVar()
        self.visual_checkbox = tk.Checkbutton(self.frame4, text="Visualization of Game Environment",
                                              variable=self.visual_checkbox_var)
        self.visual_checkbox.pack(side=tk.LEFT,padx=5)

        self.console_checkbox_var = tk.BooleanVar()
        self.console_checkbox = tk.Checkbutton(self.frame4, text="Console",
                                               variable=self.console_checkbox_var)
        self.console_checkbox.pack(side=tk.LEFT, padx=5)

        self.start_buttons_frame = tk.Frame(self.left_column)
        self.start_buttons_frame.pack(fill=tk.X, pady=10)

        # Add buttons to the left column
        self.start_button = tk.Button(self.start_buttons_frame, text="Start All Games", command=self.start_games)
        self.start_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.stop_button = tk.Button(self.start_buttons_frame, text="Stop All Games", command=self.stop_games,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.stop_selected_button = tk.Button(self.start_buttons_frame, text="Stop Selected Games",
                                              command=self.stop_selected_process)
        self.stop_selected_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.listbox_frame1 = tk.Frame(self.left_column)
        self.listbox_frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)

        self.processes_label = tk.Label(self.listbox_frame1, text="Processes")
        self.processes_label.pack(side=tk.TOP, fill=tk.X, padx=5)

        self.refresh_processes_button = tk.Button(self.listbox_frame1, text="Refresh", command=self.update_process_listbox)
        self.refresh_processes_button.pack(side=tk.TOP, padx=10, fill=tk.X)

        self.processes_listbox = tk.Listbox(self.listbox_frame1)
        self.processes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.listbox_frame2 = tk.Frame(self.left_column)
        self.listbox_frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)

        self.log_files_label = tk.Label(self.listbox_frame2, text="Log Files")
        self.log_files_label.pack(side=tk.TOP, fill=tk.X, padx=5)

        self.refresh_log_files_button = tk.Button(self.listbox_frame2, text="Refresh", command=lambda: self.populate_log_files("logs"))
        self.refresh_log_files_button.pack(side=tk.TOP, padx=10, fill=tk.X)

        self.log_files_listbox = tk.Listbox(self.listbox_frame2)
        self.log_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)


        # Placeholder for right column content
        self.right_label = tk.Label(self.right_column, text="Game Output Area")
        self.right_label.pack(pady=5)

        # Treeview widget'ı
        columns = ("Name", "Color", "Points", "Cars")
        self.tree_players_info = ttk.Treeview(self.right_column, columns=columns, show="headings", height=5)

        # Sütun başlıklarını ayarla
        self.tree_players_info.heading("Name", text="Player Name")
        self.tree_players_info.heading("Color", text="Player Color")
        self.tree_players_info.heading("Points", text="Player Points")
        self.tree_players_info.heading("Cars", text="Player Cars")

        # Sütun genişliklerini ayarla
        self.tree_players_info.column("Name", width=100)
        self.tree_players_info.column("Color", width=100)
        self.tree_players_info.column("Points", width=100)
        self.tree_players_info.column("Cars", width=100)

        self.tree_players_info.pack(fill=tk.X, padx=10, pady=10)

        # Add scrollable text widget
        self.text_frame = tk.Frame(self.right_column)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_content_listbox = tk.Listbox(self.text_frame, yscrollcommand=self.scrollbar.set)
        self.log_content_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.log_content_listbox.yview)

        # LEFT COLUMN (Log dosyası listesine tıklama işlevi)
        self.log_files_listbox.bind("<<ListboxSelect>>", self.update_log_content_listbox)

        self.game_processes = []
        self.queues = {}

        self.populate_log_files("logs")
        self.update_display_timer()

    def start_games(self):
        try:
            num_games = int(self.number_of_games_entry.get())
        except ValueError:
            print("Please enter a valid number of games.")
            return

        self.stop_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

        console = self.console_checkbox_var.get()
        visualize = self.visual_checkbox_var.get()
        number_of_ai = self.number_of_AI_entry.get()
        test_name = self.test_name_entry.get()
        time_action = self.time_between_actions_scale.get()
        time_turn = self.time_between_turns_scale.get()

        for i in range(num_games):
            game_id = len(self.game_processes) + 1  # Assign a unique ID
            queue = Queue()
            self.queues[game_id] = queue
            process = multiprocessing.Process(target=self.run_game, args=(self.queues[game_id], game_id, console, number_of_ai, visualize, test_name, time_action, time_turn))
            process.start()
            self.game_processes.append((game_id, process))  # Store ID and process together
            self.processes_listbox.insert(tk.END, game_id)

        self.update_process_listbox()


    @staticmethod
    def run_game(queue, game_id, console, number_of_ai, visualize, test_name, time_action, time_turn):
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

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def stop_selected_process(self):
        selected_index = self.processes_listbox.curselection()
        if not selected_index:
            print("No process selected.")
            return

        selected_id = self.processes_listbox.get(selected_index)  # Fazladan boşlukları temizle
        selected_process = next((process for game_id, process in self.game_processes if int(game_id) == int(selected_id)),
                                None)

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
        self.root.mainloop()

    def populate_log_files(self, directory):
        try:
            txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
            self.log_files_listbox.delete(0, tk.END)
            for file in txt_files:
                self.log_files_listbox.insert(tk.END, file)
        except Exception as e:
            print(f"Hata oluştu: {e}")

    def update_process_listbox(self):
        for idx, (game_id, process) in enumerate(self.game_processes):
            if process.is_alive():
                self.processes_listbox.itemconfig(idx, bg="green")  # Çalışıyorsa yeşil
            else:
                self.processes_listbox.itemconfig(idx, bg="red")  # Durdurulduysa kırmızı



    def update_log_content_listbox(self, event):
        """Update the log content listbox with the provided content."""
        selected_index = self.log_files_listbox.curselection()
        if not selected_index:
            return  # Hiçbir dosya seçilmediyse işlevden çık
        selected_file = self.log_files_listbox.get(selected_index)

        try:
            with open(f"logs/{selected_file}", "r", encoding="utf-8") as file:
                content = file.readlines()
        except Exception as e:
            content = [f"Error reading file: {e}"]

        # Clear the listbox
        self.log_content_listbox.delete(0, tk.END)

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
            self.log_content_listbox.insert(tk.END, stripped_line)

            # Check for matching colors
            matching_colors = [color for keyword, color in color_keywords.items() if keyword in stripped_line]
            if len(matching_colors) == 1:
                # If only one color matches, set the background color
                if matching_colors[0] == "black":
                    self.log_content_listbox.itemconfig(idx, {'bg': "gray"})
                else:
                    self.log_content_listbox.itemconfig(idx, {'bg': matching_colors[0]})
            elif len(matching_colors) > 1:
                # If more than one color matches, leave the background white (default)
                self.log_content_listbox.itemconfig(idx, {'bg': 'white'})

    def update_tree_players_info(self):
        """Update the treeview with the last GAMESTATE information from the provided content."""
        selected_index = self.log_files_listbox.curselection()
        if not selected_index:
            return  # Hiçbir dosya seçilmediyse işlevden çık
        selected_file = self.log_files_listbox.get(selected_index)

        try:
            with open(f"logs/{selected_file}", "r", encoding="utf-8") as file:
                content = file.readlines()
        except Exception as e:
            content = [f"Error reading file: {e}"]


        # Clear the table
        self.tree_players_info.delete(*self.tree_players_info.get_children())

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
                    self.tree_players_info.insert("", tk.END, values=(name, color, points, cars))

    def update_display_timer(self):
        """Call display_log_file_content every 2 seconds if an item is selected."""
        selected_index = self.log_files_listbox.curselection()
        if selected_index:
            # Çağrı yapılması gereken item varsa
            self.update_tree_players_info()
        # Timer'ı tekrar başlat
        self.root.after(2000, self.update_display_timer)


if __name__ == "__main__":
    panel = ControlPanel()
    panel.run()