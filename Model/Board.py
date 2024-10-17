from Model.Route import Route
import json

class Board:
    def __init__(self):
        self.routes = []
        self.initialize_routes()

    def initialize_routes(self):
        with open("../Model/routes_data.json", "r") as json_file:
            data = json.load(json_file)
            routes_data = data["routes_data"]

        for route_data in routes_data:
            route = Route(
                route_data["id"],
                route_data["city1"],
                route_data["city2"],
                route_data["length"],
                route_data["color"]
            )
            self.routes.append(route)

    def get_available_routes(self):
        return [route for route in self.routes if route.claimed_by is None]

    def get_claimed_routes(self):
        claimed_routes = []
        for route in self.routes:
            if route.claimed_by is not None:
                claimed_routes.append(route)
        return claimed_routes

    def get_unclaimed_routes(self):
        un_claimed_routes = []
        for route in self.routes:
            if route.claimed_by is None:
                un_claimed_routes.append(route)
        return un_claimed_routes

    def get_route_by_id(self, route_id):
        """ID'ye göre bir rotayı bul ve geri döndür."""
        for route in self.routes:
            if route.id == route_id:
                return route
        return None  # Eğer ID bulunamazsa None döndür