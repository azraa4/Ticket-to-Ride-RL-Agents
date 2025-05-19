import random
import global_vars

class Deck:
    def __init__(self, cards):
        random.seed(global_vars.random_seed())
        self.cards = cards
        random.shuffle(cards)
        #print(cards)
        #print(len(cards))

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