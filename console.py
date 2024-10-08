import tkinter as tk
from View.main_frame_view import MainFrame
from View.main_view import MainGameApp

def open_console_window(main_view_instance, main_frame_instance, train_cards_instance, claimable_routes_instance, draw_ticket_instance, header_instance):
    console_root = tk.Tk()
    console_root.title("Console Window")
    console_root.geometry("400x200")

    setup_button = tk.Button(console_root, text="Setup UI", command=main_view_instance.setup_ui)
    setup_button.place(x=0, y=0)

    # Add a button to update the destination tickets
    update_dest_tickets_button = tk.Button(console_root, text="Update Destination Tickets",
                                           command=main_frame_instance.update_destination_tickets)
    update_dest_tickets_button.place(x=0, y=50)

    update_ticket_numbers = tk.Button(console_root, text="Increase Red",
                                           command=main_frame_instance.update_ticket_numbers)
    update_ticket_numbers.place(x=0, y=100)


    console_root.mainloop()
