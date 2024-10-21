import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class MainMenu:
    def __init__(self, root, controller, start_game_callback):
        self.root = root
        self.controller = controller
        self.start_game_callback = start_game_callback
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True)

    def create_menu(self):
        title = tk.Label(self.frame, text="Main Menu", font=("Helvetica", 24))
        title.pack(pady=20)

        self.create_add_player_section()

        start_button = tk.Button(self.frame, text="Start Game", font=("Helvetica", 18), command=self.start_game)
        start_button.pack(pady=20)

    def create_add_player_section(self):
        add_player_label = tk.Label(self.frame, text="Add Player", font=("Helvetica", 18))
        add_player_label.pack(pady=10)

        self.player_name_var = tk.StringVar()
        player_name_label = tk.Label(self.frame, text="Player Name:", font=("Helvetica", 14))
        player_name_label.pack(pady=5)
        player_name_entry = tk.Entry(self.frame, textvariable=self.player_name_var, font=("Helvetica", 14))
        player_name_entry.pack(pady=5)


        self.color_var = tk.StringVar(value="Select a color")
        color_label = tk.Label(self.frame, text="Select Color:", font=("Helvetica", 14))
        color_label.pack(pady=5)
        color_options = ["Red", "Blue", "Green", "Yellow", "Black"]
        color_dropdown = tk.OptionMenu(self.frame, self.color_var, *color_options)
        color_dropdown.pack(pady=5)

        add_player_button = tk.Button(self.frame, text="Add Player", font=("Helvetica", 14), command=self.add_player)
        add_player_button.pack(pady=10)

    def add_player(self):
        player_name = self.player_name_var.get()
        selected_color = self.color_var.get()
        print(f"Player Added: {player_name} with color {selected_color}")
        self.controller.add_player_button(player_name, selected_color)

    def start_game(self):
        self.frame.pack_forget()
        self.start_game_callback()
