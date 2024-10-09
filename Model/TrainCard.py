import tkinter as tk

class TrainCard:
    COLORS = ['purple', 'blue', 'orange', 'white', 'green', 'yellow', 'black', 'red']
    LOCOMOTIVE = 'locomotive'

    def __init__(self, color, image, root=None):
        if color not in self.COLORS and color != self.LOCOMOTIVE:
            raise ValueError(f"{color} is not a valid train car color.")
        self.color = color
        self.image = image
        self.label = None
        if root:
            self.create_label(root)

    def create_label(self, root):
        # Tkinter Label oluştur
        self.label = tk.Label(root, image=self.image)
        self.label.pack()

    def is_locomotive(self):
        return self.color == self.LOCOMOTIVE

    def set_new_image(self, new_image):
        self.image = new_image
        if self.label:
            self.label.config(image=self.image)

    def __str__(self):
        return f"Train Card: {self.color}"
