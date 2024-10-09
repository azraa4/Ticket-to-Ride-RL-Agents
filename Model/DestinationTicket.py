import tkinter as tk

class DestinationTicket:
    def __init__(self, start_city, end_city, points, root=None):
        self.start_city = start_city
        self.end_city = end_city
        self.points = points
        self.completed = False
        self.label = None
        if root:
            self.create_label(root)

    def create_label(self, root):
        # Tkinter Label oluştur
        ticket_text = f"{self.start_city} to {self.end_city} ({self.points} pts)"
        self.label = tk.Label(root, text=ticket_text)
        self.label.pack()

    def check_completion(self, player_routes):
        # Bu rotanın tamamlanıp tamamlanmadığını kontrol et
        if (self.start_city, self.end_city) in player_routes or (self.end_city, self.start_city) in player_routes:
            self.completed = True
        else:
            self.completed = False
        return self.completed

    def __str__(self):
        return f"Ticket: {self.start_city} to {self.end_city}, {self.points} pts"
