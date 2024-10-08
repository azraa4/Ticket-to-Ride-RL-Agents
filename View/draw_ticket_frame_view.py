import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class DrawTicketFrame:
    def __init__(self, root):
        self.root = root

    def create_draw_ticket_frame(self):
        ticket_frame = tk.Frame(self.root, width=120, height=150, bg="#fdf8ed", highlightthickness=4,
                                highlightbackground="#e4a21d")
        ticket_frame.place(x=1160, y=570)

        image = Image.open("../Assets/Ticket.jpg")
        image = image.resize((110, 106), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(image)

        image_label = tk.Label(ticket_frame, image=img, bg="#fdf8ed")
        image_label.image = img
        image_label.place(x=0, y=0)

        draw_ticket_card_button = TTRGui.create_modern_button(ticket_frame, "Draw Ticket Card", 0, 110, 14, 2, 10)
