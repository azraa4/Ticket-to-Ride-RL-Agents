class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.points = 0
        self.train_cards = []
        self.destination_tickets = []
        self.claimed_routes = []
        self.train_cars = 45
        self.first_turn = True
        self.has_longest_road = False

    def add_train_card(self, train_card):
        self.train_cards.append(train_card)

    def add_destination_ticket(self, destination_ticket):
        self.destination_tickets.append(destination_ticket)

    def add_route(self, route):
        self.claimed_routes.append(route)

    def calculate_points(self):
        total_points = 0

        # Create adjacency list from claimed routes
        adjacency_list = {}
        for route in self.claimed_routes:
            if route.city1 not in adjacency_list:
                adjacency_list[route.city1] = []
            if route.city2 not in adjacency_list:
                adjacency_list[route.city2] = []
            adjacency_list[route.city1].append(route.city2)
            adjacency_list[route.city2].append(route.city1)

        # Function to perform DFS to check connection between two cities
        def dfs(current_city, target_city, visited):
            if current_city == target_city:
                return True
            visited.add(current_city)
            for neighbor in adjacency_list.get(current_city, []):
                if neighbor not in visited:
                    if dfs(neighbor, target_city, visited):
                        return True
            return False

        # Check each destination ticket for completion
        for ticket in self.destination_tickets:
            if dfs(ticket.city1, ticket.city2, set()):
                ticket.mark_as_completed()
                total_points += ticket.points

        for route in self.claimed_routes:
            total_points += route.get_points_of_the_route()

        # Update player points
        self.points = total_points
        print(f"POINTS STATUS: {self.name} with color {self.color} has now {self.points} points.")

    def get_number_of_cards(self, color):
        num = 0
        for train_card in self.train_cards:
            if train_card.color == color:
                num = num + 1
        return num

    def remove_card_according_to_color(self, color, amount_to_delete):
        num = amount_to_delete
        copy_of_train_cards_list = self.train_cards[:]
        for train_card in copy_of_train_cards_list:
            if color == train_card.color and num!=0:
                self.train_cards.remove(train_card)
                num -=1

    def decrease_train_cars(self, num):
        self.train_cars -= num
        print(f"{self.name} with {self.color} has now {self.train_cars} train cars.")

    def calculate_longest_route(self):
        # Create adjacency list with route lengths from claimed routes
        adjacency_list = {}
        for route in self.claimed_routes:
            if route.city1 not in adjacency_list:
                adjacency_list[route.city1] = []
            if route.city2 not in adjacency_list:
                adjacency_list[route.city2] = []
            # Add both directions with route length
            adjacency_list[route.city1].append((route.city2, route.length))
            adjacency_list[route.city2].append((route.city1, route.length))

        # Function to perform DFS and calculate the longest path
        def dfs(city, visited, current_length):
            visited.add(city)
            max_length = current_length
            for neighbor, length in adjacency_list.get(city, []):
                if neighbor not in visited:
                    max_length = max(max_length, dfs(neighbor, visited, current_length + length))
            visited.remove(city)
            return max_length

        # Calculate the longest path for all starting cities
        longest_road = 0
        for city in adjacency_list.keys():
            longest_road = max(longest_road, dfs(city, set(), 0))

        return longest_road
