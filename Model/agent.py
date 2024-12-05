import random
class Agent:
    def __init__(self, color, game_service):
        self.color = color
        self.game_service = game_service
        self.first_time_bool = True

    def perform_action(self):
        print(f"------------{self.color} COLORED AI PERFORMING ACTION---------------")

        if self.first_time_bool:
            print("AI: ",self.color,"'S FIRST ROUND SO PICKING A DESTINATION TICKET")
            self.first_time_bool = False
            action_params = {
                "selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.game_service.get_available_actions(self.color)
        print(f"AI: {self.color} available actions: {available_actions}")

        random_action = random.choice(available_actions)
        #random_action = 'claim_route'

        print(f"AI: {self.color} COLORED AGENT SELECTED THIS ACTION: {random_action}")

        if random_action == 'draw_train_card':
            self.draw_train_card()
            print(f"AI: {self.color} COLORED AI has competed DRAWING TRAIN CARD successfully")
        elif random_action == 'draw_destination_ticket':
            self.draw_destination_ticket()
            print(f"AI: {self.color} COLORED AI has competed DRAWING DESTINATION TICKET CARD successfully")
        elif random_action == 'claim_route':
            self.claim_route()
            print(f"AI: {self.color} COLORED AI has competed CLAIMING ROUTE successfully")

    def draw_train_card(self):
        # draw colored or joker train card
        random_number = random.randint(0, 5)
        print("AI: DRAW TRAIN CARD RANDOM NUMBER THAT AI SELECTED:", random_number)

        if random_number == 5:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED CARD BY AI: BLIND PICK")
            returned_item = self.game_service.perform_action("draw_train_card", action_params)
            if returned_item == 0:
                self.draw_train_card()
                return
        else:
            game_state = self.game_service.get_game_state()
            train_cards_on_the_table = game_state["train_cards_on_the_table"]
            selected_card = train_cards_on_the_table[random_number]
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for first pick: ", train_cards_on_the_table)
            print("AI: SELECTED CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)
            train_cards_on_the_table = game_state["train_cards_on_the_table"]
            print("AI: Train cards on the table for second pick: ", train_cards_on_the_table)
            if self.game_service.check_if_second_train_card_needed():
                check = True
                while check:
                    second_random_number = random.randint(0, len(train_cards_on_the_table)-1)
                    selected_second_card = train_cards_on_the_table[second_random_number]
                    if selected_second_card.color == "joker":
                        continue
                    else:
                        action_params = {"selected_card": selected_second_card}
                        print("AI: SELECTED SECOND CARD BY AI:", selected_second_card.color)
                        self.game_service.perform_action("draw_train_card", action_params)
                        check = False

    def draw_destination_ticket(self):
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)

        destination_card_list_without_none = []
        for card in draw_destination_card_list:
            if card is not None:
                destination_card_list_without_none.append(card)

        number_of_cards_to_select = random.randint(1, len(destination_card_list_without_none))
        selected_cards = random.sample(destination_card_list_without_none, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)


    def claim_route(self):
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]
        if claimable_routes:
            random_route = random.choice(claimable_routes)

            if random_route.color == "gray":
                print("AI: A GRAY ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                cards_can_be_used_to_claim_gray_route = self.game_service.perform_action("claim_route", action_params)
                use_random_color = random.choice(cards_can_be_used_to_claim_gray_route)
                action_params = {"selected_route": random_route, "use_this_color": use_random_color}
                self.game_service.perform_action("claim_route", action_params)
            else:
                print("AI: A COLORED ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                self.game_service.perform_action("claim_route", action_params)

