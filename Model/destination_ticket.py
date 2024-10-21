class DestinationTicket:
    def __init__(self, city1, city2, points, ticket_id):
        self.city1 = city1
        self.city2 = city2
        self.points = points
        self.is_completed = False  # Biletin tamamlanıp tamamlanmadığını izlemek için bir bayrak
        self.image_path = f"../Assets/DestinationTickets/destcard_{ticket_id}.png"  # Görsel yolu

    def mark_as_completed(self):
        """Biletin tamamlandığını işaretler."""
        self.is_completed = True

    def __repr__(self):
        return f"DestinationTicket({self.city1} to {self.city2}, {self.points} points)"
