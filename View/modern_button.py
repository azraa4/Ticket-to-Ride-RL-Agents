import tkinter as tk

class ModernButton(tk.Button):
    def __init__(self, parent, text, width=10, height=2, font_size=12, **kwargs):
        super().__init__(
            parent,
            background="#ae2907",
            foreground="#ffffff",
            activebackground="#841804",
            activeforeground="#ffffff",
            highlightthickness=2,
            highlightbackground="#d9390a",
            highlightcolor="white",
            width=width,
            height=height,
            border=0,
            cursor='hand1',
            text=text,
            font=('Arial', font_size, 'bold'),
            **kwargs
        )


