import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui
class HeaderInfo:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

    def create_header_info_frame(self):
        header_info_canvas = tk.Canvas(self.root, width=1288, height=40, bg="#fdf8ed",
                                       highlightthickness=4, highlightbackground="#e4a21d")
        header_info_canvas.place(x=-4, y=-4)

        header_info_canvas.create_text(20, 24, text="Turn: ", font=("Arial", 14), fill="#c0954a", anchor="w")
        header_info_canvas.create_text(250, 24, text="Players Info: ", font=("Arial", 14), fill="#c0954a", anchor="w")
