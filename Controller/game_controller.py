class GameController:
    def __init__(self, view, game_manager):
        self.view = view
        self.game_manager = game_manager
        self.turns_available = True
        self.draw_train_card_limit = 2

    def start_game(self):
        self.game_manager.start_game()
        self.update_turn_text()
        self.update_player_info_text()
        self.set_inventory()
        self.deal_the_cards_to_train_card_selection_frame()
        self.update_claimable_routes_frame()

    def update_turn_text(self):
        self.view.header.update_turn_text(f"Turn: {self.game_manager.current_turn+1}")

    def update_player_info_text(self):
        self.view.header.update_players_info_text(f"Player: {self.game_manager.current_player.name} ({self.game_manager.current_player.color}) Points: {self.game_manager.current_player.points}")

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
        print(self.game_manager.cards_on_the_table)
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

    def draw_train_card(self, train_card):
        if train_card.color == "joker":
            if self.draw_train_card_limit == 1:
                print("You can only take 1 joker or 2 colored cards!!!")
            else:
                self.game_manager.draw_train_card(train_card)
                self.deal_the_cards_to_train_card_selection_frame()
                self.set_inventory()
                self.update_claimable_routes_frame()
                self.go_to_next_turn()
        else:
            self.game_manager.draw_train_card(train_card)
            self.deal_the_cards_to_train_card_selection_frame()
            self.set_inventory()
            self.update_claimable_routes_frame()
            if self.draw_train_card_limit == 1:
                self.go_to_next_turn()
            self.draw_train_card_limit -= 1

    def draw_cards_from_blind_deck(self):
        print("blind cards is drawn.")
        self.game_manager.draw_cards_from_blind_deck()
        self.set_inventory()
        self.update_claimable_routes_frame()
        self.go_to_next_turn()

    def go_to_next_turn(self):
        if self.turns_available:
            self.game_manager.next_turn()
            self.update_turn_text()
            self.update_player_info_text()
            self.set_inventory()
            self.update_claimable_routes_frame()

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
        if using == "Claim using red cards.":
            self.game_manager.current_player.remove_card_according_to_color("red", selected_route.length)
        if using == "Claim using green cards.":
            self.game_manager.current_player.remove_card_according_to_color("green", selected_route.length)
        if using == "Claim using orange cards.":
            self.game_manager.current_player.remove_card_according_to_color("orange", selected_route.length)
        if using == "Claim using yellow cards.":
            self.game_manager.current_player.remove_card_according_to_color("yellow", selected_route.length)
        if using == "Claim using white cards.":
            self.game_manager.current_player.remove_card_according_to_color("white", selected_route.length)
        if using == "Claim using black cards.":
            self.game_manager.current_player.remove_card_according_to_color("black", selected_route.length)
        if using == "Claim using pink cards.":
            self.game_manager.current_player.remove_card_according_to_color("pink", selected_route.length)
        if using == "Claim using joker cards.":
            self.game_manager.current_player.remove_card_according_to_color("joker", selected_route.length)

        self.view.main_frame.create_roads()
        self.view.claimable_routes.update_routes_frame()
        self.set_inventory()
        self.view.main_frame.destroy_select_card_for_gray_roads_frame()
        self.go_to_next_turn()

    def claim_route_force(self, id, player):
        print("claimed")
        unclaimed_routes = self.game_manager.board.get_unclaimed_routes()
        for route in unclaimed_routes:
            if route.id == id:
                route.claimed_by = player
                route.claimed_color = "blue"
        self.view.main_frame.create_roads()

    def get_claimable_routes(self):
        routes = self.game_manager.get_claimable_routes()

        return routes

    def update_claimable_routes_frame(self):
        self.view.claimable_routes.update_routes_frame()