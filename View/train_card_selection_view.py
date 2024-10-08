import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class TrainCardSelectionFrame:
    def __init__(self, root):
        self.root = root

    def create_train_card_selection_frame(self):
        train_card_selection_frame = tk.Frame(self.root, width=924, height=150, bg="#fdf8ed",
                                              highlightthickness=4, highlightbackground="#e4a21d")
        train_card_selection_frame.place(x=240, y=570)

        frame_width = 150
        frame_height = 150
        total_width = 920
        num_frames = 6
        spacing = (total_width - (num_frames * frame_width)) // (num_frames + 1)

        for i in range(num_frames):
            x_position = spacing + i * (frame_width + spacing)
            inner_frame = tk.Frame(train_card_selection_frame, width=frame_width, height=frame_height, bg="#d7ab5e")
            inner_frame.place(x=x_position, y=1)

            if i != 5:
                train_card_pick_button = TTRGui.create_modern_button(inner_frame, "Pick", 0, 105, 18, 2, 10)
                image = Image.open("../Assets/whitecard.png")
            else:
                train_card_pick_button = TTRGui.create_modern_button(inner_frame, "Blind Pick", 0, 105, 18, 2, 10)
                image = Image.open("../Assets/deck.jpg")

            image = image.resize((150, 105), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(image)
            image_label = tk.Label(inner_frame, image=img, bg="#fdf8ed")
            image_label.image = img
            image_label.place(x=0, y=0)

