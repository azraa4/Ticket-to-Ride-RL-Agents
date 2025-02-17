import ast
import random
import json
import os

import global_vars


class RLAgent:
    def __init__(self, color, game_service):
        self.color = color
        self.game_service = game_service
        self.first_time_bool = True

        # Q-learning için hiperparametreler:
        self.epsilon = 1.0  # Başlangıç keşif oranı: Yüksek epsilon, başlangıçta daha fazla rastgele eylem seçimi sağlar.
        self.epsilon_min = 0.01  # Epsilon'un düşebileceği minimum değer
        self.epsilon_decay = 0.990  # Her epizod sonunda epsilon değerinin çarpanla azaltılması (eksponensiyel azalma)
        self.alpha = 0.3  # Öğrenme oranı (ne kadar hızlı güncelleme yapılacağı)
        self.gamma = 0.9  # İndirim (discount) faktörü: Gelecekteki ödüllerin bugünkü değerine etkisi

        # Q-table: Her durum için (string olarak temsil edilen) her eylemin Q-değerlerini tutar.
        # Örnek yapı: { "state_tuple_string": { "draw_train_card": 0.0, "claim_route": 0.0, ... }, ... }
        self.q_table = {}
        self.q_table_file = "q_table.json"  # Q-table'ın kalıcı kaydı için dosya adı
        self.load_q_table()  # Önceki eğitimden Q-table verilerini yükler

        # -------------------- Q-LEARNING İLE İLGİLİ METODLAR --------------------

    def get_state(self):
        """
        Şu anki oyuncunun durumunu alır ve bu durumu sadece sayısal özellikleri içeren bir tuple olarak özetler.
        Bu özet, Q-table'da durum olarak kullanılır.
        Özellikler:
          - Elindeki toplam tren kartı sayısı.
          - Elindeki joker kart sayısı.
          - Elindeki destinasyon kartı sayısı.
          - Talep edilmiş (claim) rota sayısı.
          - Rakiplerin en yüksek skoru.
          - Destede kalan tren kartlarının sayısı.
        """
        current_state = self.game_service.get_current_player_state()

        # Oyuncunun elindeki tren kartlarının listesini alıyoruz.
        train_cards = current_state.get("train_cards", [])
        total_train_cards = len(train_cards)
        # Joker kartların sayısını hesaplıyoruz.
        joker_count = sum(1 for card in train_cards if card.color == "joker")

        # Oyuncunun elindeki destinasyon kartlarının sayısı
        num_destination_tickets = len(current_state.get("destination_cards", []))

        # Oyuncunun claim ettiği (alınmış) rotaları sayıyoruz.
        game_state = self.game_service.get_game_state()
        current_player_color = self.game_service.controller.get_current_player().color
        claimed_routes = 0
        for player in game_state["players"]:
            if player["player_color"] == current_player_color:
                claimed_routes = len(player.get("claimed_routes", []))
                break

        # Rakiplerden en yüksek skoru alıyoruz; bu bilgi rakiplerin durumunu göz önünde bulundurmak için.
        opponent_scores = [
            player.get("score", 0)
            for player in game_state["players"]
            if player["player_color"] != current_player_color
        ]
        max_opponent_score = max(opponent_scores) if opponent_scores else 0

        # Destede kalan tren kartlarının sayısını alıyoruz.
        remaining_train_cards = self.game_service.controller.game_manager.train_cards_deck.get_length()

        # Durumu özetleyen tuple: (toplam tren kartı, joker sayısı, destinasyon kartı sayısı,
        # claim edilen rota sayısı, rakiplerden en yüksek skor, destede kalan tren kartı sayısı)
        state_tuple = (
            total_train_cards,
            joker_count,
            num_destination_tickets,
            claimed_routes,
            max_opponent_score,
            remaining_train_cards
        )

        # Q-table'da anahtar olarak kullanabilmek için tuple'ı string'e çeviriyoruz.
        return str(state_tuple)

    def get_game_stage(self):
        """
        Oyunun aşamasını belirler:
          - "late": Oyun sona ermiş veya son tur başlatılmışsa.
          - "mid": Destede kalan tren kartı sayısı belirli bir eşik değerin altındaysa.
          - "early": Aksi durumda.
        Bu aşama, ödül hesaplamalarında keşif (exploration) ve istismar (exploitation) çarpanlarını ayarlamak için kullanılır.
        """
        game_state = self.game_service.get_game_state()

        # Oyun sona ermiş veya son tur başlatılmışsa aşama 'late' olarak belirlenir.
        if game_state.get("game_ended", False) or game_state.get("is_the_next_turn_last_turn", False):
            return "late"

        # Örneğin, destede kalan tren kartı sayısı 15'in altındaysa oyunun orta aşamasında olduğumuzu varsayalım.
        remaining_cards = self.game_service.controller.game_manager.train_cards_deck.get_length()
        if remaining_cards < 15:
            return "mid"

        return "early"

    def compute_reward(self, previous_state, action, action_params, new_state):
        """
        Q-learning algoritması için eylemin sonucunda alınan ödülü hesaplar.
        Hesaplama, oyunun aşamasına göre (early, mid, late) farklı keşif ve istismar çarpanları kullanır.
        Farklı eylemlerin (claim_route, draw_train_card, draw_destination_ticket) ödül mantıkları burada belirlenir.
        """
        reward = 0
        game_stage = self.get_game_stage()

        # Oyun aşamasına göre keşif ve istismar için çarpanlar ayarlanır.
        if game_stage == "early":
            exploration_multiplier = 1.2
            exploitation_multiplier = 0.8
        elif game_stage == "mid":
            exploration_multiplier = 1.0
            exploitation_multiplier = 1.0
        elif game_stage == "late":
            exploration_multiplier = 0.7
            exploitation_multiplier = 1.3

        # Eyleme göre ödül hesaplamaları:
        if action == "claim_route":
            route = action_params.get("selected_route", None)
            if route:
                # Rota uzunluğuna bağlı ödül: Uzun rota daha yüksek ödül getirir.
                if route.length <= 2:
                    reward += route.length * 2 * exploitation_multiplier
                elif route.length <= 4:
                    reward += route.length * 3 * exploitation_multiplier
                else:
                    reward += route.length * 4 * exploitation_multiplier

                # Rotanın destinasyon biletlerini tamamlama durumuna göre ek ödül veya bonus:
                if self.game_service.is_ticket_completed_by_route(self.color, route):
                    reward += 20 * exploitation_multiplier
                elif self.game_service.is_ticket_partially_completed_by_route(self.color, route):
                    reward += 5 * exploitation_multiplier
            else:
                # Rota seçilemediyse, eylem başarısız sayılır ve ceza verilir.
                reward -= 5

        elif action == "draw_train_card":
            selected_card = action_params.get("selected_card", None)
            if selected_card is not None:
                # Joker kart çekimi genellikle değerli olduğundan ödüllendirilir.
                if selected_card.color == "joker":
                    reward += 3 * exploration_multiplier
                # Özel durum (kritik) kart çekimleri için ek ödül.
                if action_params.get("is_critical", False):
                    reward += 5 * exploration_multiplier

            # Eğer oyuncunun elinde zaten yeterli tren kartı varsa, gereksiz kart çekimi ceza getirebilir.
            claimable_routes = self.game_service.controller.get_claimable_routes()
            if claimable_routes:
                max_route_length = max(route.length for route in claimable_routes)
                if self.has_many_train_cards(previous_state, max_route_length):
                    reward -= 2 * exploration_multiplier

        elif action == "draw_destination_ticket":
            drawn_tickets = action_params.get("selected_destination_tickets", [])
            # Eğer çekilen biletlerden herhangi biri neredeyse tamamlanabiliyorsa ödül verilir.
            for ticket in drawn_tickets:
                if self.game_service.is_ticket_almost_completable(self.color, ticket):
                    reward += 5 * exploitation_multiplier
                    break  # Sadece ilk bilet ödüllendirilir.

        # Oyun sona erdiğinde, tamamlanmış biletlerden pozitif, tamamlanmamışlardan negatif ödül alınır.
        if self.game_service.get_game_state()["game_ended"]:
            current_player = self.game_service.controller.get_current_player()
            unfinished_tickets = 0
            for ticket in current_player.destination_tickets:
                if self.game_service.is_ticket_completed(ticket):
                    reward += ticket.value * exploitation_multiplier
                else:
                    unfinished_tickets += 1
                    if unfinished_tickets == 1:
                        reward -= ticket.value * exploitation_multiplier
                    elif unfinished_tickets == 2:
                        reward -= 1.2 * ticket.value * exploitation_multiplier
                    else:
                        reward -= 1.5 * ticket.value * exploitation_multiplier

        return reward


    def has_many_train_cards(self, state, max_route_length):
        """
        Bu metot, 'state' parametresini ayrıştırarak oyuncunun elindeki toplam tren kartı sayısını hesaplar.
        Eğer toplam kart sayısı 10'dan fazlaysa True döner.
        Bu bilgi, gerekirse kart çekme eylemine ceza verilmesi için kullanılır.
        """
        try:
            # Güvenli şekilde string'den tuple'a dönüştürüyoruz.
            parsed_state = ast.literal_eval(state)
            # Tuple'ın ilk elemanı, oyuncunun tren kartlarının sayıları bilgisi içeriyor.
            train_card_counts_items = parsed_state[0]
            total_cards = sum(count for (_, count) in train_card_counts_items)
            return total_cards > 10
        except Exception as e:
            print("has_many_train_cards metodunda durum ayrıştırılırken hata oluştu:", e)
            return False

    def choose_action(self, state, available_actions):
        """
        ε-greedy (epsilon-greedy) stratejisiyle eylem seçimi yapar:
          - Belirli bir epsilon olasılığıyla rastgele eylem seçer (keşif).
          - Aksi takdirde Q-table'da en yüksek Q-değerine sahip eylemi seçer (istismar).
        """
        if not available_actions:
            return None

        # Eğer bu durum Q-table'da yoksa, mevcut tüm eylemler için başlangıç değeri 0.0 atanır.
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in available_actions}

        if random.random() < self.epsilon:
            chosen_action = random.choice(available_actions)
        else:
            max_q_value = max(self.q_table[state].values())
            # En iyi Q-değerine sahip eylemlerden rastgele seçim yapılır.
            best_actions = [action for action, q_value in self.q_table[state].items() if q_value == max_q_value]
            chosen_action = random.choice(best_actions)

        return chosen_action

    def update_q_value(self, state, action, reward, next_state, next_available_actions):
        """
        Q-learning güncelleme formülünü uygular:
          Q(s,a) = Q(s,a) + α * [ r + γ * maxₐ' Q(s',a') - Q(s,a) ]
        Bu sayede ajan, her durum-eylem çifti için ödül beklentisini günceller.
        """
        if state not in self.q_table:
            self.q_table[state] = {}

        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0

        # Eğer sonraki durum Q-table'da yoksa, mevcut eylemler için başlangıç değeri 0.0 atanır.
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in next_available_actions} if next_available_actions else {}

        max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        current_q = self.q_table[state][action]
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

    def decay_epsilon(self):
        """
        Her epizod sonunda epsilon değerini azaltır.
        Bu, eğitim ilerledikçe keşif oranını düşürüp istismara (en iyi bilinen eylemleri seçmeye)
        yönlendirmek için kullanılır.
        """
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def load_q_table(self):
        """
        Q-table verilerini JSON dosyasından yükler.
        Eğer dosya mevcut değilse veya hata oluşursa boş bir Q-table oluşturulur.
        """
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, "r") as f:
                    self.q_table = json.load(f)
            except Exception as e:
                print("Q-table yüklenirken hata oluştu:", e)
                self.q_table = {}
        else:
            self.q_table = {}

    def save_q_table(self):
        """
        Güncel Q-table verilerini JSON dosyasına kaydeder.
        Bu, eğitim sürecinin devamlılığı açısından önemlidir.
        """
        try:
            with open(self.q_table_file, "w") as f:
                json.dump(self.q_table, f)
        except Exception as e:
            print("Q-table kaydedilirken hata oluştu:", e)

        # -------------------- Ajanın EYLEM FONKSİYONU --------------------
    def perform_action(self):
        """
        Her turda çağrılır. İşlem sırası:
          1. Oyun sona erdiyse hiçbir şey yapmaz.
          2. İlk turda (first_time_bool True iken) destinasyon biletleri çekilir.
          3. Sonraki turlarda Q-table kullanılarak ε-greedy stratejisi ile eylem seçilir.
          4. Seçilen eylem gerçekleştirilir (örneğin, draw_train_card, claim_route vb.).
          5. Eylem sonrası yeni durum hesaplanır, ödül alınır ve Q-değer güncellemesi yapılır.
          6. Epsilon değeri düşürülerek gelecek turda daha istismar odaklı seçim yapılır.
        """
        # Eğer oyun bitti ise eylem gerçekleştirme.
        if self.game_service.get_game_state()["game_ended"]:
            return

        # İlk turda, ajan sabit (kural tabanlı) olarak destinasyon biletleri çeker.
        if self.first_time_bool:
            print(f"AI: {self.color}'S FIRST ROUND SO PICKING A DESTINATION TICKET")
            self.first_time_bool = False

            # Oyunun başlangıcında 2 ila 3 bilet çekilir.
            tickets = self.game_service.get_destination_tickets_list_at_the_start_of_the_game()
            selected_tickets = random.sample(tickets, k=random.randint(2, 3))
            action_params = {"selected_destination_tickets": selected_tickets}
            self.game_service.perform_action("draw_destination_ticket", action_params)

            # Loglama: Seçilen biletleri yazdır.
            log_message = f"{self.color}, Action: DESTINATION TICKET,"
            for ticket in selected_tickets:
                log_message += f" {ticket.city1} to {ticket.city2},"
            log_message = log_message.rstrip(',')
            self.game_service.log(log_message)

            self.game_service.change_status_text(f"{self.color} drew destination ticket card.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return

        # Mevcut durum alınır ve mevcut eylemler belirlenir.
        state = self.get_state()
        available_actions = self.game_service.get_available_actions(self.color)
        self.game_service.log(f"{self.color}, Available Actions: {available_actions}")

        # Eğer hiçbir eylem mevcut değilse, tur pas geçilir.
        if not available_actions:
            print(f"AI: No available actions for {self.color}, passing turn.")
            self.game_service.log(f"{self.color}, Action: PASS_TURN")
            self.game_service.pass_the_turn()
            return

        # Q-table'da mevcut durum için eylemler yoksa eklenir.
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in available_actions}
        else:
            for action in available_actions:
                if action not in self.q_table[state]:
                    self.q_table[state][action] = 0.0

        # ε-greedy stratejisi: Rastgele seçim (keşif) veya en yüksek Q-değerli eylem (istismar)
        if random.random() < self.epsilon:
            chosen_action = random.choice(available_actions)
            print(f"AI: {self.color} selected RANDOM action: {chosen_action}")
        else:
            chosen_action = max(self.q_table[state], key=self.q_table[state].get)
            if chosen_action not in available_actions:
                chosen_action = random.choice(available_actions)
            print(f"AI: {self.color} selected Q-LEARNING action: {chosen_action}")

        self.game_service.log(f"{self.color}, Chosen Action: {chosen_action}")

        # Seçilen eyleme göre ilgili metot çağrılır.
        if chosen_action == 'draw_train_card':
            self.draw_train_card()
        elif chosen_action == 'draw_destination_ticket':
            self.draw_destination_ticket()
        elif chosen_action == 'claim_route':
            # Rota talep etme: Mevcut claimable_routes listesinden rastgele bir rota seçilir.
            current_state = self.game_service.get_current_player_state()
            claimable_routes = current_state.get("claimable_routes", [])
            if claimable_routes:
                route = random.choice(claimable_routes)
                self.claim_route(route)
            else:
                print(f"AI: No claimable routes available for {self.color}, passing turn.")
                self.game_service.pass_the_turn()
        elif chosen_action == 'pass_turn':
            self.game_service.pass_the_turn()
        else:
            # Eğer bilinmeyen bir eylem seçilmişse, fallback olarak rastgele bir eylem gerçekleştirilir.
            fallback_action = random.choice(available_actions)
            self.game_service.log(f"{self.color}, Unknown action chosen. Falling back to {fallback_action}")
            if fallback_action == 'draw_train_card':
                self.draw_train_card()
            elif fallback_action == 'draw_destination_ticket':
                self.draw_destination_ticket()
            elif fallback_action == 'claim_route':
                current_state = self.game_service.get_current_player_state()
                claimable_routes = current_state.get("claimable_routes", [])
                if claimable_routes:
                    route = random.choice(claimable_routes)
                    self.claim_route(route)
                else:
                    self.game_service.pass_the_turn()
            else:
                self.game_service.pass_the_turn()

        # Eylem gerçekleştirildikten sonra yeni durum alınır ve ödül hesaplanır.
        new_state = self.get_state()
        reward = self.compute_reward(state, chosen_action, {}, new_state)

        # Q-learning güncelleme adımı: Q-değeri güncellenir.
        old_value = self.q_table.get(state, {}).get(chosen_action, 0.0)
        max_next = max(self.q_table[new_state].values()) if new_state in self.q_table and self.q_table[
            new_state] else 0.0
        updated_value = old_value + self.alpha * (reward + self.gamma * max_next - old_value)
        self.q_table[state][chosen_action] = updated_value
        self.save_q_table()  # Q-table dosyaya kaydedilir

        # Epsilon değeri düşürülerek ajan daha çok istismar yapmaya yönlendirilir.
        self.decay_epsilon()

        # Tur sonu güncellemesi
        self.game_service.change_status_text("TURN CHANGED.")
        self.game_service.wait_for_it(global_vars.time_action * 1000)


    def draw_train_card(self):
        """
        Tren kartı çekme eylemini gerçekleştirir.
        Önce masadaki joker kartları, sonra görev biletleri için gerekli renkleri,
        ardından desteden kör çekim yapmayı dener.
        """
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]
        current_player_state = self.game_service.get_current_player_state()
        destination_tickets = current_player_state["destination_cards"]

        # Kural 1: Masada joker kart varsa, onu seç (ilk kart)
        joker_cards = [card for card in train_cards_on_the_table if card.color == "joker"]
        if joker_cards:
            selected_card = joker_cards[0]
            action_params = {"selected_card": selected_card}
            print("AI: SELECTED CARD BY AI: JOKER")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drew {selected_card.color} train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card()
            return

        # Kural 2: Görev biletleri için gerekli renkleri belirle.
        needed_colors = set()
        for ticket in destination_tickets:
            for route in self.game_service.controller.game_manager.board.routes:
                if ((route.city1 == ticket.city1 and route.city2 == ticket.city2) or
                    (route.city1 == ticket.city2 and route.city2 == ticket.city1)):
                    if route.color == "gray":
                        needed_colors.update(["red", "blue", "green", "yellow", "orange", "pink", "white", "black"])
                    else:
                        needed_colors.add(route.color)

        needed_cards = [card for card in train_cards_on_the_table if card.color in needed_colors]
        if needed_cards:
            selected_card = random.choice(needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for first pick:", train_cards_on_the_table)
            print("AI: SELECTED CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drew {selected_card.color} train card.")
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD, {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return

        # Kural 3: Destede 4 veya daha fazla kart varsa blind pick yap.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() > 4:
            action_params = {"selected_card": "select_blind"}
            print("AI: SELECTED CARD BY AI: BLIND PICK")
            self.game_service.perform_action("draw_train_card", action_params)

            self.game_service.change_status_text(f"{self.color} drew from blind pick")
            self.game_service.log(f"{self.color}, Action: DRAW BLIND CARD")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            if self.game_service.check_if_second_train_card_needed():
                self.draw_second_train_card(needed_colors)
            return

        # Kural 4: Destede 2 veya daha az kart varsa, masadaki kartlardan rastgele seç.
        if self.game_service.controller.game_manager.train_cards_deck.get_length() <= 4:
            if train_cards_on_the_table:
                selected_card = random.choice(train_cards_on_the_table)
                action_params = {"selected_card": selected_card}
                print("AI: SELECTED CARD BY AI:", selected_card.color)
                self.game_service.perform_action("draw_train_card", action_params)

                self.game_service.change_status_text(
                    f"{self.color} drew {selected_card.color} train card as an alternative action."
                )
                self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD (Alternative), {selected_card.color}")
                self.game_service.wait_for_it(global_vars.time_action * 1000)

                if self.game_service.check_if_second_train_card_needed():
                    self.draw_second_train_card()
            else:
                print("AI: Not enough cards in deck for blind pick and no cards on table, trying to claim a route.")
                self.game_service.log(
                    f"{self.color}, Action: BLIND PICK NOT AVAILABLE AND NO CARDS ON TABLE, trying to claim a route."
                )
                available_actions = self.game_service.get_available_actions(self.color)
                if "claim_route" in available_actions:
                    current_state = self.game_service.get_current_player_state()
                    claimable_routes = current_state["claimable_routes"]
                    if claimable_routes:
                        route = random.choice(claimable_routes)
                        self.claim_route(route)
                        print(f"AI: {self.color} claimed a route as an alternative action.")
                        return
                print(f"AI: {self.color} CAN'T DO ANYTHING this turn.")
                self.game_service.log(
                    f"{self.color}, Action: CAN'T DO ANYTHING (Insufficient cards and no valid route)."
                )

    def draw_second_train_card(self, needed_colors=None):
        """
        İkinci tren kartı çekme işlemini gerçekleştirir.
        Joker seçilemez; masadan görev biletlerine uygun kart seçilir.
        """
        game_state = self.game_service.get_game_state()
        train_cards_on_the_table = game_state["train_cards_on_the_table"]

        non_joker_needed_cards = [
            card for card in train_cards_on_the_table
            if (needed_colors is None or card.color in needed_colors) and card.color != "joker"
        ]
        if non_joker_needed_cards:
            selected_card = random.choice(non_joker_needed_cards)
            action_params = {"selected_card": selected_card}
            print("AI: Train cards on the table for second pick:", train_cards_on_the_table)
            print("AI: SELECTED SECOND CARD BY AI:", selected_card.color)
            self.game_service.perform_action("draw_train_card", action_params)
            self.game_service.change_status_text(
                f"{self.color} drew {selected_card.color} train card as second train card."
            )
            self.game_service.log(f"{self.color}, Action: DRAW TRAIN CARD (Second), {selected_card.color}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)
            return

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
                    f"{self.color} drew {selected_card.color} train card as alternative second card."
                )
                self.game_service.log(
                    f"{self.color}, Action: DRAW TRAIN CARD (Alternative Second), {selected_card.color}"
                )
                self.game_service.wait_for_it(global_vars.time_action * 1000)
            else:
                print("AI: No valid second card options available.")
                self.game_service.log(f"{self.color}, Action: NO VALID SECOND CARD OPTION.")

    def draw_destination_ticket(self):
        """
        Yeni görev biletleri çeker ve bunlardan en az 1, en fazla çekilen sayısı kadarını seçer.
        """
        draw_destination_card_list = self.game_service.perform_action("draw_destination_ticket", None)
        destination_card_list_without_none = [card for card in draw_destination_card_list if card is not None]

        if not destination_card_list_without_none:
            print("AI: No valid destination tickets drawn.")
            self.game_service.log(f"{self.color}, Action: DRAW DESTINATION TICKET - NO CARDS")
            return

        number_of_cards_to_select = random.randint(1, len(destination_card_list_without_none))
        selected_cards = random.sample(destination_card_list_without_none, number_of_cards_to_select)

        action_params = {"selected_destination_tickets": selected_cards}
        self.game_service.perform_action("draw_destination_ticket", action_params)
        self.game_service.change_status_text(f"{self.color} drew destination ticket card.")

        log_message = f"{self.color}, Action: DESTINATION TICKET,"
        for ticket in action_params['selected_destination_tickets']:
            log_message += f" {ticket.city1} to {ticket.city2},"
        log_message = log_message.rstrip(',')
        self.game_service.log(log_message)
        self.game_service.wait_for_it(global_vars.time_action * 1000)

    def claim_route(self, route):
        """
        Belirlenen rotayı talep etmeye çalışır.
         - Eğer rota gri ise, önce hangi renklerin kullanılabileceğini öğrenip ardından
           uygun rengi (ve gerekirse jokerleri) kullanarak rota talebinde bulunur.
         - Renkli rota ise doğrudan talep edilir.
        """
        if not route:
            print("AI: No route provided to claim.")
            self.game_service.log(f"{self.color}, Action: CLAIM ROUTE - NO ROUTE")
            return

        if route.color == "gray":
            print("AI: A GRAY ROUTE SELECTED")
            action_params = {"selected_route": route, "use_this_color": None}
            cards_can_be_used = self.game_service.perform_action("claim_route", action_params)
            self.game_service.change_status_text(f"{self.color} claiming a gray route.")
            self.game_service.wait_for_it(global_vars.time_action * 1000)

            if not cards_can_be_used:
                self.game_service.change_status_text(f"{self.color} can't claim gray route - insufficient cards maybe.")
                self.game_service.log(f"{self.color}, Action: CAN'T CLAIM GRAY ROUTE, insufficient cards.")
                return

            current_state = self.game_service.get_current_player_state()
            train_cards = current_state["train_cards"]
            route_length = route.length
            joker_count = sum(1 for c in train_cards if c.color == "joker")
            candidate_colors = ["red", "blue", "green", "yellow", "orange", "pink", "white", "black"]
            possible_colors = []
            for c in candidate_colors:
                color_count = sum(1 for card in train_cards if card.color == c)
                if color_count >= route_length or (color_count + joker_count) >= route_length:
                    possible_colors.append(c)

            if not possible_colors:
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
            self.game_service.change_status_text(
                f"{self.color} claimed a gray route with {use_random_color_with_jokers}"
            )
            self.game_service.log(
                f"{self.color}, Action: CLAIM GRAY ROUTE, {route.city1} to {route.city2}, {use_random_color_with_jokers}"
            )
            self.game_service.wait_for_it(global_vars.time_action * 1000)
        else:
            print("AI: A COLORED ROUTE SELECTED")
            action_params = {"selected_route": route, "use_this_color": None}
            self.game_service.perform_action("claim_route", action_params)
            self.game_service.change_status_text(f"{self.color} claimed a colored route.")
            self.game_service.log(f"{self.color}, Action: CLAIM COLORED ROUTE, {route.city1} to {route.city2}")
            self.game_service.wait_for_it(global_vars.time_action * 1000)


