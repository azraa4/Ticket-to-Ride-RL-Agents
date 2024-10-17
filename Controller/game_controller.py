"""
from Model.Deck import Deck

class GameController:
    def __init__(self, view, board, players):
        self.view = view
        self.board = board
        self.players = players  # Oyuncuları ekledik
        self.deck = Deck()  # Kartları yöneten Deck sınıfını ekledik
        self.current_player_index = 0

    def get_unclaimed_routes(self):
        return self.board.get_unclaimed_routes()

    def get_claimed_routes(self):
        return self.board.get_claimed_routes()

    def claim_route(self, id, player_name):  # player şimdilik bir string sonra player objesi olacak
        print("claimed")
        unclaimed_routes = self.board.get_unclaimed_routes()
        for route in unclaimed_routes:
            if route.id == id:
                route.claimed_by = player_name
                route.claimed_color = "blue"
        self.view.main_frame.create_roads()

    def draw_train_card(self, card_number):
        current_player = self.players[self.current_player_index]  # Şu anki oyuncuyu al
        if card_number <= len(self.deck.train_cards):
            card = self.deck.draw_train_card()
            if card:
                current_player.add_train_card(card)
                print(f"{current_player.name} drew a {card.color} train card.")
                # Yüzü açık kartları güncelle
                self.view.train_cards.update_train_card_selection_frame()

    def draw_destination_ticket(self):
        current_player = self.players[self.current_player_index]
        ticket = self.deck.draw_destination_ticket()
        if ticket:
            current_player.add_destination_ticket(ticket)
            print(f"{current_player.name} drew a destination ticket: {ticket.city1} to {ticket.city2}")
            self.view.destination_tickets.update_destination_ticket_frame()

    def blind_pick(self):
        current_player = self.players[self.current_player_index]
        card = self.deck.draw_train_card()  # Kapalı bir kart çekiyoruz
        if card:
            current_player.add_train_card(card)
            print(f"Player {current_player.name} drew a blind {card.color} train card.")
            # Yüzü kapalı kartları GUI'de güncelle
            self.view.train_cards.update_train_card_selection_frame()

    def update_train_numbers(self):
        current_player = self.players[self.current_player_index]  # Sadece şu anki oyuncunun kart sayısını güncelle
        train_card_counts = {color: current_player.get_train_card_count(color) for color in
                             ["blue", "red", "green", "orange", "yellow", "white", "black", "pink", "joker"]}
        self.view.main_frame.update_train_numbers(train_card_counts)

"""


class GameController:
    def __init__(self, view, game_manager):
        self.view = view
        self.game_manager = game_manager

    def get_unclaimed_routes(self):
        """Talep edilmemiş rotaları GameManager'dan al"""
        return self.game_manager.get_unclaimed_routes()

    def get_claimed_routes(self):
        """Talep edilen rotaları GameManager'dan al"""
        return self.game_manager.get_claimed_routes()

    """
    def claim_route(self, route_id):
        success = self.game_manager.claim_route(route_id)
        if success:
            self.view.main_frame.create_roads()
        else:
            print(f"Route {route_id} could not be claimed.")
    """

    def draw_train_card(self, card_number=None):
        self.game_manager.draw_train_card(card_number)
        self.view.train_cards.update_train_card_selection_frame()

    def draw_destination_ticket(self):
        self.game_manager.draw_destination_ticket()
        self.view.destination_tickets.update_destination_ticket_frame()

    def update_train_numbers(self):
        train_card_counts = self.game_manager.update_train_numbers()
        self.view.main_frame.update_train_numbers(train_card_counts)

    def next_turn(self):
        self.game_manager.next_turn()
        print(f"Next turn: {self.game_manager.get_current_player().name}'s turn")
