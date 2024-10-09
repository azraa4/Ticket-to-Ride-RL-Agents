from Model.DestinationTicket import DestinationTicket
from Model.TrainCard import TrainCard
from Model.Deck import Deck

class GameManager:
    def __init__(self):
        self.train_deck = None
        self.destination_ticket_deck = None

    def setup_game(self):
        # 110 Train Cards (12 each of 8 types, 14 Locomotives)
        train_cards = []
        for color in TrainCard.COLORS:
            for _ in range(12):
                train_cards.append(TrainCard(color=color, image=None))  # Gerçek image'i buraya ekleyebilirsiniz

        for _ in range(14):
            train_cards.append(TrainCard(color=TrainCard.LOCOMOTIVE, image=None))

        # 30 Destination Tickets
        destination_tickets = [
            DestinationTicket("Los Angeles", "New York", 21),
            DestinationTicket("San Francisco", "Chicago", 16),
            DestinationTicket("Denver", "Miami", 15),
            # Gerçek biletleri eklemeye devam edin
        ]

        # Desteleri oluştur ve karıştır
        self.train_deck = Deck(train_cards)
        self.destination_ticket_deck = Deck(destination_tickets)

        self.train_deck.shuffle()
        self.destination_ticket_deck.shuffle()

    def start_game(self):
        # Oyunu başlatma kodları buraya gelecek
        print("Game Started!")
        print(f"Train deck has {len(self.train_deck.cards)} cards.")
        print(f"Destination ticket deck has {len(self.destination_ticket_deck.cards)} cards.")
