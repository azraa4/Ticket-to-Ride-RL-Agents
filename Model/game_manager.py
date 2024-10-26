from Model.board import Board
from Model.deck import Deck
from Model.player import Player
from Model.train_card import TrainCard
from Model.destination_ticket import DestinationTicket
from Model.destination_ticket import DestinationTicket
import json

class GameManager:
    def __init__(self):
        self.players = []

        self.train_cards_deck = Deck([TrainCard(color) for color in ["blue", "red", "green", "orange", "yellow", "white", "black", "pink", "joker"]] * 12)
        self.cards_on_the_table = []

        self.destination_tickets_deck = Deck(self.create_destination_tickets_list())

        #self.destination_cards_deck =

        self.board = Board()

        self.current_turn = 0
        self.current_player = None
        self.claimed_routes = []

    def start_game(self):
        self.current_player = self.players[0]
        self.train_cards_deck.shuffle()
        self.deal_train_cards_on_the_table()
        print(self.current_player)

    def deal_train_cards_on_the_table(self):
        for i in range(0, 5-len(self.cards_on_the_table)):
            self.cards_on_the_table.append(self.train_cards_deck.draw_card())

    def draw_train_card(self, train_card):
        self.cards_on_the_table.remove(train_card)
        self.current_player.train_cards.append(train_card)
        print(self.current_player.train_cards)
        self.deal_train_cards_on_the_table()

    def draw_cards_from_blind_deck(self):
        if self.current_player is not None:
            self.current_player.train_cards.append(self.train_cards_deck.draw_card())
            self.current_player.train_cards.append(self.train_cards_deck.draw_card())

    def create_destination_tickets_list(self):
        destination_tickets_list = []
        with open("../Model/destination_tickets_data.json", "r") as json_file:
            data = json.load(json_file)
            destination_tickets_data = data["destination_tickets_data"]

        for destination_ticket in destination_tickets_data:
            dest_ticket_to_add = DestinationTicket(
                destination_ticket["city1"],
                destination_ticket["city2"],
                destination_ticket["points"],
                destination_ticket["id"],
            )
            destination_tickets_list.append(dest_ticket_to_add)

        return destination_tickets_list

    def next_turn(self):
        self.current_turn = self.current_turn + 1
        self.current_player = self.players[self.current_turn%len(self.players)]

    def get_current_player(self):
        return self.players[self.current_turn]

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    def update_train_numbers(self):
        current_player = self.get_current_player()
        card_colors = [card.color for card in current_player.train_cards]
        return {color: card_colors.count(color) for color in set(card_colors)}

    def add_player(self, player_name, player_color):
        self.players.append(Player(player_name, player_color))
        print(self.players)

    def get_claimable_routes(self):
        claimable_routes = []

        if self.current_player is not None:
            blue_card_value = self.current_player.get_number_of_cards("blue")
            red_card_value = self.current_player.get_number_of_cards("red")
            green_card_value = self.current_player.get_number_of_cards("green")
            orange_card_value = self.current_player.get_number_of_cards("orange")
            yellow_card_value = self.current_player.get_number_of_cards("yellow")
            white_card_value = self.current_player.get_number_of_cards("white")
            black_card_value = self.current_player.get_number_of_cards("black")
            pink_card_value = self.current_player.get_number_of_cards("pink")
            joker_card_value = self.current_player.get_number_of_cards("joker")

            train_tickets = {
                "blue": blue_card_value,
                "red": red_card_value,
                "green": green_card_value,
                "orange": orange_card_value,
                "yellow": yellow_card_value,
                "white": white_card_value,
                "black": black_card_value,
                "pink": pink_card_value,
            }

            for route in self.board.get_unclaimed_routes():
                if route.color == "gray":
                    for color, card_value in train_tickets.items():
                        if card_value >= route.length:
                            claimable_routes.append(route)
                            break
                        elif card_value + joker_card_value >= route.length:
                            claimable_routes.append(route)
                            break
                else:
                    needed_cards = route.length
                    available_cards = train_tickets[route.color]
                    if available_cards >= needed_cards:
                        claimable_routes.append(route)
                    else:
                        missing_cards = needed_cards - available_cards
                        if missing_cards <= joker_card_value:
                            claimable_routes.append(route)

        return claimable_routes



