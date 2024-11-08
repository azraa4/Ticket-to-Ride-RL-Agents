import random


class Deck:
    def __init__(self, cards):
        self.cards = cards
        random.shuffle(cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if len(self.cards) > 0:
            return self.cards.pop(0)
        return None

    def is_empty(self):
        return len(self.cards) == 0

    def get_length(self):
        return len(self.cards)