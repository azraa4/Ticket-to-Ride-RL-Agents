class Route:
    def __init__(self, id, city1, city2, length, color):
        self.id = id
        self.city1 = city1
        self.city2 = city2
        self.length = length
        self.color = color
        self.claimed_color = None
        self.claimed_by = None
        self.canvas_item = None

    def claim(self, player):
        if self.claimed_by is None:
            self.claimed_by = player
        else:
            print("it is already claimed")

    def get_image_path(self):
        return f"../Assets/MapRoads/{self.id}.png"

    def get_claimed_color(self):
        if self.claimed_color is not None:
            return self.claimed_color
