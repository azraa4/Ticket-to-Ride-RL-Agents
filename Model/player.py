class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.points = 0
        self.train_cards = []
        self.destination_tickets = []
        self.claimed_routes = []

    def add_train_card(self, train_card):
        self.train_cards.append(train_card)

    def add_destination_ticket(self, destination_ticket):
        self.destination_tickets.append(destination_ticket)

    def get_number_of_cards(self, color):
        num = 0
        for train_card in self.train_cards:
            if train_card.color == color:
                num = num + 1
        return num

    def remove_card_according_to_color(self, color, amount_to_delete):
        num = amount_to_delete
        print(self.train_cards)
        print(len(self.train_cards))
        copy_of_train_cards_list = self.train_cards[:]
        for train_card in copy_of_train_cards_list:
            if color == train_card.color and num!=0:
                self.train_cards.remove(train_card)
                num -=1
