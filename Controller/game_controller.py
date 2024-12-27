import global_vars
import time

class GameController:
    def __init__(self, view, game_manager, game_service, ai_manager, test_name):
        self.view = view
        self.game_manager = game_manager
        self.game_service = game_service
        self.turns_available = True
        self.draw_train_card_limit = 2
        self.selecting_second_train_card = False
        self.last_turn = None
        self.game_end = False

        self.ai_manager = ai_manager
        self.game_start_destination_tickets_list_for_ai = None

        self.test_name = test_name
        self.stop_process_end_game=False

        self.visualize = True

        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

        self.start_turn_time = None
        self.end_turn_time = None

    def start_game(self):
        self.start_time = time.time()
        #cleans the log file
        if self.test_name is not None:
            with open(f"logs/log_{self.test_name}_{self.view.game_id}.txt", "w") as log_file:
                log_file.write("GAME LOGS:\n")


        self.game_manager.start_game()

        self.log(f"Turn:{((self.game_manager.current_turn) // len(self.game_manager.players) + 1)}, {self.get_current_player().name}({self.get_current_player().color})'s turn.")

        if self.get_current_player().first_turn:
            self.game_start_destination_tickets_list_for_ai = self.open_draw_destination_ticket_frame()


        self.update_turn_text()
        self.update_player_info_text()
        self.update_players_info_text()
        self.set_inventory()
        self.deal_the_cards_to_train_card_selection_frame()
        self.view.train_cards.update_remaining_cards_in_deck(self.game_manager.train_cards_deck.get_length())
        self.update_claimable_routes_frame()
        self.view.destination_tickets.update_destination_tickets_frame()

        self.game_service.on_change_of_turn()

        self.start_turn_time = time.time()


    def update_turn_text(self):
        self.view.header.update_turn_text(f"Turn: {((self.game_manager.current_turn) // len(self.game_manager.players)+1)}")

    def update_player_info_text(self):
        self.view.header.update_player_info_text(f"Player: {self.game_manager.current_player.name} ({self.game_manager.current_player.color}) Points: {self.game_manager.current_player.points}")

    def get_current_player(self):
        return self.game_manager.current_player

    def update_players_info_text(self):
        players_info = [
            f"{player.color} : {player.points} pts - {player.train_cars} cars"
            for player in self.game_manager.players
        ]

        all_players_text = " | ".join(players_info)

        self.view.header.update_players_info_text(all_players_text)

    def get_players(self):
        return self.game_manager.players

    def set_inventory(self):
        self.view.main_frame.blue_card_value = 0
        self.view.main_frame.red_card_value = 0
        self.view.main_frame.green_card_value = 0
        self.view.main_frame.pink_card_value = 0
        self.view.main_frame.yellow_card_value = 0
        self.view.main_frame.orange_card_value = 0
        self.view.main_frame.white_card_value = 0
        self.view.main_frame.black_card_value = 0
        self.view.main_frame.joker_card_value = 0

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "blue":
                self.view.main_frame.blue_card_value = self.view.main_frame.blue_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "red":
                self.view.main_frame.red_card_value = self.view.main_frame.red_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "green":
                self.view.main_frame.green_card_value = self.view.main_frame.green_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "pink":
                self.view.main_frame.pink_card_value = self.view.main_frame.pink_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "yellow":
                self.view.main_frame.yellow_card_value = self.view.main_frame.yellow_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "orange":
                self.view.main_frame.orange_card_value = self.view.main_frame.orange_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "white":
                self.view.main_frame.white_card_value = self.view.main_frame.white_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "black":
                self.view.main_frame.black_card_value = self.view.main_frame.black_card_value + 1

        for train_card in self.game_manager.current_player.train_cards:
            if train_card.color == "joker":
                self.view.main_frame.joker_card_value = self.view.main_frame.joker_card_value + 1

        self.view.main_frame.update_train_numbers()

    def deal_the_cards_to_train_card_selection_frame(self):
        if self.game_manager.all_cards_on_the_players_hands:
            self.view.train_cards.destroy_all_train_cards()
            return
        self.view.train_cards.card_1 = self.game_manager.cards_on_the_table[0]
        self.view.train_cards.card_1_img_path = self.game_manager.cards_on_the_table[0].image_path
        self.view.train_cards.card_2 = self.game_manager.cards_on_the_table[1]
        self.view.train_cards.card_2_img_path = self.game_manager.cards_on_the_table[1].image_path
        self.view.train_cards.card_3 = self.game_manager.cards_on_the_table[2]
        self.view.train_cards.card_3_img_path = self.game_manager.cards_on_the_table[2].image_path
        self.view.train_cards.card_4 = self.game_manager.cards_on_the_table[3]
        self.view.train_cards.card_4_img_path = self.game_manager.cards_on_the_table[3].image_path
        self.view.train_cards.card_5 = self.game_manager.cards_on_the_table[4]
        self.view.train_cards.card_5_img_path = self.game_manager.cards_on_the_table[4].image_path
        self.view.train_cards.update_train_card_selection_frame()

    def get_train_cards_on_the_table(self):
        return self.game_manager.cards_on_the_table

    def draw_train_card(self, train_card):
        if train_card.color == "joker":
            if self.draw_train_card_limit == 1:
                print("!        ERROR: You can only take 1 joker or 2 colored cards!!!")
            else:
                self.game_manager.draw_train_card(train_card)
                self.deal_the_cards_to_train_card_selection_frame()
                self.set_inventory()
                self.update_claimable_routes_frame()
                self.go_to_next_turn()
        else:
            self.selecting_second_train_card = True
            self.game_manager.draw_train_card(train_card)
            self.deal_the_cards_to_train_card_selection_frame()
            self.set_inventory()
            self.update_claimable_routes_frame()
            self.draw_train_card_limit -= 1
            self.view.destination_tickets.destroy_draw_ticket_button()
            self.view.claimable_routes.update_routes_frame()
            self.view.train_cards.update_train_card_pick_buttons(True)

            if self.draw_train_card_limit == 0:
                self.view.destination_tickets.create_draw_ticket_button()
                self.selecting_second_train_card = False
                self.view.claimable_routes.update_routes_frame()
                self.view.train_cards.update_train_card_pick_buttons(False)
                self.go_to_next_turn()

        self.view.train_cards.update_remaining_cards_in_deck(self.game_manager.train_cards_deck.get_length())

    def draw_train_card_for_ai(self, train_card):
        if train_card == "select_blind":
            return self.draw_cards_from_blind_deck()
        else:
            return self.draw_train_card(train_card)

    def draw_cards_from_blind_deck(self):
        if self.game_manager.train_cards_deck.get_length()<=2:
            print("!        ERROR: can't draw blind cards since there is less than two cards in the deck.")
            return 0
        if self.draw_train_card_limit == 1:
            print("!        ERROR: You can't take blind card as second card!!!")
            return
        self.game_manager.draw_cards_from_blind_deck()
        self.set_inventory()
        self.update_claimable_routes_frame()
        self.view.train_cards.update_remaining_cards_in_deck(self.game_manager.train_cards_deck.get_length())
        self.go_to_next_turn()

    def can_draw_destination_ticket(self):
        return not self.game_manager.destination_tickets_deck.is_empty()
    def open_draw_destination_ticket_frame(self):
        if not self.can_draw_destination_ticket():
            print("!        IMPORTANT INFO: destination tickets deck is empty")
            return

        self.game_manager.destination_tickets_deck.shuffle()

        card1 = self.game_manager.destination_tickets_deck.draw_card()
        card2 = self.game_manager.destination_tickets_deck.draw_card()
        card3 = self.game_manager.destination_tickets_deck.draw_card()

        self.view.main_frame.create_select_destination_tickets_canvas(card1, card2, card3)

        return [card1, card2, card3]

    def draw_destination_ticket(self, cards_list):
        for card in cards_list:
            self.game_manager.current_player.add_destination_ticket(card)
        self.view.destination_tickets.update_destination_tickets_frame()
        self.go_to_next_turn()

    def destroy_select_destination_tickets_canvas_for_ai(self):
        self.view.main_frame.destroy_select_destination_tickets_canvas()

    def get_current_player_destination_tickets(self):
        destination_tickets = []
        if self.game_manager.current_player is not None:
            destination_tickets = self.game_manager.current_player.destination_tickets
        return destination_tickets

    def go_to_next_turn(self):
        if self.turns_available and not self.game_end:
            if(self.get_current_player().ai):
                self.view.root.after(global_vars.time_turn * 1000, self._go_to_next_turn)
            else:
                self.view.root.after(global_vars.time_turn_for_human*1000, self._go_to_next_turn)
                self.change_status_text("TURN CHANGED.")


    def _go_to_next_turn(self):
        # Before going next turn
        self.end_turn_time = time.time()
        self.get_current_player().total_turn_played += 1
        self.get_current_player().total_time_played += self.end_turn_time - self.start_turn_time
        self.end_turn_time = None
        self.start_turn_time = None

        self.get_current_player().first_turn = False

        self.calculate_current_player_points()
        self.update_players_info_text()
        self.check_last_turn()

        if self.game_manager.train_cards_deck.get_length() <= 2:
            print("!        ERROR:Blind card deleted since there is less than two cards on the deck.")
            self.view.train_cards.destroy_train_card_pick_button("train_card_pick_button6")
            self.view.destination_tickets.create_draw_ticket_button()
            self.view.claimable_routes.update_routes_frame()
            self.selecting_second_train_card = False
            self.draw_train_card_limit = 2

        log_this = "POINTS: "
        for player in self.game_manager.players:
            log_this+=f"{player.color} has {player.points},"
        log_this = log_this.rstrip(',')
        self.log(log_this)

        check = self.check_if_game_ended()
        if check:
            return

        # Going next turn
        self.game_manager.next_turn()

        # After going next turn
        self.start_turn_time = time.time()
        log_this = f"GAMESTATE: Turn: {((self.game_manager.current_turn) // len(self.game_manager.players) + 1)} | "
        for i in range(len(self.game_manager.players)):
            player = self.game_manager.players[i]
            log_this += f"Player {i} Name: {player.name}, Player {i} Color: {player.color}, Player {i} Points: {player.points}, Player {i} Cars: {player.train_cars} | "
        log_this = log_this.rstrip('|')
        self.log(log_this)

        self.log(f"Turn:{((self.game_manager.current_turn) // len(self.game_manager.players)+1)}, {self.get_current_player().name}({self.get_current_player().color})'s turn.")



        if self.get_current_player().first_turn:
            print(self.get_current_player().color, "'s First Turn (PLAYER FIRST TURN CHECK)")
            self.game_start_destination_tickets_list_for_ai = self.open_draw_destination_ticket_frame()




        self.selecting_second_train_card = False
        self.update_player_info_text()
        self.update_claimable_routes_frame()
        self.draw_train_card_limit = 2
        self.update_turn_text()
        self.set_inventory()
        self.view.destination_tickets.update_destination_tickets_frame()

        self.game_service.on_change_of_turn()



    def force_go_to_next_turn(self):
        # Before going next turn
        self.calculate_current_player_points()
        self.update_players_info_text()
        self.check_last_turn()

        if self.game_manager.train_cards_deck.get_length() <= 2:
            print("!        IMPORTANT INFO: Blind card deleted since there is less than two cards on the deck.")
            self.view.train_cards.destroy_train_card_pick_button("train_card_pick_button6")
            self.view.destination_tickets.create_draw_ticket_button()
            self.view.claimable_routes.update_routes_frame()
            self.selecting_second_train_card = False
            self.draw_train_card_limit = 2
            return

        # Going next turn
        self.game_manager.next_turn()

        # After going next turn
        if self.get_current_player().first_turn:
            print(self.get_current_player().color, "'s First Turn (PLAYER FIRST TURN CHECK)")
            self.game_start_destination_tickets_list_for_ai = self.open_draw_destination_ticket_frame()
            self.get_current_player().first_turn = False

        self.check_if_game_ended()
        self.selecting_second_train_card = False
        self.update_player_info_text()
        self.update_claimable_routes_frame()
        self.draw_train_card_limit = 2
        self.update_turn_text()
        self.set_inventory()
        self.view.destination_tickets.update_destination_tickets_frame()

        self.game_service.on_change_of_turn()

        #print(f"Draw Train Card Limit: {self.draw_train_card_limit}")

    def change_turn_availability(self, bool):
        self.turns_available = bool

    def get_unclaimed_routes(self):
        return self.game_manager.board.get_unclaimed_routes()

    def get_claimed_routes(self):
        return self.game_manager.board.get_claimed_routes()

    def claim_route(self, selected_route):
        selected_route.claimed_by = self.game_manager.current_player
        selected_route.claimed_color = self.game_manager.current_player.color

        if selected_route.color == "gray":
            self.view.main_frame.create_select_card_for_gray_roads_frame(selected_route)
        else:
            if self.game_manager.current_player.get_number_of_cards(selected_route.color) >= selected_route.length:
                self.game_manager.current_player.remove_card_according_to_color(selected_route.color, selected_route.length)
            else:
                amount_of_joker_card_to_delete = selected_route.length - self.game_manager.current_player.get_number_of_cards(selected_route.color)
                self.game_manager.current_player.remove_card_according_to_color(selected_route.color, self.game_manager.current_player.get_number_of_cards(selected_route.color))
                self.game_manager.current_player.remove_card_according_to_color("joker", amount_of_joker_card_to_delete)
            self.view.main_frame.create_roads()
            self.view.claimable_routes.update_routes_frame()
            self.set_inventory()
            self.game_manager.current_player.add_route(selected_route)
            self.game_manager.current_player.decrease_train_cars(selected_route.length)
            self.go_to_next_turn()

    def cards_needed_to_claim_gray_route(self, selected_route):
        cards_can_be_used = []
        if self.game_manager.current_player is not None:
            blue_card_value = self.game_manager.current_player.get_number_of_cards("blue")
            red_card_value = self.game_manager.current_player.get_number_of_cards("red")
            green_card_value = self.game_manager.current_player.get_number_of_cards("green")
            orange_card_value = self.game_manager.current_player.get_number_of_cards("orange")
            yellow_card_value = self.game_manager.current_player.get_number_of_cards("yellow")
            white_card_value = self.game_manager.current_player.get_number_of_cards("white")
            black_card_value = self.game_manager.current_player.get_number_of_cards("black")
            pink_card_value = self.game_manager.current_player.get_number_of_cards("pink")
            joker_card_value = self.game_manager.current_player.get_number_of_cards("joker")

            if blue_card_value>=selected_route.length or blue_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using blue cards.")
            if red_card_value>=selected_route.length or red_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using red cards.")
            if green_card_value>=selected_route.length or green_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using green cards.")
            if orange_card_value>=selected_route.length or orange_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using orange cards.")
            if yellow_card_value>=selected_route.length or yellow_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using yellow cards.")
            if white_card_value>=selected_route.length or white_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using white cards.")
            if black_card_value>=selected_route.length or black_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using black cards.")
            if pink_card_value>=selected_route.length or pink_card_value + joker_card_value >= selected_route.length:
                cards_can_be_used.append("Claim using pink cards.")
            if joker_card_value>=selected_route.length:
                cards_can_be_used.append("Claim using joker cards.")

        return cards_can_be_used

    def claim_gray_route(self, using, selected_route):
        if using == "Claim using blue cards.":
            self.game_manager.current_player.remove_card_according_to_color("blue", selected_route.length)
        elif using == "Claim using red cards.":
            self.game_manager.current_player.remove_card_according_to_color("red", selected_route.length)
        elif using == "Claim using green cards.":
            self.game_manager.current_player.remove_card_according_to_color("green", selected_route.length)
        elif using == "Claim using orange cards.":
            self.game_manager.current_player.remove_card_according_to_color("orange", selected_route.length)
        elif using == "Claim using yellow cards.":
            self.game_manager.current_player.remove_card_according_to_color("yellow", selected_route.length)
        elif using == "Claim using white cards.":
            self.game_manager.current_player.remove_card_according_to_color("white", selected_route.length)
        elif using == "Claim using black cards.":
            self.game_manager.current_player.remove_card_according_to_color("black", selected_route.length)
        elif using == "Claim using pink cards.":
            self.game_manager.current_player.remove_card_according_to_color("pink", selected_route.length)
        elif using == "Claim using joker cards.":
            self.game_manager.current_player.remove_card_according_to_color("joker", selected_route.length)
        else:
            print("!        ERROR: there is an error about claim gray route using color")

        self.view.main_frame.create_roads()
        self.view.claimable_routes.update_routes_frame()
        self.set_inventory()
        self.view.main_frame.destroy_select_card_for_gray_roads_frame()
        self.game_manager.current_player.add_route(selected_route)
        self.game_manager.current_player.decrease_train_cars(selected_route.length)
        self.go_to_next_turn()

    def claim_route_force(self, id, player):
        print("forced claim")
        unclaimed_routes = self.game_manager.board.get_unclaimed_routes()
        for route in unclaimed_routes:
            if route.id == id:
                route.claimed_by = player
                route.claimed_color = "blue"
        self.view.main_frame.create_roads()

    def claim_route_for_ai(self, selected_route, with_color):
        selected_route.claimed_by = self.game_manager.current_player
        selected_route.claimed_color = self.game_manager.current_player.color

        if selected_route.color == "gray":
            self.claim_gray_route(f"Claim using {with_color} cards.", selected_route)
        else:
            if self.game_manager.current_player.get_number_of_cards(selected_route.color) >= selected_route.length:
                self.game_manager.current_player.remove_card_according_to_color(selected_route.color, selected_route.length)
            else:
                amount_of_joker_card_to_delete = selected_route.length - self.game_manager.current_player.get_number_of_cards(selected_route.color)
                self.game_manager.current_player.remove_card_according_to_color(selected_route.color, self.game_manager.current_player.get_number_of_cards(selected_route.color))
                self.game_manager.current_player.remove_card_according_to_color("joker", amount_of_joker_card_to_delete)
            self.view.main_frame.create_roads()
            self.view.claimable_routes.update_routes_frame()
            self.set_inventory()
            self.game_manager.current_player.add_route(selected_route)
            self.game_manager.current_player.decrease_train_cars(selected_route.length)
            self.go_to_next_turn()

    def get_claimable_routes(self):
        routes = self.game_manager.get_claimable_routes()

        return routes

    def update_claimable_routes_frame(self):
        self.view.claimable_routes.update_routes_frame()

    def calculate_current_player_points(self):
        self.game_manager.current_player.calculate_points()

    def check_last_turn(self):
        if self.last_turn is not None:
            return

        for player in self.game_manager.players:
            if player.train_cars <= 2:
                self.last_turn = ((self.game_manager.current_turn) // len(self.game_manager.players)+1) + 1
                print("GAME INFO: Entered to last turn!")

    def get_last_turn_info(self):
        if self.last_turn is not None:
            return True
        return False

    def check_if_game_ended(self):
        if self.last_turn is not None and not self.game_end:
            if (((self.game_manager.current_turn) // len(self.game_manager.players)+1)) == self.last_turn+1:
                print("---GAME END---")
                self.get_current_player().total_turn_played -= 1

                self.game_end = True
                self.reward_the_longest_route()
                self.show_game_end_frame()

                if self.stop_process_end_game:
                    self.quit_game()
                return True
        return False


    def reward_the_longest_route(self):
        players_have_longest_route = []
        longest_route_length = 0
        for player in self.game_manager.players:
            longest_route_of_the_player = player.calculate_longest_route()
            if longest_route_length<longest_route_of_the_player:
                players_have_longest_route = []
                players_have_longest_route.append(player)
                longest_route_length = longest_route_of_the_player
            elif longest_route_length == longest_route_of_the_player:
                players_have_longest_route.append(player)

        for player in players_have_longest_route:
            print(f"POINT STATUS: {player.color} has rewarded with longest route extra points.")
            player.points += 10
            player.has_longest_road = True

    def show_game_end_frame(self):
        self.end_time = time.time()

        #find the winner
        winner_player = None
        temp_max_points = 0
        for player in self.game_manager.players:
            if player.points>=temp_max_points:
                winner_player = player
                temp_max_points = player.points

        for player in self.game_manager.players:
            if player == winner_player:
                player.winner = True

        turn_played = ((self.game_manager.current_turn) // len(self.game_manager.players)+1)
        info = {"winner": winner_player, "players": self.game_manager.players, "turn played": turn_played}

        total_time_played=self.end_time - self.start_time
        longest_route_player = None
        for player in self.game_manager.players:
            if player.has_longest_road:
                self.log(f"{player.color} has {player.points} with longest road.")
                longest_route_player = player
            else:
                self.log(f"{player.color} has {player.points}")

        self.log(f"Turn:{((self.game_manager.current_turn) // len(self.game_manager.players) + 1)}, GAME END")
        self.log(f"Winner: {winner_player.name}({winner_player.color})")

        send_this = f"PLAYERS:"
        for player in self.game_manager.players:
            send_this+=f"{player.color}, {player.points}, {player.has_longest_road}, {45-player.train_cars}, {player.total_turn_played}, {player.total_time_played:.2f}, {player.winner};"

        self.log(send_this)
        self.log(f"RESULTS: {len(self.game_manager.players)}, {winner_player.color}, {longest_route_player.color}, {turn_played}, {total_time_played:.2f}")

        self.view.game_end_frame.create_game_end_frame(info)



    def get_game_end(self):
        return self.game_end

    def change_player_cars(self, player_index, car_amount):
        self.game_manager.players[player_index].train_cars = car_amount

    def get_player_by_color(self, color):
        for player in self.game_manager.players:
            if player.color == color:
                return player

    def get_ai_list(self):
        return self.ai_manager.agents

    def change_status_text(self, text):
        self.view.main_frame.update_status_text(text)

    def quit_game(self):
        self.view.stop_game()

    def log(self, text):
        if self.test_name is not None:
            with open(f"logs/log_{self.test_name}_{self.view.game_id}.txt", "a") as log_file:
                log_file.write(text + "\n")
