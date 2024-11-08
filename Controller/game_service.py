class GameService:
    def __init__(self, controller):
        self.controller = controller

    def get_game_state(self):
        current_turn_player = self.controller.get_current_player()
        is_the_next_turn_last_turn = self.controller.get_last_turn_info()
        game_ended = self.controller.get_game_end()

        claimed_routes = self.controller.get_claimed_routes()
        unclaimed_routes = self.controller.get_unclaimed_routes()

        players = [
            {
                "player_color": player.color,
                "score": player.points,
                "remaining_train_cars": player.train_cars,
                "claimed_routes": player.claimed_routes,
            } for player in self.controller.get_players()
        ]

        train_cards_on_the_table = self.controller.get_train_cards_on_the_table()

        #who has the longest road eklenebilir (muhtemelen eklenmez işi çok zorlaştırır. AI bunu bilerek düşünemez.)

        game_state = {
            "current_turn_player": current_turn_player,
            "is_the_next_turn_last_turn": is_the_next_turn_last_turn,
            "game_ended": game_ended,
            "players": players,
            "claimed_routes": claimed_routes,
            "unclaimed_routes": unclaimed_routes,
            "train_cards_on_the_table": train_cards_on_the_table,
        }

        print(game_state)

        return game_state

    def get_current_player_state(self):
        claimable_routes = self.controller.get_claimable_routes()
        train_cards = self.controller.get_current_player().train_cards
        destination_cards = self.controller.get_current_player().destination_tickets

        current_player_state = {
            "claimable_routes": claimable_routes,
            "train_cards": train_cards,
            "destination_cards": destination_cards,
        }

        print(current_player_state)
        return current_player_state

    def get_available_actions(self, player_color):
        player = self.controller.get_player_by_color(player_color)
        if player is None:
            print("Player not found. Color must be written as Red, Blue, Green etc.")
            return
        if player != self.controller.get_current_player():
            print(f"No available actions since it is not {player.color}'s turn")
            return

        available_actions = []
        if self.controller.get_claimable_routes():
            available_actions.append("claim_route")

        if self.controller.can_draw_destination_ticket():
            available_actions.append("draw_destination_ticket")

        if not self.controller.game_manager.all_cards_on_the_players_hands:
            available_actions.append("draw_train_card")


        print(available_actions)
        return available_actions

    def get_destination_tickets_list_at_the_start_of_the_game(self):
        '''
        Burda oyunun başında açılan destination ticket seçme ekranındaki kartların listesi dönüyor.
        Oyun başında ilk perform action AI'ın kesinlikle draw destination cards olması lazım.
        Ama oyunun başındaki ekranda çıkan draw destination card listesine nerden ulaşacak.
        İşte tam olarak bu metodu kullanarak ulaşabilir.
        '''
        return self.controller.game_start_destination_tickets_list_for_ai

    def perform_action(self, action, action_params):
        if action not in self.get_available_actions(self.controller.get_current_player().color):
            print("This action is not in the available actions list.")
        if action == "claim_route":
            '''
            Claimable routes'a baktın seçeceğin route'a karar verdin 
            Eğer düz rengi olan bir route ise action_params sadece route bilgisini alır. 
                EX: action_params = {"selected_route":route, "with_colors":None}
            
            
            Eğer gri renkli bir route ise action_params hem route hem de route'u hangi renkle alacağını bildirmen gerekir. 
                EX: action_params = {"selected_route":route, "with_colors":"red"}
            '''
            #self.controller.claim_route_for_ai(action_params["selected_route"], action_params["with_colors"])
            if action_params["use_this_color"] is None:
                self.controller.claim_route(action_params["selected_route"])
                return self.controller.cards_needed_to_claim_gray_route(action_params["selected_route"])
            else:
                self.controller.claim_gray_route(action_params["use_this_color"], action_params["selected_route"])

        elif action == "draw_train_card":
            '''
            Masada 6 kart var bunlardan 5'i tekli kartlar 6.sı ise blind pick yani desteden çekmek.
            Bu masadaki 6 kart seçeneği listenin indexleri olarak gözükür list = [1.kart, 2.kart, 3.kart, 4.kart, 5.kart, 6.kart(blind_pick)]  
                EX: action_params = {"selected_index":1} //masadaki 2. kartı seçer (çünkü liste 0 dan başlıyor !!!)
                EX: action_params = {"selected_index":5} //masadaki 6. kartı seçer yani blind pick (çünkü liste 0 dan başlıyor !!!)
                
            ÖNEMLİ NOT: Bu action bir kere alındıysa ve renkli kart seçildiyse (joker ya da blind card seçilmediyse) TEKRAR ALINMAK ZORUNDADIR
            ÇÜNKÜ: 2 renkli ya da 1 joker ya da blind carddan iki kartı görmeden seçebiliyoruz.
            Yani bir renkli aldıysam önce masaya konacak yeni kartı görmeliyim ve ikinci kartı da seçmeliyim. 
            Böylece turumu bitirmiş olurum.
            '''
            self.controller.draw_train_card_for_ai(action_params["selected_card"])

        elif action == "draw_destination_ticket":
            if action_params is None: #ÖNCE KARTLARI AÇIP GÖRMEN LAZIM SONRA SEÇECEKSİN
                list = self.controller.open_draw_destination_ticket_frame() #açıp gördüğümüz kartları listeye alıp sonuç olarak döndürdük
                return list
            else:
                '''
                if kısmında önce 3 kart açtık gördük.
                Ardından else kısmında bu kartlardan seçtiklerimizi belirteceğiz.
                Yani action_params kısmında bir seçili kartlar listesi döndürmeliyiz (çünkü birden fazla kart da seçilebiliyor)
                    EX: action_params = {"selected_destination_tickets" : seçilen_kartların_listesi}
                '''
                self.controller.draw_destination_ticket(action_params["selected_destination_tickets"])
                self.controller.destroy_select_destination_tickets_canvas_for_ai()

    def on_change_of_turn(self):
        '''
        Bu method her turn değiştiğinde çağrılacak.
        Bu metodu kullanarak ai turn değişti mi sıra bana geldi mi kontrolünü yaptırabilirsin.
        Sonuç olarak ai'ın sırası geldiğini bilmesi ve sırası geldiğinde burdaki işlemleri gerçekleştirmesi lazım.
        '''

        print("Turn Changed. AI informed.")
        return



