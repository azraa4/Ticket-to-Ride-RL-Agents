import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class MainFrame:
    def __init__(self, root):
        self.root = root

    def create_main_frame(self):
        main_frame = tk.Frame(self.root, width=1284, height=570, bg="black")
        main_frame.place(x=-2, y=0)

        image = Image.open("../Assets/map.jpg")
        image = image.resize((1284, 570), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(image)

        canvas = tk.Canvas(main_frame, width=1284, height=570, highlightthickness=0)
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.place(x=0, y=0)
        canvas.image = img

        # Player inventory section
        def create_card_with_text(image_path, x, y, card_value):
            card_img = Image.open(image_path)
            card_img = card_img.resize((100, 65), Image.Resampling.LANCZOS)
            card_img = ImageTk.PhotoImage(card_img)
            canvas.create_image(x, y, anchor="nw", image=card_img)
            canvas.create_rectangle(x+41, y+22, x+60, y+42, fill="white", outline="black", width=2)
            text_id = canvas.create_text(x+50, y+32, text=str(card_value), fill="black", font=("Helvetica", 12, "bold"))
            return card_img, text_id

        # Card values
        blue_card_value = 0
        red_card_value = 0
        green_card_value = 0
        orange_card_value = 0
        yellow_card_value = 0
        white_card_value = 0
        black_card_value = 0
        pink_card_value = 0
        joker_card_value = 0

        # Displaying cards
        canvas.create_text(65, 55, anchor="nw", text="Inventory", fill="#e4a21d", font=("Helvetica", 16, "bold"))
        blue_card_img, blue_text_id = create_card_with_text("../Assets/bluecard.png", 120, 90, blue_card_value)
        red_card_img, red_text_id = create_card_with_text("../Assets/redcard.png", 10, 90, red_card_value)
        green_card_img, green_text_id = create_card_with_text("../Assets/greencard.png", 120, 160, green_card_value)
        orange_card_img, orange_text_id = create_card_with_text("../Assets/orangecard.png", 10, 160, orange_card_value)
        yellow_card_img, yellow_text_id = create_card_with_text("../Assets/yellowcard.png", 120, 230, yellow_card_value)
        white_card_img, white_text_id = create_card_with_text("../Assets/whitecard.png", 10, 230, white_card_value)
        black_card_img, black_text_id = create_card_with_text("../Assets/blackcard.png", 120, 300, black_card_value)
        pink_card_img, pink_text_id = create_card_with_text("../Assets/pinkcard.png", 10, 300, pink_card_value)
        joker_card_img, joker_text_id = create_card_with_text("../Assets/jokercard.png", 10, 370, joker_card_value)

        # Keep references to images to avoid garbage collection
        canvas.blue_card_img = blue_card_img
        canvas.red_card_img = red_card_img
        canvas.green_card_img = green_card_img
        canvas.orange_card_img = orange_card_img
        canvas.yellow_card_img = yellow_card_img
        canvas.white_card_img = white_card_img
        canvas.black_card_img = black_card_img
        canvas.pink_card_img = pink_card_img
        canvas.joker_card_img = joker_card_img

        # Destination tickets
        dest_card_1_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        dest_card_1_img = dest_card_1_img.resize((150, 102), Image.Resampling.LANCZOS)
        dest_card_1_img = ImageTk.PhotoImage(dest_card_1_img)
        canvas.create_image(10, 460, anchor="nw", image=dest_card_1_img)
        canvas.dest_card_1_img = dest_card_1_img

        dest_card_2_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        dest_card_2_img = dest_card_2_img.resize((150, 102), Image.Resampling.LANCZOS)
        dest_card_2_img = ImageTk.PhotoImage(dest_card_2_img)
        canvas.create_image(170, 460, anchor="nw", image=dest_card_2_img)
        canvas.dest_card_2_img = dest_card_2_img

        dest_card_3_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        dest_card_3_img = dest_card_3_img.resize((150, 102), Image.Resampling.LANCZOS)
        dest_card_3_img = ImageTk.PhotoImage(dest_card_3_img)
        canvas.create_image(330, 460, anchor="nw", image=dest_card_3_img)
        canvas.dest_card_3_img = dest_card_3_img
