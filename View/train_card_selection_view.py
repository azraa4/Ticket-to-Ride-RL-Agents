import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class TrainCardSelectionFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.card_1 = None
        self.card_1_img = None
        self.card_1_img_path = "../Assets/whitecard.png"
        self.train_card_pick_button1 = None

        self.card_2 = None
        self.card_2_img = None
        self.card_2_img_path = "../Assets/whitecard.png"
        self.train_card_pick_button2 = None

        self.card_3 = None
        self.card_3_img = None
        self.card_3_img_path = "../Assets/whitecard.png"
        self.train_card_pick_button3 = None

        self.card_4 = None
        self.card_4_img = None
        self.card_4_img_path = "../Assets/whitecard.png"
        self.train_card_pick_button4 = None

        self.card_5 = None
        self.card_5_img = None
        self.card_5_img_path = "../Assets/whitecard.png"
        self.train_card_pick_button5 = None

        self.blind_pick_img = None
        self.blind_pick_img_path = "../Assets/deck.jpg"
        self.train_card_pick_button6 = None

        self.canvas = None

        self.remaining_cards_in_deck = 0

        self.blind_pick_text_id = None


    def create_train_card_selection_frame(self):
        # Create the main frame
        train_card_selection_frame = tk.Frame(self.root, width=848, height=150, bg="#fdf8ed",
                                              highlightthickness=4, highlightbackground="#ae2907")
        train_card_selection_frame.place(x=230, y=570)

        # Create one large canvas within the frame
        self.canvas = tk.Canvas(train_card_selection_frame, width=843.5, height=150, bg="#fdf8ed", highlightthickness=0)
        self.canvas.place(x=0, y=0)

        frame_width = 138
        spacing = 2.5  # Adjust for the correct spacing between the cards

        # First card
        self.train_card_pick_button1 = TTRGui.create_modern_button(self.canvas, "Pick", spacing, 105, 16, 2, 10)
        self.train_card_pick_button1.config(command=lambda: self.controller.draw_train_card(self.card_1))
        self.card_1_img = Image.open("../Assets/whitecard.png").resize((frame_width, 105), Image.Resampling.LANCZOS)
        self.card_1_img = ImageTk.PhotoImage(self.card_1_img)
        self.canvas.card_1_img_id = self.canvas.create_image(spacing, 0, anchor='nw', image=self.card_1_img)
        self.card_1_img = self.card_1_img  # Keep a reference to avoid garbage collection

        # Second card
        self.train_card_pick_button2 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 2 + frame_width, 105, 16,
                                                              2, 10)
        self.train_card_pick_button2.config(command=lambda: self.controller.draw_train_card(self.card_2))
        self.card_2_img = Image.open("../Assets/whitecard.png").resize((frame_width, 105), Image.Resampling.LANCZOS)
        self.card_2_img = ImageTk.PhotoImage(self.card_2_img)
        self.canvas.card_2_img_id = self.canvas.create_image(spacing * 2 + frame_width, 0, anchor='nw',
                                                             image=self.card_2_img)
        self.card_2_img = self.card_2_img

        # Third card
        self.train_card_pick_button3 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 3 + frame_width * 2, 105,
                                                              16, 2, 10)
        self.train_card_pick_button3.config(command=lambda: self.controller.draw_train_card(self.card_3))
        self.card_3_img = Image.open("../Assets/whitecard.png").resize((frame_width, 105), Image.Resampling.LANCZOS)
        self.card_3_img = ImageTk.PhotoImage(self.card_3_img)
        self.canvas.card_3_img_id = self.canvas.create_image(spacing * 3 + frame_width * 2, 0, anchor='nw',
                                                             image=self.card_3_img)
        self.card_3_img = self.card_3_img

        # Fourth card
        self.train_card_pick_button4 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 4 + frame_width * 3, 105,
                                                              16, 2, 10)
        self.train_card_pick_button4.config(command=lambda: self.controller.draw_train_card(self.card_4))
        self.card_4_img = Image.open("../Assets/whitecard.png").resize((frame_width, 105), Image.Resampling.LANCZOS)
        self.card_4_img = ImageTk.PhotoImage(self.card_4_img)
        self.canvas.card_4_img_id = self.canvas.create_image(spacing * 4 + frame_width * 3, 0, anchor='nw',
                                                             image=self.card_4_img)
        self.card_4_img = self.card_4_img

        # Fifth card
        self.train_card_pick_button5 = TTRGui.create_modern_button(self.canvas, "Pick", spacing * 5 + frame_width * 4, 105,
                                                              16, 2, 10)
        self.train_card_pick_button5.config(command=lambda: self.controller.draw_train_card(self.card_5))
        self.card_5_img = Image.open("../Assets/whitecard.png").resize((frame_width, 105), Image.Resampling.LANCZOS)
        self.card_5_img = ImageTk.PhotoImage(self.card_5_img)
        self.canvas.card_5_img_id = self.canvas.create_image(spacing * 5 + frame_width * 4, 0, anchor='nw',
                                                             image=self.card_5_img)
        self.card_5_img = self.card_5_img

        # Sixth card (Blind Pick)
        self.train_card_pick_button6 = TTRGui.create_modern_button(self.canvas, "Blind Pick", spacing * 6 + frame_width * 5,
                                                              105, 16, 2, 10)
        self.train_card_pick_button6.config(command=lambda: self.controller.draw_cards_from_blind_deck())
        self.blind_pick_img = Image.open("../Assets/deck.jpg").resize((frame_width-2, 105), Image.Resampling.LANCZOS)
        self.blind_pick_img = ImageTk.PhotoImage(self.blind_pick_img)
        self.canvas.blind_pick_img_id = self.canvas.create_image(spacing * 6 + frame_width * 5, 0, anchor='nw',
                                                                 image=self.blind_pick_img)
        self.blind_pick_img = self.blind_pick_img


        self.remaining_cards_in_deck = 103
        #remaining cards in the deck
        center_x = spacing * 6 + frame_width * 5 + (frame_width - 2) / 2
        center_y = 105 / 2
        self.blind_pick_text_id = self.canvas.create_text(center_x, center_y, text=str(self.remaining_cards_in_deck),
                                                                 font=("Arial", 16), fill="black")

    def update_remaining_cards_in_deck(self, remaining):
        self.remaining_cards_in_deck = remaining
        self.canvas.itemconfig(self.blind_pick_text_id, text=str(self.remaining_cards_in_deck))

    def update_train_card_pick_buttons(self, check):
        if check:
            if self.card_1.color == "joker":
                self.destroy_train_card_pick_button("train_card_pick_button1")
            if self.card_2.color == "joker":
                self.destroy_train_card_pick_button("train_card_pick_button2")
            if self.card_3.color == "joker":
                self.destroy_train_card_pick_button("train_card_pick_button3")
            if self.card_4.color == "joker":
                self.destroy_train_card_pick_button("train_card_pick_button4")
            if self.card_5.color == "joker":
                self.destroy_train_card_pick_button("train_card_pick_button5")

            self.destroy_train_card_pick_button("train_card_pick_button6")
        elif not check:
            frame_width = 138
            spacing = 2.5
            if self.train_card_pick_button1 is None:
                self.train_card_pick_button1 = TTRGui.create_modern_button(self.canvas, "Pick", spacing, 105, 16, 2, 10)
                self.train_card_pick_button1.config(command=lambda: self.controller.draw_train_card(self.card_1))
            if self.train_card_pick_button2 is None:
                self.train_card_pick_button2 = TTRGui.create_modern_button(self.canvas, "Pick",
                                                                           spacing * 2 + frame_width, 105, 16,
                                                                           2, 10)
                self.train_card_pick_button2.config(command=lambda: self.controller.draw_train_card(self.card_2))
            if self.train_card_pick_button3 is None:
                self.train_card_pick_button3 = TTRGui.create_modern_button(self.canvas, "Pick",
                                                                           spacing * 3 + frame_width * 2, 105,
                                                                           16, 2, 10)
                self.train_card_pick_button3.config(command=lambda: self.controller.draw_train_card(self.card_3))
            if self.train_card_pick_button4 is None:
                self.train_card_pick_button4 = TTRGui.create_modern_button(self.canvas, "Pick",
                                                                           spacing * 4 + frame_width * 3, 105,
                                                                           16, 2, 10)
                self.train_card_pick_button4.config(command=lambda: self.controller.draw_train_card(self.card_4))
            if self.train_card_pick_button5 is None:
                self.train_card_pick_button5 = TTRGui.create_modern_button(self.canvas, "Pick",
                                                                           spacing * 5 + frame_width * 4, 105,
                                                                           16, 2, 10)
                self.train_card_pick_button5.config(command=lambda: self.controller.draw_train_card(self.card_5))
            if self.train_card_pick_button6 is None:
                self.train_card_pick_button6 = TTRGui.create_modern_button(self.canvas, "Blind Pick",
                                                                           spacing * 6 + frame_width * 5,
                                                                           105, 16, 2, 10)
                self.train_card_pick_button6.config(command=lambda: self.controller.draw_cards_from_blind_deck())

    def destroy_train_card_pick_button(self, button_name):
        button = getattr(self, button_name, None)
        if button is not None:
            button.destroy()
            setattr(self, button_name, None)

    def destroy_all_train_cards(self):
        if self.train_card_pick_button1 is not None:
            self.train_card_pick_button1.destroy()
        if self.train_card_pick_button2 is not None:
            self.train_card_pick_button2.destroy()
        if self.train_card_pick_button3 is not None:
            self.train_card_pick_button3.destroy()
        if self.train_card_pick_button4 is not None:
            self.train_card_pick_button4.destroy()
        if self.train_card_pick_button5 is not None:
            self.train_card_pick_button5.destroy()
        if self.train_card_pick_button6 is not None:
            self.train_card_pick_button6.destroy()
        self.canvas.delete("all")

        self.canvas_for_text = tk.Canvas(self.canvas, bg="#fdf8ed", width=230, height=30)
        self.canvas_for_text.place(x=0, y=0)
        self.canvas_for_text.create_text(5, 5, anchor="nw", text="All cards are in the hands of players.", fill="black",
                                         font=("Helvetica", 10, "bold"))


    def update_train_card_selection_frame(self):
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



