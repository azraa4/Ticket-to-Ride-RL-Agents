import tkinter as tk
from PIL import Image, ImageTk
from View.ttr_gui_view import TTRGui

class HeaderInfo:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.header_info_canvas = None
        self.turn_text_id = None
        self.players_info_text_id = None
        self.all_players_info_text_id = None

    def create_header_info_frame(self):
        self.header_info_canvas = tk.Canvas(self.root, width=1288, height=40, bg="#fdf8ed",
                                            highlightthickness=4, highlightbackground="#ae2907")
        self.header_info_canvas.place(x=-4, y=-4)

        # Create the text elements and save their IDs
        self.turn_text_id = self.header_info_canvas.create_text(20, 24, text="Turn: ", font=("Arial", 14), fill="#ae2907", anchor="w")
        self.players_info_text_id = self.header_info_canvas.create_text(100, 24, text="Player Info: ", font=("Arial", 14), fill="#ae2907", anchor="w")
        self.all_players_info_text_id = self.header_info_canvas.create_text(1260, 24, text="Players: ", font=("Arial", 14), fill="#ae2907", anchor="e")

    def update_turn_text(self, new_text):
        if not self.controller.visualize:  # optimization
            return

        """Update the 'Turn' text."""
        if self.turn_text_id:
            self.header_info_canvas.itemconfig(self.turn_text_id, text=new_text)

    def update_player_info_text(self, new_text):
        if not self.controller.visualize:  # optimization
            return

        """Update the 'Players Info' text."""
        if self.players_info_text_id:
            self.header_info_canvas.itemconfig(self.players_info_text_id, text=new_text)

    def update_players_info_text(self, new_text):
        if not self.controller.visualize:  # optimization
            return

        """Update the 'Players Info' text."""
        if self.all_players_info_text_id:
            self.header_info_canvas.itemconfig(self.all_players_info_text_id, text=new_text)
