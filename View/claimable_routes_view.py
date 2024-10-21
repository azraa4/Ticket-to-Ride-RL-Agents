import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class ClaimableRoutesFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.buttons_frame = None
        self.canvas = None

    def create_claimable_routes_frame(self):
        claimable_routes_frame = tk.Frame(self.root, width=240, height=150, bg="#fdf8ed",
                                          highlightthickness=4, highlightbackground="#e4a21d")
        claimable_routes_frame.place(x=0, y=570)

        canvas_for_text = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=240, height=20)
        canvas_for_text.place(x=0, y=0)
        canvas_for_text.create_text(5, 5, anchor="nw", text="Claimable Routes", fill="black",
                                    font=("Helvetica", 10, "bold"))

        self.canvas = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=220, height=130)
        self.canvas.place(x=0, y=20)
        scrollbar = tk.Scrollbar(claimable_routes_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.place(x=220, y=20, height=130)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.update_routes_frame()



    def clear_routes_frame(self):
        if self.buttons_frame is not None:
            self.buttons_frame.destroy()

    def update_routes_frame(self):
        self.clear_routes_frame()

        self.buttons_frame = tk.Frame(self.canvas, bg="#fdf8ed")
        self.canvas.create_window((0, 0), window=self.buttons_frame, anchor="nw")

        i = 0
        for route in self.controller.get_claimable_routes():
            route_label = tk.Label(self.buttons_frame, text=f"{route.city1} - {route.city2}", bg="#fdf8ed")
            route_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            claim_button = tk.Button(self.buttons_frame, text="Claim",
                                     command=lambda r=route: self.controller.claim_route(r))
            claim_button.grid(row=i, column=1, padx=5, pady=2)

            i += 1

        self.buttons_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

