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

        self.all_cards_on_the_players_hands = False

    def start_game(self):
        self.current_player = self.players[0]
        self.train_cards_deck.shuffle()
        self.deal_train_cards_on_the_table()

    def deal_train_cards_on_the_table(self):
        for i in range(0, 5-len(self.cards_on_the_table)):
            train_card = self.train_cards_deck.draw_card()
            if train_card is not None:
                self.cards_on_the_table.append(train_card)
            else:
                # Recreate the train card deck based on the colors and total count
                all_colors = ["blue", "red", "green", "orange", "yellow", "white", "black", "pink", "joker"]
                card_count_per_color = 12

                # Count how many cards of each color are currently with players
                color_counts = {color: card_count_per_color for color in all_colors}
                for player in self.players:
                    for card in player.train_cards:
                        color_counts[card.color] -= 1  # Decrease based on player's current cards

                # Recreate the deck with the remaining card counts
                new_deck = []
                for color, count in color_counts.items():
                    new_deck.extend([TrainCard(color) for _ in range(count)])

                if len(new_deck) >= 5:
                    self.train_cards_deck = Deck(new_deck)
                    self.train_cards_deck.shuffle()

                    self.cards_on_the_table = []
                    self.deal_train_cards_on_the_table()
                else:
                    print("!        ERROR:All cards are in players' hands. No more cards to draw until players discard or play cards.")
                    self.all_cards_on_the_players_hands = True
                    return


    def draw_train_card(self, train_card):
        self.cards_on_the_table.remove(train_card)
        self.current_player.train_cards.append(train_card)
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
        return self.current_player

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
                if self.current_player.train_cars >= route.length:
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



