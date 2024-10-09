import random

class Deck:
    def __init__(self, cards):
        self.cards = cards
        self.discard_pile = []

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1):
        drawn_cards = []
        for _ in range(count):
            if len(self.cards) > 0:
                drawn_cards.append(self.cards.pop())
        return drawn_cards

    def draw_face_up_card(self, face_up_cards, index):
        # Eğer kart jokerse, oyuncu sadece bir kart alabilir
        card = face_up_cards[index]
        if card.is_locomotive():
            # Yüzü açık kartlar değişmeli mi?
            if len([c for c in face_up_cards if c.is_locomotive()]) >= 3:
                self.discard_pile.extend(face_up_cards)
                return self.draw_new_face_up_cards(5)
        return card

    def draw_new_face_up_cards(self, num=5):
        return [self.draw()[0] for _ in range(num)]

    def reshuffle_discard_pile(self):
        # Eğer deste biterse, discard pile (atma destesi) karıştırılıp yeniden deste yapılır
        self.cards.extend(self.discard_pile)
        self.shuffle()
        self.discard_pile.clear()

    def return_card_to_deck(self, card):
        # Kartı destenin altına geri koy
        self.cards.insert(0, card)
