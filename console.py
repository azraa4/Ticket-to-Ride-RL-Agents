import tkinter as tk
from View.main_frame_view import MainFrame
from View.main_view import MainGameApp

def open_console_window(main_view_instance, main_frame_instance, train_cards_instance, claimable_routes_instance, draw_ticket_instance, header_instance):
    console_root = tk.Tk()
    console_root.title("Console Window")
    console_root.geometry("400x200")

    setup_button = tk.Button(console_root, text="Setup UI #pencereyi tekrar oluşturur refresh etmez refresh için kullanma :D", command=main_view_instance.setup_ui)
    setup_button.place(x=0, y=0)

    # Add a button to update the destination tickets
    update_dest_tickets_button = tk.Button(console_root, text="Update Destination Tickets",
                                           command=main_frame_instance.update_destination_tickets)
    update_dest_tickets_button.place(x=0, y=25)

    update_train_numbers = tk.Button(console_root, text="Update Train Numbers",
                                           command=main_frame_instance.update_train_numbers)
    update_train_numbers.place(x=0, y=50)

    update_train_cards = tk.Button(console_root, text="Update Train Cards",
                                     command=train_cards_instance.update_train_card_selection_frame)
    update_train_cards.place(x=0, y=75)

    def update_all_UI():
        train_cards_instance.update_train_card_selection_frame()
        main_frame_instance.update_train_numbers()
        main_frame_instance.update_destination_tickets()

    update_all_ui = tk.Button(console_root, text="Update All UI",
                                   command=update_all_UI)
    update_all_ui.place(x=0, y=100)



    console_root.mainloop()

