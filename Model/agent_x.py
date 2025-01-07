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

        # Oyun bittiyse hiçbir şey yapma
        if self.game_service.get_game_state()["game_ended"]:
            return

        print("GAME ENDED OR NOT ::::::::" , self.game_service.get_game_state()["game_ended"])

        print(f"------------{self.color} COLORED AI PERFORMING ACTION---------------")

        # Oyunun Başlangıcında Hedef Biletleri Seçme
        if self.first_time_bool:
            print(f"AI: {self.color} 'S FIRST ROUND SO PICKING A DESTINATION TICKET")
            self.first_time_bool = False

            # Oyunun başında en az 2, en fazla 3 bilet seç (rastgele)
            tickets = self.game_service.get_destination_tickets_list_at_the_start_of_the_game()
            selected_tickets = random.sample(tickets, k=random.randint(2, 3))
            action_params = {"selected_destination_tickets": selected_tickets}
            self.game_service.perform_action("draw_destination_ticket", action_params)

            # Log
            log_message = f"{self.color}, Action: DESTINATION TICKET,"
            for ticket in selected_tickets:
                log_message += f" {ticket.city1} to {ticket.city2},"
            log_message = log_message.rstrip(',')
            self.game_service.log(log_message)

            # İlk turun sonunda turnu kapatıyoruz
            self.game_service.change_status_text(f"{self.color} drawed destination ticket card.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            self.game_service.change_status_text("TURN CHANGED.")
            return

        # Mevcut turda yapılabilecek eylemleri al
        available_actions = self.game_service.get_available_actions(self.color)
        print(f"AI: {self.color} available actions: {available_actions}")
        self.game_service.log(f"{self.color}, Available Actions: {available_actions}")

        # Eğer hiçbir aksiyon yapılamıyorsa, pas geç
        if not available_actions:
            print(f"AI: No available actions for {self.color}, passing turn.")
            self.game_service.log(f"{self.color}, Action: PASS_TURN")
            self.game_service.pass_the_turn()
            return

        # Aşağıda "chosen_action" ve "route" değişkenlerini belirleyeceğiz.
        chosen_action = None
        route = None

        # Kural 1: Rota talep edilebiliyorsa, uzun rotalara (>=6) öncelik ver.
        # Yoksa, kısa rotaları talep etme olasılığını %20'ye düşür.
        if "claim_route" in available_actions:
            current_state = self.game_service.get_current_player_state()
            claimable_routes = current_state["claimable_routes"]

            if claimable_routes:
                long_routes = [r for r in claimable_routes if r.length >= 6]
                if long_routes:
                    chosen_action = 'claim_route'
                    route = random.choice(long_routes)
                else:
                    # Kısa rota talep etme şansımız %20
                    if random.random() < 0.2:
                        chosen_action = 'claim_route'
                        route = random.choice(claimable_routes)
                    elif "draw_train_card" in available_actions:
                        chosen_action = 'draw_train_card'
                    else:
                        chosen_action = random.choice(available_actions)

                # Eğer claim_route seçilmiş ama route hâlâ None ise rastgele seç
                if chosen_action == 'claim_route' and route is None:
                    route = random.choice(claimable_routes)
            else:
                # Talep edilebilecek rota yoksa eğer possible 'draw_train_card'
                if "draw_train_card" in available_actions:
                    chosen_action = 'draw_train_card'
                else:
                    chosen_action = random.choice(available_actions)
        else:
            # Kural 3: Yukarıdaki kurallar uygulanmıyorsa, mevcut eylemler arasından rastgele birini seç
            if chosen_action is None:
                chosen_action = random.choice(available_actions)

        self.game_service.log(f"{chosen_action}")
        print(f"AI: {self.color} COLORED AGENT SELECTED THIS ACTION: {chosen_action}")

        # Seçilen eylemi gerçekleştir
        if chosen_action == 'draw_train_card':
            self.draw_train_card()
            print(f"AI: {self.color} COLORED AI has completed DRAWING TRAIN CARD successfully")
            self.game_service.change_status_text("TURN CHANGED.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

        elif chosen_action == 'draw_destination_ticket':
            self.draw_destination_ticket()
            print(f"AI: {self.color} COLORED AI has completed DRAWING DESTINATION TICKET CARD successfully")
            self.game_service.change_status_text("TURN CHANGED.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

        elif chosen_action == 'claim_route':
            self.claim_route(route)
            print(f"AI: {self.color} COLORED AI has completed CLAIMING ROUTE (or attempted)")

            # Turnu kapat
            self.game_service.change_status_text("TURN CHANGED.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

    # -----------------------------------------------------------------------
    #                           DRAW TRAIN CARD
    # -----------------------------------------------------------------------
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

        # Kural 1: Masada joker kart varsa, onu seç (birinci kart olarak).
        joker_cards = [card for card in train_cards_on_the_table if card.color == "joker"]
        if joker_cards:
            selected_card = joker_cards[0]
            action_params = {"selected_card": selected_card}
            print("AI: SELECTED CARD BY AI: JOKER")
            returned_item = self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drawed {selected_card.color} colored train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card()
            return

        # Kural 2: Görev biletleri (destination_tickets) için gerekli renkleri belirle.
        needed_colors = set()
        for ticket in destination_tickets:
            for route in self.game_service.controller.game_manager.board.routes:
                if (
                    (route.city1 == ticket.city1 and route.city2 == ticket.city2) or
                    (route.city1 == ticket.city2 and route.city2 == ticket.city1)
                ):
                    if route.color == "gray":
                        needed_colors.update(["red", "blue", "green", "yellow", "orange", "pink", "white", "black"])
                    else:
                        needed_colors.add(route.color)

        # Masada, bu gerekli renklerden birini taşıyan kart varsa, onu çek
        needed_cards = [card for card in train_cards_on_the_table if card.color in needed_colors]
        if needed_cards:
            selected_card = random.choice(needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for first pick: ", train_cards_on_the_table)
            print("AI: SELECTED CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drawed {selected_card.color} colored train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return

        # Kural 3: Destede 4 veya daha fazla kart varsa blind pick yap.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() > 4:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drawed from blind pick")
            self.game_service.log(f"{self.color}, Action: DRAW BLIND CARD")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # İkinci kart çekme kontrolü:
            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return

        # Kural 4: Destede 2 veya daha az kart varsa masadaki kartlardan rastgele birini seç.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() <= 4:
            if train_cards_on_the_table:
                selected_card = random.choice(train_cards_on_the_table)
                action_params = {"selected_card": selected_card}
                print("AI: SELECTED CARD BY AI:", selected_card.color)

                self.game_service.perform_action("draw_train_card", action_params)

                self.game_service.change_status_text(
                    f"{self.color} drawed {selected_card.color} colored train card as an alternative action."
                )
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD (Alternative), {selected_card.color}")
                self.game_service.wait_for_it(global_vars.time_action * 1000)

                # İkinci kart çekme kontrolü:
                if self.game_service.check_if_second_train_card_needed():
                    self.draw_second_train_card()
            else:
                # Destede kart yok ve masada da kart yoksa
                print("AI: Not enough cards in deck for blind pick and no cards on table, turning to claim_route or pass.")
                self.game_service.log(
                    f"{self.color}, Action: BLIND PICK NOT AVAILABLE AND NO CARDS ON TABLE, trying to claim a route."
                )

                # Mümkünse route talep etmeyi dene
                available_actions = self.game_service.get_available_actions(self.color)
                if "claim_route" in available_actions:
                    current_state = self.game_service.get_current_player_state()
                    claimable_routes = current_state["claimable_routes"]
                    if claimable_routes:
                        route = random.choice(claimable_routes)
                        self.claim_route(route)
                        print(
                            f"AI: {self.color} COLORED AI has completed CLAIMING ROUTE successfully as an alternative action"
                        )
                        return

                # Başka bir şey yapılamıyorsa
                print(
                    f"AI: {self.color} COLORED AI CAN'T DO ANYTHING in this turn (Not enough cards in deck, no cards on the table, and can't claim a route)"
                )
                self.game_service.log(
                    f"{self.color}, Action: CAN'T DO ANYTHING (Insufficient cards in deck, no cards on table, and can't claim a route)"
                )

    # -----------------------------------------------------------------------
    #                      DRAW SECOND TRAIN CARD
    # -----------------------------------------------------------------------
    def draw_second_train_card(self, needed_colors=None):
        """
        İkinci tren kartını çekme işlemini gerçekleştirir.
        İkinci kart çekiminde joker seçilemez.
        Destede 3 veya daha fazla kart varsa kör çekim yapabilir.
        Masadan, görev biletleri için gerekli renklerde kartlar varsa, onlardan birini seçer.
        """

        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]

        # Kural 1: Görev biletleri için gerekli renklerde joker OLMAYAN kartları bul
        non_joker_needed_cards = [
            card
            for card in train_cards_on_the_table
            if (needed_colors is None or card.color in needed_colors) and card.color != "joker"
        ]
        if non_joker_needed_cards:
            selected_card = random.choice(non_joker_needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for second pick: ", train_cards_on_the_table)
            print("AI: SELECTED SECOND CARD BY AI:", selected_card.color)

            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(
                f"{self.color} drawed {selected_card.color} colored train card as second train card."
            )
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD (Second), {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return

        '''
        # Kural 2: Destede 3 veya daha fazla kart varsa blind pick yap
        if self.game_service.controller.game_manager.train_cards_deck.get_length() >= 3:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED SECOND CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text("AI drawed from blind pick as second train card")
            self.game_service.log(f"{self.color}, Action: DRAW BLIND CARD (Second)")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return
        '''

        # Kural 3: Destede 2 veya daha az kart varsa ve masada kart varsa, masadan joker olmayan rastgele kart
        if self.game_service.controller.game_manager.train_cards_deck.get_length() <= 2 and train_cards_on_the_table:
            print("AI: Not enough cards in deck for blind pick, taking a train card from table.")
            self.game_service.log(f"{self.color}, Action: BLIND PICK NOT AVAILABLE, taking a train card from table")

            non_joker_cards = [card for card in train_cards_on_the_table if card.color != "joker"]
            if non_joker_cards:
                selected_card = random.choice(non_joker_cards)
                action_params = {"selected_card": selected_card}
                print("AI: SELECTED SECOND CARD BY AI:", selected_card.color)

                self.game_service.perform_action("draw_train_card", action_params)

                self.game_service.change_status_text(
                    f"{self.color} drawed {selected_card.color} colored train card as alternative second card."
                )
                self.game_service.log(
                    f"{self.color}, Action: DRAW TRAIN CARD (Alternative Second), {selected_card.color}"
                )
                self.game_service.wait_for_it(global_vars.time_action * 1000)
            else:
                print("AI: No valid second card options available.")
                self.game_service.log(f"{self.color}, Action: NO VALID SECOND CARD OPTION.")

    # -----------------------------------------------------------------------
    #                   DRAW DESTINATION TICKET
    # -----------------------------------------------------------------------
    def draw_destination_ticket(self):
        """
        Yeni görev biletleri çeker ve bunlardan en az 1, en fazla gelen bilet sayısı kadar seçer.
        """
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)

        # Filtrele
        destination_card_list_without_none = [
            card for card in draw_destination_card_list if card is not None
        ]

        if not destination_card_list_without_none:
            print("AI: No valid destination tickets drawn.")
            self.game_service.log(f"{self.color}, Action: DRAW DESTINATION TICKET - NO CARDS")
            return

        # En az 1, en fazla çekilen bilet sayısı kadar bilet seç (rastgele)
        number_of_cards_to_select = random.randint(1, len(destination_card_list_without_none))
        selected_cards = random.sample(destination_card_list_without_none, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)

        self.game_service.change_status_text(f"{self.color} drawed destination ticket card.")

        log_message = f"{self.color}, Action: DESTINATION TICKET,"
        for ticket in action_params['selected_destination_tickets']:
            log_message += f" {ticket.city1} to {ticket.city2},"
        log_message = log_message.rstrip(',')
        self.game_service.log(log_message)

        self.game_service.wait_for_it(global_vars.time_action * 1000)

    # -----------------------------------------------------------------------
    #                         CLAIM ROUTE
    # -----------------------------------------------------------------------
    def claim_route(self, route):
        """
        Belirlenen rotayı talep etmeye çalışır.
       - Eğer gri rota ise, önce "use_this_color": None ile hangi renklerin uygun olduğunu öğreniyoruz.
         Sonrasında servisin döndürdüğü renk listesinden rasgele bir renk seçip tekrar "claim_route" yapıyoruz.
       - Eğer rota renkli ise doğrudan talep ediyoruz.
        """
        if not route:
            print("AI: No route provided to claim.")
            self.game_service.log(f"{self.color}, Action: CLAIM ROUTE - NO ROUTE")
            return

        # Gri rota
        if route.color == "gray":
            print("AI: A GRAY ROUTE SELECTED")
            # 1) İlk önce "use_this_color": None ile aksiyon yapıp, servisin hangi renkleri kullanabileceğini öğreniyoruz
            action_params = {"selected_route": route, "use_this_color": None}
            cards_can_be_used = self.game_service.perform_action("claim_route", action_params)

            # Eğer buradan 0 dönerse rota talebi tamamen başarısız olabilir.
            # Yine de game_service hangi bilgileri dönüyor bakın. Örneğin "cards_can_be_used" = []
            self.game_service.change_status_text(f"{self.color} claiming a gray route.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            # Eğer hiç kullanılabilir renk dönmezse => kart yetersizliği vb. durumdan dolayı talep edilemedi
            if not cards_can_be_used:
                self.game_service.change_status_text(f"{self.color} can't claim gray route - insufficient cards maybe.")
                self.game_service.log(f"{self.color}, Action: CAN'T CLAIM GRAY ROUTE, insufficient cards.")
                return  # Turn bitecek

            # Mevcut kartlara göre gri rota için kullanılabilecek renklerden birini rastgele seçelim
            # (Testlerden dönen "cards_can_be_used" doğrudan listeyse, onu da kullanabilirsiniz.)
            current_player_state = self.game_service.get_current_player_state()
            train_cards = current_player_state["train_cards"]
            route_length = route.length

            # Renkli kart adedi + joker adedi >= route.length ise o renk uygundur.
            joker_count = sum(1 for c in train_cards if c.color == "joker")
            candidate_colors = ["red", "blue", "green", "yellow", "orange", "pink", "white", "black"]
            possible_colors = []
            for c in candidate_colors:
                color_count = sum(1 for card in train_cards if card.color == c)
                if color_count >= route_length or (color_count + joker_count) >= route_length:
                    possible_colors.append(c)

            if not possible_colors:
                # Yeterli kart yoksa, eylem başarısız
                self.game_service.change_status_text(f"{self.color} can't claim gray route due to insufficient cards.")
                self.game_service.log(f"{self.color}, Action: CAN'T CLAIM GRAY ROUTE, insufficient cards.")
                return

            use_random_color = random.choice(possible_colors)
            color_count = sum(1 for card in train_cards if card.color == use_random_color)
            if color_count < route_length:
                needed_jokers = route_length - color_count
                use_random_color_with_jokers = f"{use_random_color} with {needed_jokers} jokers"
            else:
                use_random_color_with_jokers = use_random_color

            action_params = {"selected_route": route, "use_this_color": use_random_color_with_jokers}
            self.game_service.perform_action("claim_route", action_params)

            self.game_service.change_status_text(f"{self.color} claimed a gray route with {use_random_color_with_jokers}")
            self.game_service.log(
                f"{self.color}, Action: CLAIM GRAY ROUTE, {route.city1} to {route.city2}, {use_random_color_with_jokers}"
            )
            self.game_service.wait_for_it(global_vars.time_action * 1000)

        else:
            # Renkli rota
            print("AI: A COLORED ROUTE SELECTED")
            action_params = {"selected_route": route, "use_this_color": None}
            result = self.game_service.perform_action("claim_route", action_params)

            self.game_service.change_status_text(f"{self.color} claimed a colored route.")
            self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {route.city1} to {route.city2}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
