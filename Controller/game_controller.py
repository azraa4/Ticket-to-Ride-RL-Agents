class GameController:
    def __init__(self, view, board):
        self.view = view
        self.board = board

        return

    def get_unclaimed_routes(self):
        return self.board.get_unclaimed_routes()

    def get_claimed_routes(self):
        return self.board.get_claimed_routes()

    def claim_route(self, id, player): #player şimdilik bir string sonra player objesi olacak
        print("claimed")
        unclaimed_routes = self.board.get_unclaimed_routes()
        for route in unclaimed_routes:
            if route.id == id:
                route.claimed_by = player
                route.claimed_color = "blue"
        self.view.main_frame.create_roads()