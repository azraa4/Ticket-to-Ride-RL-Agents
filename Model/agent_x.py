import random
import time

import global_vars


class AgentX:
    def __init__(self, color, game_service):
        self.color = color
        self.game_service = game_service
        self.first_time_bool = True

    def perform_action(self):
        """
        Ajanın her turda yapacağı eylemi belirler ve gerçekleştirir.
        """
        if self.game_service.get_game_state()["game_ended"]:
            return

        print(f"------------{self.color} COLORED AI PERFORMING ACTION---------------")

        # Oyunun Başlangıcında Hedef Biletleri Seçme
        if self.first_time_bool:
            print("AI: ", self.color, "'S FIRST ROUND SO PICKING A DESTINATION TICKET")
            self.first_time_bool = False
            # Oyunun başında en az 2, en fazla 3 bilet seç (rastgele)
            tickets = self.game_service.get_destination_tickets_list_at_the_start_of_the_game()
            selected_tickets = random.sample(tickets, k=random.randint(2, 3))
            action_params = {"selected_destination_tickets": selected_tickets}
            self.game_service.perform_action("draw_destination_ticket", action_params)

            log_message = f"{self.color}, Action: DESTINATION TICKET,"
            for ticket in selected_tickets:
                log_message += f" {ticket.city1} to {ticket.city2},"
            log_message = log_message.rstrip(',')
            self.game_service.log(log_message)
            return  # İlk turda sadece bilet seçimi yapıldığı için fonksiyondan çık

        # Mevcut turda yapılabilecek eylemleri al
        available_actions = self.game_service.get_available_actions(self.color)
        print(f"AI: {self.color} available actions: {available_actions}")
        self.game_service.log(f"{self.color}, Available Actions: {available_actions}")

        if not available_actions:
            self.game_service.pass_the_turn()
            return


        # Kural 1: Rota talep edilebiliyorsa, uzun rotalara öncelik ver, yoksa kısa rotaları talep etme olasılığını düşür.
        chosen_action = None  # Başlangıçta chosen_action'ı None olarak tanımla
        route = None  # Başlangıçta route'u None olarak tanımla

        # Kural 1: Rota talep edilebiliyorsa, uzun rotalara öncelik ver, yoksa kısa rotaları talep etme olasılığını düşür.
        if "claim_route" in available_actions:
            current_state = self.game_service.get_current_player_state()
            claimable_routes = current_state["claimable_routes"]

            # Eğer talep edilebilecek rota varsa
            if claimable_routes:
                # Uzun rotalar (6 veya daha uzun) varsa, bunları önceliklendir
                long_routes = [route for route in claimable_routes if route.length >= 6]
                if long_routes:
                    chosen_action = 'claim_route'
                    route = random.choice(long_routes)  # Uzun rotalar arasından rastgele birini seç
                else:
                    # Kısa rotaları (uzunluğu 6'dan az olan) talep etme olasılığını %20'ye düşür
                    if random.random() < 0.2:
                        chosen_action = 'claim_route'
                        route = random.choice(claimable_routes)  # Kısa rotalar arasından rastgele birini seç
                    elif "draw_train_card" in available_actions:  # Uzun rota yoksa ve kısa rota seçmeme şansı tutmadıysa, kart çek
                        chosen_action = 'draw_train_card'
                    else:
                        chosen_action = random.choice(available_actions)  # Diğer durumlarda rastgele eylem seç

                # EĞER chosen_action claim_route ise ve route None ise, claimable_routes'dan rastgele seç:
                if chosen_action == 'claim_route' and route is None:
                    route = random.choice(claimable_routes)

            else:
                if "draw_train_card" in available_actions:
                    chosen_action = 'draw_train_card'
                else:
                    chosen_action = random.choice(available_actions) # Talep edilebilecek rota yoksa kart çek

        # Kural 3: Yukarıdaki kurallar uygulanmıyorsa, mevcut eylemler arasından rastgele birini seç.
        if chosen_action is None:
            chosen_action = random.choice(available_actions)

        print(f"AI: {self.color} COLORED AGENT SELECTED THIS ACTION: {chosen_action}")

        # Seçilen eylemi gerçekleştir
        if chosen_action == 'draw_train_card':
            self.draw_train_card()
            print(f"AI: {self.color} COLORED AI has competed DRAWING TRAIN CARD successfully")
        elif chosen_action == 'draw_destination_ticket':
            self.draw_destination_ticket()
            print(f"AI: {self.color} COLORED AI has competed DRAWING DESTINATION TICKET CARD successfully")
        elif chosen_action == 'claim_route':
            self.claim_route(route)
            print(f"AI: {self.color} COLORED AI has competed CLAIMING ROUTE successfully")

    def draw_train_card(self):
        """
           Tren kartı çekme eylemini gerçekleştirir.
           Öncelikle masadaki joker kartları, sonra görev biletleri için gerekli renkleri,
           sonra da desteden kör çekiliş yapmayı dener.
           Eğer destede yeterli kart yoksa, masadaki kartlardan rastgele birini seçer.
       """
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]
        current_player_state = self.game_service.get_current_player_state()
        destination_tickets = current_player_state["destination_cards"]

        # Kural 1: Masada joker kart varsa, onu seç.
        joker_cards = [card for card in train_cards_on_the_table if card.color == "joker"]
        if joker_cards:
            selected_card = joker_cards[0]
            action_params = {"selected_card": selected_card}
            print("AI: SELECTED CARD BY AI: JOKER")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"AI drawed {selected_card.color} colored train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card()
            return  # Joker kart çekildiği için fonksiyondan çık

        # Kural 2: Görev biletleri için gerekli renklerde kartlar varsa, onlardan birini seç.
        needed_colors = set()
        for ticket in destination_tickets:
            for route in self.game_service.controller.game_manager.board.routes:
                if (route.city1 == ticket.city1 and route.city2 == ticket.city2) or \
                        (route.city1 == ticket.city2 and route.city2 == ticket.city1):
                    if route.color == "gray":
                        needed_colors.update(["red", "blue", "green", "yellow", "orange", "pink", "white", "black"])
                    else:
                        needed_colors.add(route.color)

        needed_cards = [card for card in train_cards_on_the_table if card.color in needed_colors]
        if needed_cards:
            selected_card = random.choice(needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for first pick: ", train_cards_on_the_table)
            print("AI: SELECTED CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"AI drawed {selected_card.color} colored train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return  # İki kart da çekildiyse fonksiyondan çık.

        # Kural 3: Destede en az üç kart varsa blind pick yap.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() > 2:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text("AI drawed from blind pick")
            self.game_service.log(f"{self.color}, Action: DRAW BLIND CARD")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return  # İki kart da çekildiyse fonksiyondan çık.

        # Kural 4: Destede 2 veya daha az kart varsa masadaki kartlardan rastgele birini seç.
        elif self.game_service.controller.game_manager.train_cards_deck.get_length() <= 2:
            if train_cards_on_the_table:
                selected_card = random.choice(train_cards_on_the_table)
                action_params = {"selected_card": selected_card}
                print("AI: SELECTED CARD BY AI:", selected_card.color)

                self.game_service.perform_action("draw_train_card", action_params)

                self.game_service.change_status_text(
                    f"AI drawed {selected_card.color} colored train card as an alternative action.")
                self.game_service.log(
                    f"{self.color}, Action: DRAW TRAIN CARD (Alternative), {selected_card.color}")
                self.game_service.wait_for_it(global_vars.time_action * 1000)

                # İkinci kart çekme kontrolü:
                if self.game_service.check_if_second_train_card_needed():
                    self.draw_second_train_card()
            else:
                # Destede kart yok ve masada da kart yoksa logla ve başka bir aksiyona geç.
                print("AI: Not enough cards in deck for blind pick and no cards on table, trying to claim a route.")
                self.game_service.log(
                    f"{self.color}, Action: BLIND PICK NOT AVAILABLE AND NO CARDS ON TABLE, trying to claim a route.")

                available_actions = self.game_service.get_available_actions(self.color)
                if "claim_route" in available_actions:
                    current_state = self.game_service.get_current_player_state()
                    claimable_routes = current_state["claimable_routes"]

                    if claimable_routes:
                        route = random.choice(claimable_routes)
                        self.claim_route(route)
                        print(
                            f"AI: {self.color} COLORED AI has competed CLAIMING ROUTE successfully as an alternative action")
                        return

                # Eğer başka bir şey yapılamıyorsa loglayıp fonksiyondan çık.
                print(
                    f"AI: {self.color} COLORED AI CAN'T DO ANYTHING in this turn (Not enough cards in deck, no cards on the table, and can't claim a route)")
                self.game_service.log(
                    f"{self.color}, Action: CAN'T DO ANYTHING (Insufficient cards in deck, no cards on table, and can't claim a route)")

    def draw_second_train_card(self, needed_colors=None):
        """
        İkinci tren kartını çekme işlemini gerçekleştirir.
        İkinci kart çekiminde joker seçilemez.
        Destede 3 veya daha fazla kart varsa kör çekim yapabilir.
        Masadan, görev biletleri için gerekli renklerde kartlar varsa, onlardan birini seçer.
        Eğer destede 2 veya daha az kart varsa ve masada kart varsa, masadan joker OLMAYAN rastgele bir kart çeker.
        """
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]

        # Kural 1: Masada joker kart OLSA BİLE, ikinci çekimde joker seçme.
        #         Görev biletleri için gerekli renklerde kartlar varsa, onlardan birini seç.
        needed_cards = [card for card in train_cards_on_the_table if
                        (needed_colors is None or card.color in needed_colors) and card.color != "joker"]
        if needed_cards:
            selected_card = random.choice(needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for second pick: ", train_cards_on_the_table)
            print("AI: SELECTED SECOND CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(
                f"AI drawed {selected_card.color} colored train card as second train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD (Second), {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return

        # Kural 2: Destede 3 veya daha fazla kart varsa kör çekim (blind pick) yap.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() >= 3:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED SECOND CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text("AI drawed from blind pick as second train card")
            self.game_service.log(f"{self.color}, Action: DRAW BLIND CARD (Second)")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return

        # Kural 3: Destede 2 veya daha az kart varsa ve masada kart varsa, masadan joker OLMAYAN rastgele bir kart çek.
        elif self.game_service.controller.game_manager.train_cards_deck.get_length() <= 2 and train_cards_on_the_table:
            print("AI: Not enough cards in deck for blind pick, taking a train card from table.")
            self.game_service.log(f"{self.color}, Action: BLIND PICK NOT AVAILABLE, taking a train card from table")

            # Masadan sadece joker olmayan kartları seç
            non_joker_cards = [card for card in train_cards_on_the_table if card.color != "joker"]

            if non_joker_cards:
                selected_card = random.choice(non_joker_cards)
                action_params = {"selected_card": selected_card}
                print("AI: SELECTED SECOND CARD BY AI:", selected_card.color)

                self.game_service.perform_action("draw_train_card", action_params)

                self.game_service.change_status_text(
                    f"AI drawed {selected_card.color} colored train card as an alternative action.")
                self.game_service.log(
                    f"{self.color}, Action: DRAW TRAIN CARD (Alternative Second), {selected_card.color}")
                self.game_service.wait_for_it(global_vars.time_action * 1000)
            else:
                print("AI: No valid second card options available.")
                self.game_service.log(f"{self.color}, Action: NO VALID SECOND CARD OPTION.")

    def draw_destination_ticket(self):
        """
            Yeni görev biletleri çeker.
        """
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)

        destination_card_list_without_none = []
        for card in draw_destination_card_list:
            if card is not None:
                destination_card_list_without_none.append(card)

        # En az 1, en fazla çekilen bilet sayısı kadar bilet seç (rastgele)
        number_of_cards_to_select = random.randint(1, len(destination_card_list_without_none))
        selected_cards = random.sample(destination_card_list_without_none, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)

        self.game_service.change_status_text(f"AI drawed destination ticket card.")

        log_message = f"{self.color}, Action: DESTINATION TICKET,"
        for ticket in action_params['selected_destination_tickets']:
            log_message += f" {ticket.city1} to {ticket.city2},"
        log_message = log_message.rstrip(',')
        self.game_service.log(log_message)

        self.game_service.wait_for_it(global_vars.time_action * 1000)

    def claim_route(self, route):

        if route.color == "gray":
            print("AI: A GRAY ROUTE SELECTED")
            action_params = {"selected_route": route, "use_this_color": None}
            cards_can_be_used_to_claim_gray_route = self.game_service.perform_action("claim_route", action_params)

            self.game_service.change_status_text(f"AI claiming a gray route.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # Mevcut kartlara göre gri rota için kullanılabilecek renklerden birini seç
            current_player_state = self.game_service.get_current_player_state()
            train_cards = current_player_state["train_cards"]
            available_colors = []
            joker_count = sum(1 for card in train_cards if card.color == "joker")

            for card_color in ["red", "blue", "green", "yellow", "orange", "pink", "white", "black"]:
                color_count = sum(1 for card in train_cards if card.color == card_color)
                # Yeterli sayıda renkli kart varsa veya renkli kartlar + joker kartlar yeterliyse
                if color_count >= route.length or color_count + joker_count >= route.length:
                    available_colors.append(card_color)

            # Eğer kullanılabilecek renk varsa, bunlar arasından rastgele birini seç
            if available_colors:
                use_random_color = random.choice(available_colors)

                # Seçilen renkten yeterli kart yoksa, joker kartları kullan
                color_count = sum(1 for card in train_cards if card.color == use_random_color)
                if color_count < route.length:
                    needed_jokers = route.length - color_count
                    use_random_color_with_jokers = f"{use_random_color} with {needed_jokers} jokers"
                else:
                    use_random_color_with_jokers = use_random_color

                # Seçilen renkle gri rotayı talep et
                action_params = {"selected_route": route, "use_this_color": use_random_color_with_jokers}
                self.game_service.perform_action("claim_route", action_params)

                self.game_service.change_status_text(f"AI claimed a gray route with {use_random_color_with_jokers}")
                self.game_service.log(
                    f"{self.color}, Action: CLAIM GRAY ROUTE, {route.city1} to {route.city2}, {use_random_color_with_jokers}")
                self.game_service.wait_for_it(global_vars.time_action * 1000)
            else:
                # Yeterli kart yoksa, başka bir eylem seç
                self.game_service.change_status_text(f"AI can't claim gray route due to insufficient cards.")
                self.game_service.log(f"{self.color}, Action: CAN'T CLAIM GRAY ROUTE, insufficient cards.")
                self.game_service.wait_for_it(global_vars.time_action * 1000)

                # Alternatif eylem seçimi:
                available_actions = self.game_service.get_available_actions(self.color)
                if "draw_train_card" in available_actions:
                    self.draw_train_card()
                    print(
                        f"AI: {self.color} COLORED AI has completed DRAWING TRAIN CARD successfully as an alternative action")
                elif "draw_destination_ticket" in available_actions:
                    self.draw_destination_ticket()
                    print(
                        f"AI: {self.color} COLORED AI has completed DRAWING DESTINATION TICKET CARD successfully as an alternative action")
                else:
                    print(f"AI: {self.color} COLORED AI CAN'T DO ANYTHING in this turn")

        else:
            # Renkli rotalar için kod aynı kalır
            print("AI: A COLORED ROUTE SELECTED")
            action_params = {"selected_route": route, "use_this_color": None}
            self.game_service.perform_action("claim_route", action_params)

            self.game_service.change_status_text(f"AI claimed a colored route.")
            self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {route.city1} to {route.city2}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)



