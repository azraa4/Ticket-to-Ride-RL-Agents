import tkinter as tk
from PIL import Image, ImageTk


def create_modern_button(parent, text, x, y, width=10, height=2, font=12):
    # Colours
    colour1 = "#c0954a"  # Normal
    colour2 = "#c0954a"  # Highlight
    colour3 = "#d28840"  # Clicked
    colour4 = "#ffffff"  # White
    button = tk.Button(
        parent,
        background=colour1,
        foreground=colour4,
        activebackground=colour3,
        activeforeground=colour4,
        highlightthickness=2,
        highlightbackground=colour2,
        highlightcolor="WHITE",
        width=width,
        height=height,
        border=0,
        cursor='hand1',
        text=text,
        font=('Arial', font, 'bold')
    )
    button.place(x=x, y=y)
    return button

def create_logo_frame():
    logo_frame = tk.Frame(root, width=240, height=150, bg="#fdf8ed")
    logo_frame.place(x=0, y=0)

    #logo image
    image = Image.open("../Assets/TTR_logo.png")
    image = image.resize((200, 150), Image.Resampling.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)
    logo_label = tk.Label(logo_frame, image=logo_image)
    logo_label.place(x=0, y=0)
    logo_label.image = logo_image

def create_train_card_selection_frame():
    train_card_selection_frame = tk.Frame(root, width=840, height=150, bg="#fdf8ed", highlightthickness=2, highlightbackground="#d7ab5e")
    train_card_selection_frame.place(x=200, y=0)

    frame_width = 130
    frame_height = 140
    total_width = 800

    num_frames = 6
    spacing = (total_width - (num_frames * frame_width)) // (num_frames + 1)

    for i in range(num_frames):
        x_position = 40 + spacing + i * (frame_width + spacing)

        inner_frame = tk.Frame(train_card_selection_frame, width=frame_width, height=frame_height, bg="#d7ab5e")
        inner_frame.place(x=x_position, y=3)
        if(i!=5):
            train_card_pick_button = create_modern_button(inner_frame, "Pick", 0, 110, 13, 1)
            image = Image.open("../Assets/white_train.jpg")
            image = image.resize((128, 107), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(image)

            image_label = tk.Label(inner_frame, image=img, bg="#fdf8ed")
            image_label.image = img
            image_label.place(x=0, y=0)
        else:
            blind_pick_button = create_modern_button(inner_frame, "Blind Pick", 0, 110, 13, 1)
            image = Image.open("../Assets/deck.jpg")
            image = image.resize((128, 107), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(image)

            image_label = tk.Label(inner_frame, image=img, bg="#fdf8ed")
            image_label.image = img
            image_label.place(x=0, y=0)


def create_claimable_routes_frame():
    claimable_routes_frame = tk.Frame(root, width=240, height=570, bg="#fdf8ed", highlightthickness=2, highlightbackground="#d7ab5e")
    claimable_routes_frame.place(x=1040, y=150)

    claimable_routes_title_label = tk.Label(claimable_routes_frame, text="Claimable Routes", fg="#e60506", font=("Arial", 16, "bold"))
    claimable_routes_title_label.place(x=0, y=0)

def create_players_info_frame():
    players_info_frame = tk.Frame(root, width=240, height=150, bg="#fdf8ed", highlightthickness=2, highlightbackground="#d7ab5e")
    players_info_frame.place(x=0, y=0)

    player_info_label = tk.Label(players_info_frame, text="Player Info", fg="#e60506", font=("Arial", 16, "bold"))
    player_info_label.place(x=0, y=0)

def create_map_frame():
    players_info_frame = tk.Frame(root, width=800, height=570, bg="black")
    players_info_frame.place(x=240, y=150)

def create_draw_ticket_frame():
    players_info_frame = tk.Frame(root, width=240, height=150, bg="#fdf8ed", highlightthickness=2, highlightbackground="#d7ab5e")
    players_info_frame.place(x=1040, y=0)
    draw_ticket_card_button = create_modern_button(players_info_frame, "Draw Ticket Card", 0, 120, 23, 1)

    image = Image.open("../Assets/Ticket.jpg")
    image = image.resize((235, 118), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(image)

    image_label = tk.Label(players_info_frame, image=img, bg="#fdf8ed")
    image_label.image = img
    image_label.place(x=0, y=0)
def create_inventory_frame():
    inventory_frame = tk.Frame(root, width=240, height=570, bg="#fdf8ed", highlightthickness=2, highlightbackground="#d7ab5e")
    inventory_frame.place(x=0, y=150)

    inventory_title_label = tk.Label(inventory_frame, text="Inventory", fg="#e60506", font=("Arial", 16, "bold"))
    inventory_title_label.place(x=0, y=0)


root = tk.Tk()
root.title("Ticket to Ride")
root.geometry("1280x720")
root.resizable(False, False)

create_logo_frame()
create_train_card_selection_frame()
create_players_info_frame()
create_inventory_frame()
create_map_frame()
create_claimable_routes_frame()
create_draw_ticket_frame()

root.mainloop()
