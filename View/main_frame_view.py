import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance, ImageOps

class MainFrame:
    def __init__(self, root):
        self.root = root
        self.sanfransisco_portland_1_image_visible = True
        self.canvas = None
        self.dest_card_1_img = None
        self.dest_card_2_img = None
        self.dest_card_3_img = None

        self.blue_card_value = 0
        self.red_card_value = 0
        self.green_card_value = 0
        self.orange_card_value = 0
        self.yellow_card_value = 0
        self.white_card_value = 0
        self.black_card_value = 0
        self.pink_card_value = 0
        self.joker_card_value = 0

        self.routes_view_dictionary = {'sanfransisco_portland_1': [True, "red"], 'sanfransisco_portland_2': [False, "red"]}


    def create_main_frame(self):
        main_frame = tk.Frame(self.root, width=1284, height=527, bg="black")
        main_frame.place(x=0, y=43)

        self.canvas = tk.Canvas(main_frame, width=1284, height=527, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        image = Image.open("../Assets/map.jpg")
        image = image.resize((1284, 527), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

        # Player inventory section
        # Displaying cards
        self.canvas.create_text(65, 15, anchor="nw", text="Inventory", fill="#e4a21d", font=("Helvetica", 16, "bold"))
        blue_card_img, self.canvas.blue_text_id = self.create_card_with_text("../Assets/bluecard.png", 120, 50, self.blue_card_value)
        red_card_img, self.canvas.red_text_id = self.create_card_with_text("../Assets/redcard.png", 10, 50, self.red_card_value)
        green_card_img, self.canvas.green_text_id = self.create_card_with_text("../Assets/greencard.png", 120, 120, self.green_card_value)
        orange_card_img, self.canvas.orange_text_id = self.create_card_with_text("../Assets/orangecard.png", 10, 120, self.orange_card_value)
        yellow_card_img, self.canvas.yellow_text_id = self.create_card_with_text("../Assets/yellowcard.png", 120, 190, self.yellow_card_value)
        white_card_img, self.canvas.white_text_id = self.create_card_with_text("../Assets/whitecard.png", 10, 190, self.white_card_value)
        black_card_img, self.canvas.black_text_id = self.create_card_with_text("../Assets/blackcard.png", 120, 260, self.black_card_value)
        pink_card_img, self.canvas.pink_text_id = self.create_card_with_text("../Assets/pinkcard.png", 10, 260, self.pink_card_value)
        joker_card_img, self.canvas.joker_text_id = self.create_card_with_text("../Assets/jokercard.png", 10, 330, self.joker_card_value)

        # Keep references to images to avoid garbage collection
        self.canvas.blue_card_img = blue_card_img
        self.canvas.red_card_img = red_card_img
        self.canvas.green_card_img = green_card_img
        self.canvas.orange_card_img = orange_card_img
        self.canvas.yellow_card_img = yellow_card_img
        self.canvas.white_card_img = white_card_img
        self.canvas.black_card_img = black_card_img
        self.canvas.pink_card_img = pink_card_img
        self.canvas.joker_card_img = joker_card_img

        # Destination tickets
        self.update_destination_tickets()

        #Update Roads
        self.update_roads()



    def create_card_with_text(self, image_path, x, y, card_value):
        card_img = Image.open(image_path)
        card_img = card_img.resize((100, 65), Image.Resampling.LANCZOS)
        card_img = ImageTk.PhotoImage(card_img)
        self.canvas.create_image(x, y, anchor="nw", image=card_img)
        self.canvas.create_rectangle(x+41, y+22, x+60, y+42, fill="white", outline="black", width=2)
        text_id = self.canvas.create_text(x+50, y+32, text=str(card_value), fill="black", font=("Helvetica", 12, "bold"))
        return card_img, text_id

    def create_road_image(self, image_path, color):
        card_img = Image.open(image_path).convert("RGBA")
        card_img = card_img.resize((1284, 527), Image.Resampling.LANCZOS)

        # Seperate the alpha channel from the image so it will color only the opaque parts.
        r, g, b, alpha = card_img.split()
        grayscale_img = Image.merge("RGB", (r, g, b)).convert("L") #only colors the opaque part

        if color == "blue":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="blue")
        elif color == "red":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="red")
        elif color == "green":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="green")
        elif color == "yellow":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="yellow")
        elif color == "black":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="black")

        final_img = Image.merge("RGBA", (*colorized_img.split(), alpha))
        final_img = ImageTk.PhotoImage(final_img)
        created_road = self.canvas.create_image(0, 0, anchor="nw", image=final_img)
        return created_road, final_img

    def update_roads(self):
        print("roads")

        if(hasattr(self.canvas, 'sanfransisco_portland_1')):
            self.canvas.delete(self.canvas.sanfransisco_portland_1)

        if(self.routes_view_dictionary['sanfransisco_portland_1'][0]):
            self.canvas.sanfransisco_portland_1, self.canvas.sanfransisco_portland_1_img = self.create_road_image("../Assets/MapRoads/sanfransisco_portland_1.png", self.routes_view_dictionary['sanfransisco_portland_1'][1])


    def update_destination_tickets(self):
        if hasattr(self.canvas, 'dest_card_1'):
            self.canvas.delete(self.canvas.dest_card_1)
        if hasattr(self.canvas, 'dest_card_2'):
            self.canvas.delete(self.canvas.dest_card_2)
        if hasattr(self.canvas, 'dest_card_3'):
            self.canvas.delete(self.canvas.dest_card_3)

        self.dest_card_1_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        self.dest_card_1_img = self.dest_card_1_img.resize((150, 102), Image.Resampling.LANCZOS)
        self.dest_card_1_img = ImageTk.PhotoImage(self.dest_card_1_img)
        self.canvas.dest_card_1 = self.canvas.create_image(10, 420, anchor="nw", image=self.dest_card_1_img)

        self.dest_card_2_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        self.dest_card_2_img = self.dest_card_2_img.resize((150, 102), Image.Resampling.LANCZOS)
        self.dest_card_2_img = ImageTk.PhotoImage(self.dest_card_2_img)
        self.canvas.dest_card_2 = self.canvas.create_image(170, 420, anchor="nw", image=self.dest_card_2_img)

        self.dest_card_3_img = Image.open("../Assets/DestinationTickets/backsideOfTicket.png")
        self.dest_card_3_img = self.dest_card_3_img.resize((150, 102), Image.Resampling.LANCZOS)
        self.dest_card_3_img = ImageTk.PhotoImage(self.dest_card_3_img)
        self.canvas.dest_card_3 = self.canvas.create_image(330, 420, anchor="nw", image=self.dest_card_3_img)

    def update_ticket_numbers(self):
        print("ticket numbers are updated")

        if hasattr(self.canvas, 'blue_text_id'):
            self.canvas.itemconfig(self.canvas.blue_text_id, text=str(self.blue_card_value))

        if hasattr(self.canvas, 'red_text_id'):
            self.canvas.itemconfig(self.canvas.red_text_id, text=str(self.red_card_value))

        if hasattr(self.canvas, 'green_text_id'):
            self.canvas.itemconfig(self.canvas.green_text_id, text=str(self.green_card_value))

        if hasattr(self.canvas, 'orange_text_id'):
            self.canvas.itemconfig(self.canvas.orange_text_id, text=str(self.orange_card_value))

        if hasattr(self.canvas, 'yellow_text_id'):
            self.canvas.itemconfig(self.canvas.yellow_text_id, text=str(self.yellow_card_value))

        if hasattr(self.canvas, 'white_text_id'):
            self.canvas.itemconfig(self.canvas.white_text_id, text=str(self.white_card_value))

        if hasattr(self.canvas, 'black_text_id'):
            self.canvas.itemconfig(self.canvas.black_text_id, text=str(self.black_card_value))

        if hasattr(self.canvas, 'pink_text_id'):
            self.canvas.itemconfig(self.canvas.pink_text_id, text=str(self.pink_card_value))

        if hasattr(self.canvas, 'joker_text_id'):
            self.canvas.itemconfig(self.canvas.joker_text_id, text=str(self.joker_card_value))


