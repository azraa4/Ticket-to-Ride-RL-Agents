import tkinter as tk
from PIL import Image, ImageTk

class TTRGui:
    @staticmethod
    def create_modern_button(parent, text, x, y, width=10, height=2, font=12):
        colour1 = "#c0954a"
        colour2 = "#c0954a"
        colour3 = "#d28840"
        colour4 = "#ffffff"

        button = tk.Button(
            parent,
            background=colour1,
            foreground=colour4,
            activebackground=colour3,
            activeforeground=colour4,
            highlightthickness=2,
            highlightbackground=colour2,
            highlightcolor="WHITE",
            width=width,
            height=height,
            border=0,
            cursor='hand1',
            text=text,
            font=('Arial', font, 'bold')
        )
        button.place(x=x, y=y)
        return button
