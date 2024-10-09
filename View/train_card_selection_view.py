import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class TrainCardSelectionFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.card_1_img = None
        self.card_1_img_path = "../Assets/whitecard.png"

        self.card_2_img = None
        self.card_2_img_path = "../Assets/whitecard.png"

        self.card_3_img = None
        self.card_3_img_path = "../Assets/whitecard.png"

        self.card_4_img = None
        self.card_4_img_path = "../Assets/whitecard.png"

        self.card_5_img = None
        self.card_5_img_path = "../Assets/whitecard.png"

        self.blind_pick_img = None
        self.blind_pick_img_path = "../Assets/deck.jpg"

        self.canvas = None



    def create_train_card_selection_frame(self):
        # Create the main frame
        train_card_selection_frame = tk.Frame(self.root, width=924, height=150, bg="#fdf8ed",
                                              highlightthickness=4, highlightbackground="#e4a21d")
        train_card_selection_frame.place(x=240, y=570)

        # Create one large canvas within the frame
        self.canvas = tk.Canvas(train_card_selection_frame, width=924, height=150, bg="#fdf8ed", highlightthickness=0)
        self.canvas.place(x=0, y=0)

        frame_width = 150
        frame_height = 150
        spacing = 2.5  # Adjust for the correct spacing between the cards

        # First card
        train_card_pick_button1 = TTRGui.create_modern_button(self.canvas, "Pick", spacing, 105, 14, 2, 12)
        self.card_1_img = Image.open("../Assets/whitecard.png").resize((150, 105), Image.Resampling.LANCZOS)
        self.card_1_img = ImageTk.PhotoImage(self.card_1_img)
        self.canvas.card_1_img_id = self.canvas.create_image(spacing, 0, anchor='nw', image=self.card_1_img)
        self.card_1_img = self.card_1_img  # Keep a reference to avoid garbage collection

        # Second card
        train_card_pick_button2 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 2 + frame_width, 105,14, 2, 12)
        self.card_2_img = Image.open("../Assets/whitecard.png").resize((150, 105), Image.Resampling.LANCZOS)
        self.card_2_img = ImageTk.PhotoImage(self.card_2_img)
        self.canvas.card_2_img_id = self.canvas.create_image(spacing * 2 + frame_width, 0, anchor='nw', image=self.card_2_img)
        self.card_2_img = self.card_2_img

        # Third card
        train_card_pick_button3 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 3 + frame_width * 2, 105,14, 2, 12)
        self.card_3_img = Image.open("../Assets/whitecard.png").resize((150, 105), Image.Resampling.LANCZOS)
        self.card_3_img = ImageTk.PhotoImage(self.card_3_img)
        self.canvas.card_3_img_id = self.canvas.create_image(spacing * 3 + frame_width * 2, 0, anchor='nw', image=self.card_3_img)
        self.card_3_img = self.card_3_img

        # Fourth card
        train_card_pick_button4 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 4 + frame_width * 3, 105,14, 2, 12)
        self.card_4_img = Image.open("../Assets/whitecard.png").resize((150, 105), Image.Resampling.LANCZOS)
        self.card_4_img = ImageTk.PhotoImage(self.card_4_img)
        self.canvas.card_4_img_id = self.canvas.create_image(spacing * 4 + frame_width * 3, 0, anchor='nw', image=self.card_4_img)
        self.card_4_img = self.card_4_img

        # Fifth card
        train_card_pick_button5 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 5 + frame_width * 4, 105,14, 2, 12)
        self.card_5_img = Image.open("../Assets/whitecard.png").resize((150, 105), Image.Resampling.LANCZOS)
        self.card_5_img = ImageTk.PhotoImage(self.card_5_img)
        self.canvas.card_5_img_id = self.canvas.create_image(spacing * 5 + frame_width * 4, 0, anchor='nw', image=self.card_5_img)
        self.card_5_img = self.card_5_img

        # Sixth card (Blind Pick)
        train_card_pick_button6 = TTRGui.create_modern_button(self.canvas, "Blind Pick", spacing * 6 + frame_width * 5,
                                                              105, 14, 2, 12)
        self.blind_pick_img = Image.open("../Assets/deck.jpg").resize((150, 105), Image.Resampling.LANCZOS)
        self.blind_pick_img = ImageTk.PhotoImage(self.blind_pick_img)
        self.canvas.blind_pick_img_id = self.canvas.create_image(spacing * 6 + frame_width * 5, 0, anchor='nw', image=self.blind_pick_img)
        self.blind_pick_img = self.blind_pick_img

    def update_train_card_selection_frame(self):
        print("Train Card Selection Frame is Updated.")
        self.card_1_img = TTRGui.change_image(self, self.canvas.card_1_img_id, self.card_1_img,
                                                   self.card_1_img_path)
        self.card_2_img = TTRGui.change_image(self, self.canvas.card_2_img_id, self.card_2_img,
                                                   self.card_2_img_path)
        self.card_3_img = TTRGui.change_image(self, self.canvas.card_3_img_id, self.card_3_img,
                                                   self.card_3_img_path)
        self.card_4_img = TTRGui.change_image(self, self.canvas.card_4_img_id, self.card_4_img,
                                                   self.card_4_img_path)
        self.card_5_img = TTRGui.change_image(self, self.canvas.card_5_img_id, self.card_5_img,
                                                   self.card_5_img_path)
        self.blind_pick_img = TTRGui.change_image(self, self.canvas.blind_pick_img_id, self.blind_pick_img,
                                                   self.blind_pick_img_path)



