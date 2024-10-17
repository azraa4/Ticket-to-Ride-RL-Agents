import random
from Model.TrainCard import TrainCard
from Model.DestinationTicket import DestinationTicket

class Deck:
    def __init__(self):
        # TrainCard objelerinin listesi
        self.train_cards = [TrainCard(color) for color in ["blue", "red", "green", "orange", "yellow", "white", "black", "pink", "joker"]] * 12
        random.shuffle(self.train_cards)

        # DestinationTicket objelerinin listesi (ID'ler görsellerle eşleşiyor)
        self.destination_tickets = [
            DestinationTicket("New York", "Los Angeles", 21, "01"),
            DestinationTicket("Chicago", "New Orleans", 7, "02"),
            DestinationTicket("San Francisco", "Atlanta", 17, "03"),
            DestinationTicket("Boston", "Miami", 12, "04"),
            DestinationTicket("Seattle", "Denver", 9, "05"),
            # Diğer biletler...
        ]
        random.shuffle(self.destination_tickets)

    def shuffle(self):
        """Tren kartları ve destination ticket destelerini karıştır"""
        random.shuffle(self.train_cards)
        random.shuffle(self.destination_tickets)

    def draw_train_card(self):
        if len(self.train_cards) > 0:
            return self.train_cards.pop(0)
        return None

    def draw_destination_ticket(self):
        if len(self.destination_tickets) > 0:
            return self.destination_tickets.pop(0)
        return None
