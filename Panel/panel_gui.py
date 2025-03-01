import tkinter as tk
from tkinter import ttk
import random
import time

import global_vars


class PanelGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Tournament Panel")
        self.root.geometry("1280x720")

        # Create a frame to hold the two columns
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create the left and right columns
        self.left_column = tk.Frame(self.main_frame, bd=0, relief="solid", bg="#dbdbdb")
        self.right_column = tk.Frame(self.main_frame, bd=0, relief="solid", bg="#dbdbdb")

        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_left_column()
        self.create_right_column()

        # LEFT COLUMN (Log dosyası listesine tıklama işlevi)
        self.log_files_listbox.bind("<<ListboxSelect>>",
                                    lambda event: self.controller.update_log_content_listbox(event, listbox_type="log"))
        self.history_listbox.bind("<<ListboxSelect>>", lambda event: self.controller.update_log_content_listbox(event,listbox_type="history"))

        self.game_processes = []
        self.queues = {}

        self.controller.populate_log_files("logs")
        self.update_display_timer()

        self.loop_count = 0

    def create_left_column(self):
        # LEFT COLUMN
        self.upper_frame = tk.Frame(self.left_column, bd=4, relief="groove")
        self.upper_frame.pack(fill=tk.X, pady=5, padx=5)

        self.frame1 = tk.Frame(self.upper_frame)
        self.frame1.pack(fill=tk.X, pady=5)

        self.number_of_process_entry_label = tk.Label(self.frame1, text="Number of Process: ")
        self.number_of_process_entry_label.pack(side=tk.LEFT, padx=5)
        self.number_of_process_entry = tk.Entry(self.frame1)
        self.number_of_process_entry.pack(side=tk.LEFT, padx=5)

        self.test_name_entry_label = tk.Label(self.frame1, text="Test Name: ")
        self.test_name_entry_label.pack(side=tk.LEFT, padx=5)
        self.test_name_entry = tk.Entry(self.frame1)
        self.test_name_entry.pack(side=tk.LEFT, padx=5)

        self.frame2 = tk.Frame(self.upper_frame)
        self.frame2.pack(fill=tk.X, pady=5)

        # Label ve Agent Type Dropdown
        self.label_agent = tk.Label(self.frame2, text="Agent Type: ")
        self.label_agent.pack(side=tk.LEFT, padx=5)

        self.agent_type_var = tk.StringVar()
        agent_dropdown = ttk.Combobox(self.frame2, textvariable=self.agent_type_var, state="readonly", width=15)
        agent_dropdown["values"] = ["RandomAgent", "AgentX", "QLearningAgent", "DeepQNetworkAgent","2DeepQNetworkAgent", "DDQNAgent", "2DDQNAgent"]
        agent_dropdown.pack(side=tk.LEFT, padx=5)

        # Label, Color Dropdown and Button
        self.available_colors = ["Red", "Blue", "Green", "Yellow", "Black"]
        label_color = tk.Label(self.frame2, text="Color: ")
        label_color.pack(side=tk.LEFT, padx=5)

        self.color_var = tk.StringVar()
        self.color_dropdown = ttk.Combobox(self.frame2, textvariable=self.color_var, state="readonly", width=10)
        self.color_dropdown["values"] = self.available_colors
        self.color_dropdown.pack(side=tk.LEFT, padx=5)

        add_player_button = tk.Button(self.frame2, text="Add Player", command=self.controller.add_player)
        add_player_button.pack(side=tk.LEFT, padx=5)

        reset_players_button = tk.Button(self.frame2, text="Reset Player", command=self.controller.reset_agents)
        reset_players_button.pack(side=tk.LEFT, padx=5)

        # Time Settings Frame
        self.frame3 = tk.Frame(self.upper_frame)
        self.frame3.pack(fill=tk.X, pady=5)

        self.time_between_actions_label = tk.Label(self.frame3, text="Time to take an action: ")
        self.time_between_actions_label.pack(side=tk.LEFT)
        self.time_between_actions_scale = tk.Scale(self.frame3, from_=0, to=20, orient=tk.HORIZONTAL, length=100)
        self.time_between_actions_scale.pack(side=tk.LEFT, padx=5)

        self.time_between_turns_label = tk.Label(self.frame3, text="Time to go to next turn: ")
        self.time_between_turns_label.pack(side=tk.LEFT)
        self.time_between_turns_scale = tk.Scale(self.frame3, from_=0, to=20, orient=tk.HORIZONTAL, length=100)
        self.time_between_turns_scale.pack(side=tk.LEFT, padx=5)

        self.frame4 = tk.Frame(self.upper_frame)
        self.frame4.pack(fill=tk.X, pady=5)

        self.visual_checkbox_var = tk.BooleanVar()
        self.visual_checkbox = tk.Checkbutton(self.frame4, text="Visualization of Game Environment",
                                              variable=self.visual_checkbox_var)
        self.visual_checkbox.pack(side=tk.LEFT, padx=5)

        self.console_checkbox_var = tk.BooleanVar()
        self.console_checkbox = tk.Checkbutton(self.frame4, text="Console",
                                               variable=self.console_checkbox_var)
        self.console_checkbox.pack(side=tk.LEFT, padx=5)

        self.number_of_games_entry_label = tk.Label(self.frame4, text="Number of Games: ")
        self.number_of_games_entry_label.pack(side=tk.LEFT, padx=5)
        self.number_of_games_entry = tk.Entry(self.frame4, width=5)
        self.number_of_games_entry.pack(side=tk.LEFT, padx=5)
        self.number_of_games_entry.insert(0, "50")

        self.start_buttons_frame = tk.Frame(self.upper_frame)
        self.start_buttons_frame.pack(fill=tk.X, pady=5)

        # Add buttons to the left column
        self.start_button = tk.Button(self.start_buttons_frame, text="Start All Games", command=self.controller.start_games)
        self.start_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.stop_button = tk.Button(self.start_buttons_frame, text="Stop All Games", command=self.controller.stop_games,
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.stop_selected_button = tk.Button(self.start_buttons_frame, text="Stop Selected Games",
                                              command=self.controller.stop_selected_process)
        self.stop_selected_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Loop Başlat/Durdur Butonları
        self.loop_running = False  # Loop durumu takibi için

        self.loop_button = tk.Button(self.start_buttons_frame, text="Start Loop", command=self.start_loop_games)
        self.loop_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.stop_loop_button = tk.Button(self.start_buttons_frame, text="Stop Loop", command=self.stop_loop_games,
                                          state=tk.DISABLED)
        self.stop_loop_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Listbox Frames
        self.lower_frame = tk.Frame(self.left_column, bd=4, relief="groove")
        self.lower_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.double_list_frame = tk.Frame(self.lower_frame)
        self.double_list_frame.pack(fill=tk.X, pady=5)

        self.listbox_frame1 = tk.Frame(self.double_list_frame)
        self.listbox_frame1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)

        self.processes_label = tk.Label(self.listbox_frame1, text="Game Processes")
        self.processes_label.pack(side=tk.TOP, fill=tk.X, padx=5)

        self.refresh_processes_button = tk.Button(self.listbox_frame1, text="Refresh", command=self.controller.update_process_listbox)
        self.refresh_processes_button.pack(side=tk.TOP, padx=10, fill=tk.X)

        self.processes_listbox = tk.Listbox(self.listbox_frame1, height=15)
        self.processes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.listbox_frame2 = tk.Frame(self.double_list_frame)
        self.listbox_frame2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)

        self.log_files_label = tk.Label(self.listbox_frame2, text="Current Games Logs")
        self.log_files_label.pack(side=tk.TOP, fill=tk.X, padx=5)

        self.refresh_log_files_button = tk.Button(self.listbox_frame2, text="Refresh", command=lambda: self.controller.populate_log_files("logs"))
        self.refresh_log_files_button.pack(side=tk.TOP, padx=10, fill=tk.X)

        self.log_files_listbox = tk.Listbox(self.listbox_frame2, height=15)
        self.log_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.listbox_frame3 = tk.Frame(self.lower_frame)
        self.listbox_frame3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_label = tk.Label(self.listbox_frame3, text="History")
        self.history_label.pack(side=tk.TOP, fill=tk.BOTH, padx=5)

        self.refresh_history_button = tk.Button(self.listbox_frame3, text="Refresh", command=lambda: self.controller.populate_history_files("logs/history"))
        self.refresh_history_button.pack(side=tk.TOP, padx=10, fill=tk.X)

        self.history_listbox = tk.Listbox(self.listbox_frame3)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)


    def create_right_column(self):
        # Treeview widget for agents general performance

        self.general_info_frame = tk.Frame(self.right_column, bd=4, relief="groove")
        self.general_info_frame.pack(fill=tk.X, pady=5, padx=5)

        text_and_refresh_button_frame = tk.Frame(self.general_info_frame)
        text_and_refresh_button_frame.pack()

        self.agent_status_label = tk.Label(text_and_refresh_button_frame, text="Agents' Status")
        self.agent_status_label.pack(side=tk.LEFT)

        self.refresh_general_info = tk.Button(text_and_refresh_button_frame, text="Refresh", command=self.controller.refresh_game_summaries)
        self.refresh_general_info.pack(side=tk.LEFT, padx=5, pady=5)

        columns = ("Agent Type", "Agent Color", "Total Points", "Total Wins", "Total Longest Route", "Total Cars Spent", "Total Turn Played", "Total Time Played")
        self.tree_general_players_info = ttk.Treeview(self.general_info_frame, columns=columns, show="headings", height=5)

        self.tree_general_players_info.heading("Agent Type", text="Agent Type")
        self.tree_general_players_info.heading("Agent Color", text="Agent Color")
        self.tree_general_players_info.heading("Total Points", text="Total Points")
        self.tree_general_players_info.heading("Total Wins", text="Total Wins")
        self.tree_general_players_info.heading("Total Longest Route", text="Total Longest Route")
        self.tree_general_players_info.heading("Total Cars Spent", text="Total Cars Spend")
        self.tree_general_players_info.heading("Total Turn Played", text="Total Turn Played")
        self.tree_general_players_info.heading("Total Time Played", text="Total Time Played")

        self.tree_general_players_info.column("Agent Type", width=70)
        self.tree_general_players_info.column("Agent Color", width=70)
        self.tree_general_players_info.column("Total Points", width=70)
        self.tree_general_players_info.column("Total Wins", width=70)
        self.tree_general_players_info.column("Total Longest Route", width=100)
        self.tree_general_players_info.column("Total Cars Spent", width=100)
        self.tree_general_players_info.column("Total Turn Played", width=100)
        self.tree_general_players_info.column("Total Time Played", width=100)

        self.tree_general_players_info.pack(side=tk.TOP, fill=tk.X, padx=5)

        # Treeview widget for game summaries
        self.summaries_frame = tk.Frame(self.general_info_frame)
        self.summaries_frame.pack(fill=tk.X)

        self.summaries_label = tk.Label(self.summaries_frame, text="Summaries of the Games")
        self.summaries_label.pack()
        columns = ("Game Name","Player Amount", "Winner", "Longest Route", "Turns Played", "Time Played")
        self.tree_game_summaries = ttk.Treeview(self.summaries_frame, columns=columns, show="headings", height=8)
        self.tree_game_summaries.heading("Game Name", text="Game Name")
        self.tree_game_summaries.heading("Player Amount", text="Player Amount")
        self.tree_game_summaries.heading("Winner", text="Winner")
        self.tree_game_summaries.heading("Longest Route", text="Longest Route")
        self.tree_game_summaries.heading("Turns Played", text="Turns Played")
        self.tree_game_summaries.heading("Time Played", text="Time Played")

        self.tree_game_summaries.column("Game Name", width=100)
        self.tree_game_summaries.column("Player Amount", width=100)
        self.tree_game_summaries.column("Winner", width=100)
        self.tree_game_summaries.column("Longest Route", width=150)
        self.tree_game_summaries.column("Turns Played", width=100)
        self.tree_game_summaries.column("Time Played", width=100)

        self.tree_game_summaries.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=(0,5))
        self.tree_scrollbar = ttk.Scrollbar(self.summaries_frame, orient="vertical",command=self.tree_game_summaries.yview)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0,5))
        self.tree_game_summaries.configure(yscrollcommand=self.tree_scrollbar.set)

        self.analysis_frame = tk.Frame(self.general_info_frame)
        self.analysis_frame.pack()

        self.mean_of_points_label = tk.Label(self.analysis_frame, text="Mean of Points:")
        self.mean_of_points_label.pack(side=tk.LEFT, padx=5)

        self.std_dev_of_points_label = tk.Label(self.analysis_frame, text="Standard Deviation of Points:")
        self.std_dev_of_points_label.pack(side=tk.LEFT, padx=5)

        self.most_winner_label = tk.Label(self.analysis_frame, text="Most Winner:")
        self.most_winner_label.pack(side=tk.LEFT, padx=5)

        self.most_longest_route_label = tk.Label(self.analysis_frame, text="Most Longest Route Achiever:")
        self.most_longest_route_label.pack(side=tk.LEFT, padx=5)

        # Placeholder for right column content
        self.details_frame = tk.Frame(self.right_column, bd=4, relief="groove")
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.right_label = tk.Label(self.details_frame, text="Game Details")
        self.right_label.pack()

        # Treeview Widged
        columns = ("Name", "Color", "Points", "Cars")
        self.tree_players_info = ttk.Treeview(self.details_frame, columns=columns, show="headings", height=5)

        self.tree_players_info.heading("Name", text="Player Name")
        self.tree_players_info.heading("Color", text="Player Color")
        self.tree_players_info.heading("Points", text="Player Points")
        self.tree_players_info.heading("Cars", text="Player Cars")

        self.tree_players_info.column("Name", width=100)
        self.tree_players_info.column("Color", width=100)
        self.tree_players_info.column("Points", width=100)
        self.tree_players_info.column("Cars", width=100)

        self.tree_players_info.pack(fill=tk.X, padx=10, pady=5)

        self.text_frame = tk.Frame(self.details_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_content_listbox = tk.Listbox(self.text_frame, yscrollcommand=self.scrollbar.set)
        self.log_content_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.log_content_listbox.yview)





    def update_display_timer(self):
        """Call display_log_file_content every 2 seconds if an item is selected."""
        # Timer'ı tekrar başlat
        self.root.after(2000, self.update_display_timer)
        selected_index = self.log_files_listbox.curselection()
        if selected_index:
            # Çağrı yapılması gereken item varsa
            self.controller.update_tree_players_info()

    def update_analysis_labels(self, mean_points, std_dev_points, most_winner, most_longest_route):
        """Update the analysis labels with the provided data."""
        self.mean_of_points_label.config(text=f"Mean of Points: {mean_points:.2f}")
        self.std_dev_of_points_label.config(text=f"Standard Deviation of Points: {std_dev_points:.2f}")
        self.most_winner_label.config(text=f"Most Winner: {most_winner}")
        self.most_longest_route_label.config(text=f"Most Longest Route Achiever: {most_longest_route}")

    def reset_dropdown(self):
        print("Resetting dropdown...")
        self.available_colors = ["Red", "Blue", "Green", "Yellow", "Black"]
        self.color_dropdown["values"] = self.available_colors
        self.color_var.set("")
        self.color_dropdown.update_idletasks()

    def start_loop_games(self):
        """Oyunları sürekli olarak başlatan loop fonksiyonu."""
        if not self.loop_running:
            global_vars.test_count = int(self.number_of_games_entry.get()) - 1
            self.loop_running = True
            self.loop_button.config(state=tk.DISABLED)
            self.stop_loop_button.config(state=tk.NORMAL)
            self.run_game_loop()

    def stop_loop_games(self):
        """Loop'u durduran fonksiyon."""
        self.loop_running = False
        self.loop_button.config(state=tk.NORMAL)
        self.stop_loop_button.config(state=tk.DISABLED)
    
    def run_game_loop(self):
        """Loop aktifken sürekli oyun başlatır."""
        if self.loop_running:
            self.loop_count+=1
            print(f"Games are running: {self.loop_count} times this func called -", self.controller.are_games_running())
            if self.loop_count==1000:
                self.controller.stop_games()
            elif not self.controller.are_games_running():
                self.loop_count=0
                self.controller.start_games()
            self.root.after(1000, self.run_game_loop)
