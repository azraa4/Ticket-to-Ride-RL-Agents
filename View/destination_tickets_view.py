import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class DestinationTicketsFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.destination_scroll_frame = None
        self.canvas = None

    def create_destination_tickets_frame(self):
        destination_tickets_frame = tk.Frame(self.root, width=250, height=100, bg="#fdf8ed",
                                          highlightthickness=4, highlightbackground="#e4a21d")
        destination_tickets_frame.place(x=0, y=470)

        canvas_for_text = tk.Canvas(destination_tickets_frame, bg="#fdf8ed", width=230, height=20)
        canvas_for_text.place(x=0, y=0)
        canvas_for_text.create_text(5, 5, anchor="nw", text="Destination Tickets", fill="black",
                                    font=("Helvetica", 10, "bold"))

        self.canvas = tk.Canvas(destination_tickets_frame, bg="#fdf8ed", width=225, height=80)
        self.canvas.place(x=0, y=20)
        scrollbar = tk.Scrollbar(destination_tickets_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.place(x=225, y=20, height=80)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.update_destination_tickets_frame()

    def clear_destination_tickets_frame(self):
        # Remove all items from within the canvas, keeping the scrollbar intact
        if self.destination_scroll_frame is not None:
            for widget in self.destination_scroll_frame.winfo_children():
                widget.destroy()

    def update_destination_tickets_frame(self):
        # Clear any existing items in the canvas
        self.clear_destination_tickets_frame()

        # Create a new frame within the canvas to hold the tickets, if it doesn't already exist
        self.destination_scroll_frame = tk.Frame(self.canvas, bg="#fdf8ed")
        self.canvas.create_window((0, 0), window=self.destination_scroll_frame, anchor="nw")

        # Retrieve the list of destination tickets for the current player
        destination_tickets_list = self.controller.get_current_player_destination_tickets()

        # Populate the scrollable frame with each destination ticket
        for ticket in destination_tickets_list:
            city1 = ticket.city1
            city2 = ticket.city2
            points = ticket.points
            completed = ticket.is_completed

            # Format the ticket information
            ticket_text = f"{city1} to {city2} - {points} pts"
            if completed:
                ticket_text += " (Completed)"

            # Add the ticket text to the scrollable frame
            label = tk.Label(self.destination_scroll_frame, text=ticket_text, bg="#fdf8ed",
                             font=("Helvetica", 9), anchor="w")
            label.pack(fill="x", padx=5, pady=2)

        # Update scroll region based on the contents
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))




