import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
from ttr_gui_view import TTRGui
class GameEndFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.game_end_frame = None

    def create_game_end_frame(self):
        if not self.game_end_frame:
            self.game_end_frame = tk.Frame(self.root, width=1280, height=720, bg="black")

            # Add "Game End" Label
            game_end_label = tk.Label(
                self.game_end_frame,
                text="Game End",
                font=("Arial", 36),
                fg="white",
                bg="black"
            )
            game_end_label.pack(pady=100)

            # Add Quit Button
            quit_button = tk.Button(
                self.game_end_frame,
                text="Quit",
                font=("Arial", 24),
                bg="red",
                fg="white",
                command=self.quit_game
            )
            quit_button.pack(pady=20)

        self.game_end_frame.place(x=0, y=0, relwidth=1, relheight=1)

    def quit_game(self):
        #self.root.quit()
        print("this will quit the game")