class TrainCard:
    def __init__(self, color):
        self.color = color
        self.image_path = f"../Assets/MapRoads/{color}card.png"  # Kartın rengine göre resim dosyası yolu

    def __repr__(self):
        return f"TrainCard({self.color})"

