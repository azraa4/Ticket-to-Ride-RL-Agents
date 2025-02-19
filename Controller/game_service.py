from Model.DQNModel.dqn_agent import DQNAgent
from Model.agent_qlearning_basic import QLearningAgent
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

        return game_state

    def get_current_player_state(self):
        claimable_routes = self.controller.get_claimable_routes()
        train_cards = self.controller.get_current_player().train_cards
        destination_cards = self.controller.get_current_player().destination_tickets
        current_score = self.controller.get_current_player().points
        remaining_cars = self.controller.get_current_player().train_cars
        claimed_routes = self.controller.get_current_player().claimed_routes

        current_player_state = {
            "claimable_routes": claimable_routes,
            "train_cards": train_cards,
            "destination_cards": destination_cards,
            "current score": current_score,
            "remaining cars": remaining_cars,
            "claimed routes": claimed_routes,
        }

        #console print("CURRENT PLAYER STATE: ", current_player_state)
        return current_player_state

    def get_available_actions(self, player_color):
        player = self.controller.get_player_by_color(player_color)
        if player is None:
            print("!        ERROR: Player not found. Color must be written as Red, Blue, Green etc.")
            return
        if player != self.controller.get_current_player():
            print(f"!        ERROR: No available actions since it is not {player.color}'s turn")
            return

        available_actions = []
        if self.controller.get_claimable_routes():
            available_actions.append("claim_route")

        if self.controller.can_draw_destination_ticket():
            available_actions.append("draw_destination_ticket")

        if not self.controller.game_manager.all_cards_on_the_players_hands:
            available_actions.append("draw_train_card")


        #console print("AVAILABLE ACTIONS CALLED: ", available_actions)
        return available_actions

    def get_destination_tickets_list_at_the_start_of_the_game(self):
        '''
        Burda oyunun başında açılan destination ticket seçme ekranındaki kartların listesi dönüyor.
        Oyun başında ilk perform action AI'ın kesinlikle draw destination cards olması lazım.
        Ama oyunun başındaki ekranda çıkan draw destination card listesine nerden ulaşacak.
        İşte tam olarak bu metodu kullanarak ulaşabilir.
        '''
        return self.controller.game_start_destination_tickets_list_for_ai

    def check_if_second_train_card_needed(self):
        if self.controller.draw_train_card_limit == 1:
            return True
        else:
            return False

    def perform_action(self, action, action_params):
        '''
        draw_destination_ticket seçimined ikinci aşamaya geçerken destination card biterse ikinci aşamaya geçmene izin vermiyor.
        if action not in self.get_available_actions(self.controller.get_current_player().color):
            print("!        ERROR: This action is not in the available actions list.")
        '''
        if action == "claim_route":
            '''
            Claimable routes'a baktın seçeceğin route'a karar verdin 
            Eğer düz rengi olan bir route ise action_params sadece route bilgisini alır. 
                EX: action_params = {"selected_route":route, "use_this_color":None}
            
            
            Eğer gri renkli bir route ise action_params hem route hem de route'u hangi renkle alacağını bildirmen gerekir. 
                EX: action_params = {"selected_route":route, "use_this_color":"red"}
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
            önce index belirle sonra kartı seç ve gönder agent tarafında 
                EX: action_params = {"selected_card":card1} 
                EX: action_params = {"selected_card":card2} 
                
            ÖNEMLİ NOT: Bu action bir kere alındıysa ve renkli kart seçildiyse (joker ya da blind card seçilmediyse) TEKRAR ALINMAK ZORUNDADIR
            ÇÜNKÜ: 2 renkli ya da 1 joker ya da blind carddan iki kartı görmeden seçebiliyoruz.
            Yani bir renkli aldıysam önce masaya konacak yeni kartı görmeliyim ve ikinci kartı da seçmeliyim. 
            Böylece turumu bitirmiş olurum.
            '''

            return self.controller.draw_train_card_for_ai(action_params["selected_card"])

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

    def pass_the_turn(self):
        self.controller.go_to_next_turn()

    def on_change_of_turn(self):
        '''
        Bu method her turn değiştiğinde çağrılacak.
        Bu metodu kullanarak ai turn değişti mi sıra bana geldi mi kontrolünü yaptırabilirsin.
        Sonuç olarak ai'ın sırası geldiğini bilmesi ve sırası geldiğinde burdaki işlemleri gerçekleştirmesi lazım.
        '''


        ai_list = self.controller.get_ai_list()
        current_color = self.controller.get_current_player().color
        for agent in ai_list:
            if agent.color == current_color:
                if not self.controller.get_game_end():
                    agent.perform_action()

        #console print("AI: AI informed about turn change.")
        return

    def change_status_text(self, text):
        self.controller.change_status_text(text)

    def log(self, text):
        self.controller.log(text)

    def wait_for_it(self, time_ms):
        """Simulate waiting for a specified time in milliseconds."""
        import time
        end_time = time.time() + (time_ms / 1000)
        while time.time() < end_time:
            self.controller.view.root.update_idletasks()
            self.controller.view.root.update()

    def run_at_game_end(self):
        for ai in self.controller.get_ai_list():
            if isinstance(ai, QLearningAgent):
                ai.save_q_table()

        for ai in self.controller.get_ai_list():
            if isinstance(ai, DQNAgent):
                for player in self.controller.get_players():
                    if player.color == ai.color:
                        if player.has_longest_road:
                            ai.apply_final_reward(player.calculate_destination_gains()+10)
                        else:
                            ai.apply_final_reward(player.calculate_destination_gains())

                # 1) Update the target model
                ai.update_target_model()
                # 2) Save the model (weights, optimizer, replay buffer)
                ai.save_model()

    def get_availability_of_blind_pick(self):
        if self.controller.game_manager.train_cards_deck.get_length() <= 4:
            return False
        return True