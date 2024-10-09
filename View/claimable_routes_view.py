import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class ClaimableRoutesFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

    def create_claimable_routes_frame(self):
        claimable_routes_frame = tk.Frame(self.root, width=240, height=150, bg="#fdf8ed",
                                          highlightthickness=4, highlightbackground="#e4a21d")
        claimable_routes_frame.place(x=0, y=570)

        canvas_for_text = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=240, height=20)
        canvas_for_text.place(x=0, y=0)
        canvas_for_text.create_text(5, 5, anchor="nw", text="Claimable Routes", fill="black",
                                    font=("Helvetica", 10, "bold"))

        canvas = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=220, height=130)
        canvas.place(x=0, y=20)
        scrollbar = tk.Scrollbar(claimable_routes_frame, orient="vertical", command=canvas.yview)
        scrollbar.place(x=220, y=20, height=130)
        canvas.configure(yscrollcommand=scrollbar.set)

        buttons_frame = tk.Frame(canvas, bg="#fdf8ed")
        canvas.create_window((0, 0), window=buttons_frame, anchor="nw")

        for i in range(10):
            button = tk.Button(buttons_frame, text=f"Button {i + 1}", width=20)
            button.pack(pady=2)

        buttons_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))