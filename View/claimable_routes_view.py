import tkinter as tk
from PIL import Image, ImageTk
from View.ttr_gui_view import TTRGui
from View.modern_button import ModernButton

class ClaimableRoutesFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.buttons_frame = None
        self.canvas = None
        # StringVar to hold the search text
        self.search_var = tk.StringVar()

    def create_claimable_routes_frame(self):
        claimable_routes_frame = tk.Frame(self.root, width=238, height=175, bg="#fdf8ed",
                                          highlightthickness=4, highlightbackground="#ae2907")
        claimable_routes_frame.place(x=-4, y=540)

        # Title
        canvas_for_text = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=234, height=20)
        canvas_for_text.place(x=-4, y=0)
        canvas_for_text.create_text(5, 5, anchor="nw", text="Claimable Routes", fill="#ae2907",
                                    font=("Helvetica", 10, "bold"))

        # Search bar
        search_entry = tk.Entry(claimable_routes_frame, textvariable=self.search_var, width=35,
                                font=("Arial", 8))
        search_entry.place(x=5, y=30)
        search_entry.insert(0, "Search...")
        # Clear placeholder on focus
        def on_focus_in(event):
            if search_entry.get() == "Search...":
                search_entry.delete(0, tk.END)
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Search...")
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)

        # Ensure clicks outside the entry shift focus away and trigger on_focus_out
        def on_click_anywhere(event):
            if event.widget is not search_entry:
                claimable_routes_frame.focus_set()

        self.root.bind_all('<Button-1>', on_click_anywhere)

        # Trigger update on text change
        self.search_var.trace('w', lambda *args: self.update_routes_frame())

        # Canvas for list
        self.canvas = tk.Canvas(claimable_routes_frame, bg="#fdf8ed", width=214, height=120)
        self.canvas.place(x=-4, y=55)
        scrollbar = tk.Scrollbar(claimable_routes_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.place(x=214, y=55, height=120)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Populate initial list
        self.update_routes_frame()

    def clear_routes_frame(self):
        if self.buttons_frame is not None:
            self.buttons_frame.destroy()

    def update_routes_frame(self):
        if not self.controller.visualize:
            return

        # Get search text and filter routes
        search_text = self.search_var.get().lower()

        self.clear_routes_frame()
        self.buttons_frame = tk.Frame(self.canvas, bg="#fdf8ed")
        self.canvas.create_window((0, 0), window=self.buttons_frame, anchor="nw")

        i = 0
        for route in self.controller.get_claimable_routes():
            label_text = f"{route.city1}-{route.city2},{route.color}"
            if search_text and search_text != "search...":
                if search_text not in label_text.lower():
                    continue

            route_label = tk.Label(self.buttons_frame, text=label_text, bg="#fdf8ed", font=("Arial", 8))
            route_label.grid(row=i, column=0, padx=0, pady=2, sticky="w")

            if not self.controller.selecting_second_train_card:
                claim_button = ModernButton(self.buttons_frame, text="Claim", font_size=9, width=5, height=1,
                                             command=lambda r=route: self.controller.claim_route(r))
                claim_button.grid(row=i, column=1, padx=0, pady=2)

            i += 1

        self.buttons_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
