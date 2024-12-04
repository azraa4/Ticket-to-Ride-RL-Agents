import random
class Agent:
    def __init__(self, color, game_service):
        self.color = color
        self.game_service = game_service
        self.first_time_bool = True

    def perform_action(self):
        print("------------perform actiona girildi---------------")

        if self.first_time_bool:
            print(self.color,"'S FIRST TIME")
            self.first_time_bool = False
            action_params = {
                "selected_destination_tickets": self.game_service.get_destination_tickets_list_at_the_start_of_the_game()}
            self.game_service.perform_action("draw_destination_ticket", action_params)
            return

        available_actions = self.game_service.get_available_actions(self.color)
        print(f"{self.color} available actions: {available_actions}")

        random_action = random.choice(available_actions)
        #random_action = 'claim_route'

        print(self.color," COLORED AGENT SELECTED THIS ACTION:", random_action)

        if random_action == 'draw_train_card':
            self.draw_train_card()
        elif random_action == 'draw_destination_ticket':
            self.draw_destination_ticket()
        elif random_action == 'claim_route':
            self.claim_route()

    def draw_train_card(self):
        # draw colored or joker train card
        random_number = random.randint(0, 5)
        print("RANDOM NUMBER THAT AI SELECTED:", random_number)

        if random_number == 5:
            action_params = {"selected_card": "select_blind"}
            print("SELECTED CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)
        else:
            game_state = self.game_service.get_game_state()
            train_cards_on_the_table = game_state["train_cards_on_the_table"]
            selected_card = train_cards_on_the_table[random_number]
            action_params = {"selected_card": selected_card}
            print("SELECTED CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)
            if self.game_service.check_if_second_train_card_needed():
                check = True
                while check:
                    second_random_number = random.randint(0, 4)
                    selected_second_card = train_cards_on_the_table[second_random_number]
                    if selected_second_card.color == "joker":
                        continue
                    else:
                        action_params = {"selected_card": selected_second_card}
                        print("SELECTED SECOND CARD BY AI:", selected_second_card.color)
                        self.game_service.perform_action("draw_train_card", action_params)
                        check = False

    def draw_destination_ticket(self):
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)

        number_of_cards_to_select = random.randint(1, 3)
        selected_cards = random.sample(draw_destination_card_list, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)

    def claim_route(self):
        current_state = self.game_service.get_current_player_state()
        claimable_routes = current_state["claimable_routes"]
        if claimable_routes:
            random_route = random.choice(claimable_routes)

            if random_route.color == "gray":
                print("A GRAY ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                cards_can_be_used_to_claim_gray_route = self.game_service.perform_action("claim_route", action_params)
                use_random_color = random.choice(cards_can_be_used_to_claim_gray_route)
                action_params = {"selected_route": random_route, "use_this_color": use_random_color}
                self.game_service.perform_action("claim_route", action_params)
            else:
                print("A COLORED ROUTE SELECTED")
                action_params = {"selected_route": random_route, "use_this_color": None}
                self.game_service.perform_action("claim_route", action_params)

