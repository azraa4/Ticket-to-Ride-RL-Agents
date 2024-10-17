class Player:
    def __init__(self, name, color):
        self.name = name  # Oyuncu ismi
        self.color = color  # Oyuncunun rengi (rotalara talep edileceği zaman kullanılacak)
        self.train_cards = []  # Oyuncunun elindeki tren kartları
        self.destination_tickets = []  # Oyuncunun elindeki destination ticket'lar
        self.claimed_routes = []  # Oyuncunun talep ettiği rotalar

    def add_train_card(self, train_card):
        """Oyuncunun eline bir tren kartı ekler."""
        self.train_cards.append(train_card)

    def add_destination_ticket(self, destination_ticket):
        """Oyuncunun eline bir destination ticket ekler."""
        self.destination_tickets.append(destination_ticket)

    def claim_route(self, route, required_cards):
        """
        Oyuncu bir rota talep eder.
        Gerekli tren kartlarına sahip olup olmadığını kontrol eder ve rota talep işlemini gerçekleştirir.
        """
        # Oyuncunun gerekli renkteki kartlara sahip olup olmadığını kontrol et
        if self.has_required_cards(required_cards):
            # Gerekli kartları elden çıkar
            self.use_required_cards(required_cards)
            # Rotayı oyuncunun talep ettiği rotalara ekle
            self.claimed_routes.append(route)
            return True
        else:
            print(f"{self.name} does not have enough cards to claim this route.")
            return False

    def has_required_cards(self, required_cards):
        """Oyuncunun bir rotayı talep etmek için yeterli tren kartına sahip olup olmadığını kontrol eder."""
        card_count = {color: 0 for color in
                      ["blue", "red", "green", "orange", "yellow", "white", "black", "pink", "joker"]}

        # Oyuncunun elindeki kartları sayar
        for card in self.train_cards:
            card_count[card.color] += 1

        # Gerekli kartların oyuncuda olup olmadığını kontrol eder
        for required_color, count in required_cards.items():
            if card_count[required_color] < count:
                return False
        return True

    def use_required_cards(self, required_cards):
        """Bir rotayı talep ederken oyuncunun gerekli kartları kullanmasını sağlar."""
        for required_color, count in required_cards.items():
            cards_to_remove = [card for card in self.train_cards if card.color == required_color][:count]
            for card in cards_to_remove:
                self.train_cards.remove(card)

    def get_train_card_count(self, color):
        """Belirli bir renkte kaç tane tren kartı olduğunu döndürür."""
        return sum(1 for card in self.train_cards if card.color == color)

    def __repr__(self):
        return f"Player({self.name}, color={self.color})"
