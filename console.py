import tkinter as tk
import inspect
import sys

class Console:
    def __init__(self, view):
        self.view = view
        self.console_root = None
        self.console_output = None

    def open_console_window(self):
        self.console_root = tk.Tk()
        self.console_root.title("Console Window")
        self.console_root.geometry("400x400")
        self.console_root.attributes("-topmost", True)

        # Create a Text widget to act like a console at the top
        self.console_output = tk.Text(self.console_root, height=20, state='disabled', bg='white', fg='black')
        self.console_output.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Frame for method entry and call button at the bottom
        bottom_frame = tk.Frame(self.console_root)
        bottom_frame.pack(side="bottom", fill="x", padx=5, pady=5)

        # Use grid for proper placement and fill
        bottom_frame.grid_columnconfigure(0, weight=5)
        bottom_frame.grid_columnconfigure(1, weight=1)

        # Entry for method input - spans full width
        self.method_entry = tk.Entry(bottom_frame)
        self.method_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Call Method Button - aligned to the right
        call_method_button = tk.Button(bottom_frame, text="Call", command=self.call_method)
        call_method_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.help()
        self.console_root.mainloop()

    def setup_ui(self):
        """Calls the setup UI method from the view."""
        self.view.setup_ui()

    def update_destination_tickets(self):
        """Updates the destination tickets using view's main_frame."""
        self.view.main_frame.update_destination_tickets()

    def update_train_numbers(self):
        """Updates the train numbers using view's main_frame."""
        self.view.main_frame.update_train_numbers()

    def update_train_cards(self):
        """Updates the train cards using view's train_cards."""
        self.view.train_cards.update_train_card_selection_frame()

    def update_all_UI(self):
        """Updates all parts of the UI by calling respective update methods."""
        self.update_train_cards()
        self.update_train_numbers()
        self.update_destination_tickets()

    def claim_route(self, route_id, player_name):
        """Claims a route based on input values from the entry fields."""
        if route_id and player_name:
            # Assuming 'view.game_controller' has a 'claim_route' method
            self.view.game_controller.claim_route(route_id, player_name)

    def log_to_console(self, text):
        """Adds text to the console output area."""
        self.console_output.config(state='normal')  # Enable editing
        self.console_output.insert(tk.END, text + '\n')  # Insert text at the end
        self.console_output.see(tk.END)  # Scroll to the bottom
        self.console_output.config(state='disabled')  # Disable editing again

    def update_turn_text(self, text):
        self.view.game_controller.update_turn_text(text)

    def go_to_next_turn(self):
        self.view.game_controller.go_to_next_turn()

    def force_go_to_next_turn(self):
        self.view.game_controller.force_go_to_next_turn()

    def print_claimable_routes(self):
        self.view.game_controller.get_claimable_routes()

    def clear_routes_frame(self):
        self.view.claimable_routes.clear_routes_frame()

    def turn_availability(self, bool_string):
        bool = None
        if(bool_string == "True" or bool_string == "true"):
            bool = True
        elif (bool_string == "False" or bool_string == "false"):
            bool = False

        self.view.game_controller.change_turn_availability(bool)

    def change_player_cars(self, player_index, car_amount):
        self.view.game_controller.change_player_cars(int(player_index), int(car_amount))

    def show_end_game_frame(self):
        self.view.game_controller.show_game_end_frame()

    #game_services control
    def ai_get_game_state(self):
        self.view.game_service.get_game_state()

    def ai_get_current_player_state(self):
        self.view.game_service.get_current_player_state()

    def ai_get_available_actions(self, player_color):
        self.view.game_service.get_available_actions(player_color)

    def ai_claim_route_example(self):
        player_state = self.view.game_service.get_current_player_state()

        claimable_route = player_state["claimable_routes"][0]

        action_params_1 = {"selected_route": claimable_route, "use_this_color" : None}
        returned_list_of_colors = self.view.game_service.perform_action("claim_route", action_params_1)

        action_params_2 = {"selected_route": claimable_route, "use_this_color" : returned_list_of_colors[0]}
        self.view.game_service.perform_action("claim_route", action_params_2)

    def ai_draw_train_card_example(self):
        game_state = self.view.game_service.get_game_state()

        train_cards_on_the_table = game_state["train_cards_on_the_table"]


        #action_params = {"selected_card": train_cards_on_the_table[0]}
        action_params = {"selected_card": "select_blind"}
        self.view.game_service.perform_action("draw_train_card", action_params)

    def ai_draw_destination_ticket_example(self):
        action_params = None
        list_of_available_destination_tickets = self.view.game_service.perform_action("draw_destination_ticket", action_params)

        action_params = {"selected_destination_tickets": [list_of_available_destination_tickets[0]]}
        self.view.game_service.perform_action("draw_destination_ticket", action_params)

    def call_method(self):
        """Dynamically calls a method by name with arguments inside parentheses and logs to console."""
        full_input = self.method_entry.get()  # Full input in the format: method_name(arg1, arg2)

        # Extract method name and arguments from the input
        method_name, args_text = full_input.split("(", 1)
        method_name = method_name.strip()  # Strip spaces around method name
        args_text = args_text.rstrip(")")  # Remove closing parenthesis

        self.log_to_console(f"> {method_name}({args_text})")

        # Find the method in this Console class using getattr()
        method_to_call = getattr(self, method_name, None)
        if method_to_call is None:
            self.log_to_console(f"Error: Method {method_name} not found.")
            return

        # Get the method's signature (i.e., its parameters)
        sig = inspect.signature(method_to_call)
        params = sig.parameters

        # Split the arguments by commas, trim spaces, and handle no-argument methods
        if args_text:
            args = [arg.strip() for arg in args_text.split(",")]
        else:
            args = []

        # If the number of arguments does not match, return an error
        if len(args) != len(params):
            self.log_to_console(f"Error: Expected {len(params)} arguments, but got {len(args)}.")
            return

        # Call the method with the provided arguments
        method_to_call(*args)
        self.log_to_console(f"Method {method_name} executed successfully.")

    def help(self):
        """Prints the names of all methods in this class along with their input parameters to the console."""
        methods = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        self.log_to_console("Methods:")
        for method in methods:
            method_func = getattr(self, method)
            sig = inspect.signature(method_func)  # Get method signature
            self.log_to_console(f"- {method}{sig}")

