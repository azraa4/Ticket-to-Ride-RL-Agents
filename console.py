import tkinter as tk


def open_console_window(view):
    console_root = tk.Tk()
    console_root.title("Console Window")
    console_root.geometry("400x400")


    setup_button = tk.Button(console_root, text="Setup UI #pencereyi tekrar oluşturur refresh etmez refresh için kullanma :D", command=view.setup_ui)
    setup_button.place(x=0, y=0)

    # Add a button to update the destination tickets
    update_dest_tickets_button = tk.Button(console_root, text="Update Destination Tickets",
                                           command=view.main_frame.update_destination_tickets)
    update_dest_tickets_button.place(x=0, y=25)

    update_train_numbers = tk.Button(console_root, text="Update Train Numbers",
                                           command=view.main_frame.update_train_numbers)
    update_train_numbers.place(x=0, y=50)

    update_train_cards = tk.Button(console_root, text="Update Train Cards",
                                     command=view.train_cards.update_train_card_selection_frame)
    update_train_cards.place(x=0, y=75)

    def update_all_UI():
        view.train_cards.update_train_card_selection_frame()
        view.main_frame.update_train_numbers()
        view.main_frame.update_destination_tickets()

    update_all_ui = tk.Button(console_root, text="Update All UI",
                                   command=update_all_UI)
    update_all_ui.place(x=0, y=100)

    # Label and Entry for Route ID
    route_id_label = tk.Label(console_root, text="Route ID:")
    route_id_label.place(x=0, y=130)
    route_id_entry = tk.Entry(console_root)
    route_id_entry.place(x=100, y=130)

    # Label and Entry for Player
    player_label = tk.Label(console_root, text="Player:")
    player_label.place(x=0, y=160)
    player_entry = tk.Entry(console_root)
    player_entry.place(x=100, y=160)

    # Function to claim route using the entered data
    def claim_route_action():
        route_id = route_id_entry.get()
        player_name = player_entry.get()
        if route_id and player_name:
            # Assuming 'claimable_routes_instance' has the 'claim_route' method
            view.game_controller.claim_route(route_id, player_name)

    # Button to claim route
    claim_route_button = tk.Button(console_root, text="Claim Route", command=claim_route_action)
    claim_route_button.place(x=0, y=190)



    console_root.mainloop()