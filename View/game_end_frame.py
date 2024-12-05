import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
from ttr_gui_view import TTRGui
from modern_button import ModernButton
class GameEndFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.game_end_frame = None
        self.info = {"winner": "Name", "players": [], "turn played": 0, "player has longest road": "Name"}


    def create_game_end_frame(self, info=None):
        if info is not None:
            self.info = info
        if not self.game_end_frame:
            self.game_end_frame = tk.Frame(self.root, width=1280, height=720, bg="black")
            self.game_end_frame.pack(expand=True, fill="both")

            # Arka plan resmi ayarla
            self.background_image = Image.open("../Assets/end_background.jpg")
            self.background_photo = ImageTk.PhotoImage(self.background_image)
            self.background_label = tk.Label(self.game_end_frame, image=self.background_photo)
            self.background_label.place(relwidth=1, relheight=1)

            # Winner frame
            winner = self.info["winner"]

            if winner != "Name":
                winner_label = tk.Label(
                    self.game_end_frame,
                    text=f"THE WINNER IS:{winner.name}",
                    font=("Arial", 25, "bold"),
                    fg="#ae2907",
                    bg="#d5b570"
                )
                winner_label.pack(pady=(220,0))

            players_label = tk.Label(
                self.game_end_frame,
                text=f"Players:",
                font=("Arial", 20, "bold"),
                fg="#ae2907",
                bg="#d5b570"
            )
            players_label.pack(pady=(10, 0))

            players = self.info["players"]
            if len(players) != 0:
                for player in players:
                    if player.longest_road == True:
                        text = f"{player.name} ({player.color}) has {player.points} points with longest road."
                    else:
                        text = f"{player.name} ({player.color}) has {player.points} points."

                    player_label = tk.Label(self.game_end_frame,
                        text=text,
                        font=("Arial", 20, "bold"),
                        fg="#ae2907",
                        bg="#d5b570"
                    )
                    player_label.pack(pady=(10, 0))

            turn_played = self.info["turn played"]
            turn_played_label = tk.Label(
                self.game_end_frame,
                text=f"Turn Played: {turn_played}",
                font=("Arial", 20, "bold"),
                fg="#ae2907",
                bg="#d5b570"
            )
            turn_played_label.pack(pady=(20, 0))

            # Add Quit Button
            quit_button = ModernButton(
                self.game_end_frame,
                text="Quit",
                command=self.quit_game,
                font_size=20
            )
            quit_button.pack(pady=20)

        self.game_end_frame.place(x=0, y=0, relwidth=1, relheight=1)

    def quit_game(self):
        #self.root.quit()
        print("this will quit the game")