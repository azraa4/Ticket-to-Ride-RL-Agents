class GameManager:
    def __init__(self, players, board, deck):
        self.players = players
        self.board = board
        self.deck = deck
        self.current_turn = 0
        self.claimed_routes = []
        self.face_up_cards = []

    def start_game(self):
        self.deck.shuffle()
        for player in self.players:
            for _ in range(4):
                card = self.deck.draw_train_card()
                if card:
                    player.add_train_card(card)
            print(f"{player.name} has been dealt 4 train cards.")

        for _ in range(5):
            card = self.deck.draw_train_card()
            if card:
                self.face_up_cards.append(card)

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % len(self.players)

    def get_current_player(self):
        return self.players[self.current_turn]

    def claim_route(self, route_id, player_name):
        """Bir rotayı talep etme işlemi"""
        player = self.get_player_by_name(player_name)  # Oyuncu adını alıyoruz
        route = self.board.get_route_by_id(route_id)
        if route and not route.claimed_by:  # Rota talep edilmemişse
            if player.claim_route(route, {"blue": route.length}):  # Örnek olarak mavi kart gerekiyor
                route.claimed_by = player_name
                route.claimed_color = player.color
                self.claimed_routes.append(route)
                return True
        return False

    def get_player_by_name(self, name):
        """Oyuncuyu isme göre bulur"""
        for player in self.players:
            if player.name == name:
                return player
        return None

    def draw_train_card(self, card_number=None):
        current_player = self.get_current_player()
        if card_number is not None and card_number < len(self.face_up_cards):
            card = self.face_up_cards.pop(card_number)
            self.face_up_cards.append(self.deck.draw_train_card())
        else:
            card = self.deck.draw_train_card()

        if card:
            current_player.add_train_card(card)

    def draw_destination_ticket(self):
        current_player = self.get_current_player()
        ticket = self.deck.draw_destination_ticket()
        if ticket:
            current_player.add_destination_ticket(ticket)

    def update_train_numbers(self):
        current_player = self.get_current_player()
        card_colors = [card.color for card in current_player.train_cards]
        return {color: card_colors.count(color) for color in set(card_colors)}

