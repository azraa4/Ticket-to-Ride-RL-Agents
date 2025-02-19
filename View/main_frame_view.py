import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
from View.ttr_gui_view import TTRGui
from View.modern_option_menu import ModernOptionMenu
from View.modern_button import ModernButton

class MainFrame:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.canvas = None
        self.select_card_for_gray_roads_frame = None
        self.select_destination_tickets_canvas = None

        self.back_side_of_ticket_image_path = "Assets/DestinationTickets/backsideOfTicket.png"
        self.dest_card_1_img_path = self.back_side_of_ticket_image_path
        self.dest_card_2_img_path = self.back_side_of_ticket_image_path
        self.dest_card_3_img_path = self.back_side_of_ticket_image_path

        self.dest_card_1_img = None
        self.dest_card_2_img = None
        self.dest_card_3_img = None

        self.selectable_dest_card_1_img = None
        self.selectable_dest_card_2_img = None
        self.selectable_dest_card_3_img = None

        self.check_var1 = None
        self.check_var2 = None
        self.check_var3 = None

        self.blue_card_value = 0
        self.red_card_value = 0
        self.green_card_value = 0
        self.orange_card_value = 0
        self.yellow_card_value = 0
        self.white_card_value = 0
        self.black_card_value = 0
        self.pink_card_value = 0
        self.joker_card_value = 0


    def create_main_frame(self):
        main_frame = tk.Frame(self.root, width=1284, height=527, bg="black")
        main_frame.place(x=0, y=43)

        self.canvas = tk.Canvas(main_frame, width=1284, height=527, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        image = Image.open("Assets/map.jpg")
        image = image.resize((1284, 527), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=img)
        self.canvas.image = img

        # Player inventory section
        # Displaying cards
        self.canvas.create_text(80, 15, anchor="nw", text="Inventory", fill="white", font=("Helvetica", 16, "bold"))
        blue_card_img, self.canvas.blue_text_id = self.create_card_with_text("Assets/bluecard.png", 144, 50, self.blue_card_value)
        red_card_img, self.canvas.red_text_id = self.create_card_with_text("Assets/redcard.png", 10, 50, self.red_card_value)
        green_card_img, self.canvas.green_text_id = self.create_card_with_text("Assets/greencard.png", 144, 140, self.green_card_value)
        orange_card_img, self.canvas.orange_text_id = self.create_card_with_text("Assets/orangecard.png", 10, 140, self.orange_card_value)
        yellow_card_img, self.canvas.yellow_text_id = self.create_card_with_text("Assets/yellowcard.png", 144, 230, self.yellow_card_value)
        white_card_img, self.canvas.white_text_id = self.create_card_with_text("Assets/whitecard.png", 10, 230, self.white_card_value)
        black_card_img, self.canvas.black_text_id = self.create_card_with_text("Assets/blackcard.png", 144, 320, self.black_card_value)
        pink_card_img, self.canvas.pink_text_id = self.create_card_with_text("Assets/pinkcard.png", 10, 320, self.pink_card_value)
        joker_card_img, self.canvas.joker_text_id = self.create_card_with_text("Assets/jokercard.png", 77, 410, self.joker_card_value)

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

        #Update Roads
        self.create_roads()

        self.status_text_id =self.canvas.create_text(1280, 500, anchor="e", text="", fill="white", font=("Helvetica", 24, "bold"))

    def update_status_text(self, new_text):
        if not self.controller.visualize:  # optimization
            return

        self.canvas.itemconfig(self.status_text_id, text=new_text)

    def create_card_with_text(self, image_path, x, y, card_value):
        card_img = Image.open(image_path)
        card_img = card_img.resize((130, 85), Image.Resampling.LANCZOS)
        card_img = ImageTk.PhotoImage(card_img)
        self.canvas.create_image(x, y, anchor="nw", image=card_img)
        self.canvas.create_rectangle(x+52, y+32, x+78, y+52, fill="white", outline="black", width=2)
        text_id = self.canvas.create_text(x+65, y+42, text=str(card_value), fill="black", font=("Helvetica", 12, "bold"))
        return card_img, text_id

    def create_road_image(self, image_path, color):
        card_img = Image.open(image_path).convert("RGBA")
        card_img = card_img.resize((1284, 527), Image.Resampling.LANCZOS)

        # Seperate the alpha channel from the image so it will color only the opaque parts.
        r, g, b, alpha = card_img.split()
        grayscale_img = Image.merge("RGB", (r, g, b)).convert("L") #only colors the opaque part

        if color == "Blue":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="blue")
        elif color == "Red":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="red")
        elif color == "Green":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="green")
        elif color == "Yellow":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="yellow")
        elif color == "Black":
            colorized_img = ImageOps.colorize(grayscale_img, black="black", white="black")

        final_img = Image.merge("RGBA", (*colorized_img.split(), alpha))
        final_img = ImageTk.PhotoImage(final_img)
        created_road = self.canvas.create_image(0, 0, anchor="nw", image=final_img)
        return created_road, final_img

    def create_roads(self):
        if not self.controller.visualize:  # optimization
            return

        for route in self.controller.get_unclaimed_routes():
            if(hasattr(self.canvas, route.id)):
                self.canvas.delete(getattr(self.canvas, route.id))

        for route in self.controller.get_claimed_routes():
            road_image, road_image_img = self.create_road_image(route.get_image_path(), route.get_claimed_color())
            setattr(self.canvas, f"{route.id}", road_image)
            setattr(self.canvas, f"{route.id}_img", road_image_img)

    def update_train_numbers(self):
        if not self.controller.visualize:  # optimization
            return
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

    def create_select_card_for_gray_roads_frame(self, selected_route):
        if not self.controller.visualize:  # optimization
            return
        if self.select_card_for_gray_roads_frame is None:
            self.additional_frame = tk.Frame(self.root, width=1288, height=154, bg="#fdf8ed", highlightthickness=2, highlightbackground="#ae2907")
            self.additional_frame.place(x=-4, y=570)

            self.select_card_for_gray_roads_frame = tk.Frame(self.root, width=1800, height=188, bg="#fdf8ed", highlightthickness=2, highlightbackground="#ae2907")
            self.select_card_for_gray_roads_frame.place(x=0, y=570)
            label = tk.Label(self.select_card_for_gray_roads_frame, text="Select Card to Use", bg="#fdf8ed", fg="#ae2907", font=("Arial", 18, "bold"))
            label.pack(pady=5)

            card_options = self.controller.cards_needed_to_claim_gray_route(selected_route)
            selected_card = tk.StringVar(self.select_card_for_gray_roads_frame)
            selected_card.set(card_options[0])

            dropdown = ModernOptionMenu(self.select_card_for_gray_roads_frame, selected_card, *card_options)
            dropdown.config(width=20)
            dropdown.pack(pady=5)

            select_button = ModernButton(self.select_card_for_gray_roads_frame, text="Select", command=lambda: self.controller.claim_gray_route(selected_card.get(), selected_route))
            select_button.pack(pady=5)



    def destroy_select_card_for_gray_roads_frame(self):
        if self.select_card_for_gray_roads_frame is not None:
            self.select_card_for_gray_roads_frame.destroy()
            self.select_card_for_gray_roads_frame = None
            self.additional_frame.destroy()
            self.additional_frame = None

    def create_select_destination_tickets_canvas(self, card1, card2, card3):
        if not self.controller.visualize:  # optimization
            return
        if self.select_destination_tickets_canvas is None:

            self.select_destination_tickets_canvas = tk.Canvas(self.root, width=1280, height=270, bg="#fdf8ed", highlightthickness=2, highlightbackground="#ae2907")
            self.select_destination_tickets_canvas.place(x=-4, y=570)

            label = tk.Label(self.select_destination_tickets_canvas, text="Select Tickets", bg="#fdf8ed", fg="#ae2907", font=("Arial", 20, "bold"))
            label.place(x=10, y=5)

            # Selection variables
            self.check_var1 = tk.IntVar()
            self.check_var2 = tk.IntVar()
            self.check_var3 = tk.IntVar()


            if card1 is not None:
                # First Image and Checkbox
                self.selectable_dest_card_1_img = Image.open(card1.image_path)
                self.selectable_dest_card_1_img = self.selectable_dest_card_1_img.resize((225, 153), Image.Resampling.LANCZOS)
                self.selectable_dest_card_1_img = ImageTk.PhotoImage(self.selectable_dest_card_1_img)
                self.select_destination_tickets_canvas.selectable_dest_card_1_img_id = self.select_destination_tickets_canvas.create_image(210, 0, anchor="nw", image=self.selectable_dest_card_1_img)

                check_button1 = tk.Checkbutton(self.select_destination_tickets_canvas, bg="#ae2907", variable=self.check_var1, relief="flat", padx=5, pady=5)
                check_button1.place(x=220, y=110)

            if card2 is not None:
                # Second Image and Checkbox
                self.selectable_dest_card_2_img = Image.open(card2.image_path)
                self.selectable_dest_card_2_img = self.selectable_dest_card_2_img.resize((225, 153),
                                                                                         Image.Resampling.LANCZOS)
                self.selectable_dest_card_2_img = ImageTk.PhotoImage(self.selectable_dest_card_2_img)
                self.select_destination_tickets_canvas.selectable_dest_card_2_img_id = self.select_destination_tickets_canvas.create_image(435, 0, anchor="nw",
                                                                    image=self.selectable_dest_card_2_img)

                check_button2 = tk.Checkbutton(self.select_destination_tickets_canvas, bg="#ae2907", relief="flat", variable=self.check_var2, padx=5, pady=5)
                check_button2.place(x=445, y=110)

            if card3 is not None:
                # Third Image and Checkbox
                self.selectable_dest_card_3_img = Image.open(card3.image_path)
                self.selectable_dest_card_3_img = self.selectable_dest_card_3_img.resize((225, 153),
                                                                                         Image.Resampling.LANCZOS)
                self.selectable_dest_card_3_img = ImageTk.PhotoImage(self.selectable_dest_card_3_img)
                self.select_destination_tickets_canvas.selectable_dest_card_2_img_id = self.select_destination_tickets_canvas.create_image(660, 0, anchor="nw",
                                                                    image=self.selectable_dest_card_3_img)

                check_button3 = tk.Checkbutton(self.select_destination_tickets_canvas, bg="#ae2907", relief="flat", variable=self.check_var3, padx=5, pady=5)
                check_button3.place(x=670, y=110)

            # Apply Button
            apply_button = ModernButton(self.select_destination_tickets_canvas, text="Apply", command=lambda:self.apply_selection(card1,card2,card3), font_size=18)
            apply_button.place(x=28, y=50)

    def apply_selection(self, card1, card2, card3):
        list_of_selected = []

        sum = self.check_var1.get() + self.check_var2.get() + self.check_var3.get()
        if self.controller.game_manager.current_player.first_turn:
            if sum < 2:
                #console print("You must select at least two destination card!")
                return
        else:
            if sum == 0:
                #console print("You must select at least one destination card!")
                return

        if self.check_var1.get() == 1 and card1 is not None:
            list_of_selected.append(card1)
        if self.check_var2.get() == 1 and card2 is not None:
            list_of_selected.append(card2)
        if self.check_var3.get() == 1 and card3 is not None:
            list_of_selected.append(card3)
        self.destroy_select_destination_tickets_canvas()
        self.controller.draw_destination_ticket(list_of_selected)


    def destroy_select_destination_tickets_canvas(self):
        if self.select_destination_tickets_canvas is not None:
            self.select_destination_tickets_canvas.destroy()
            self.select_destination_tickets_canvas = None


