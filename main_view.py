from View.destination_tickets_view import DestinationTicketsFrame
from View.header_info_view import HeaderInfo
from View.train_card_selection_view import TrainCardSelectionFrame
from View.claimable_routes_view import ClaimableRoutesFrame
from View.draw_ticket_frame_view import DrawTicketFrame
from View.destination_tickets_view import DestinationTicketsFrame
from View.main_frame_view import MainFrame
from View.main_menu import MainMenu
from View.game_end_frame import GameEndFrame

from Controller.game_controller import GameController
from Controller.main_menu_controller import MainMenuController
from console import Console

from Model.game_manager import GameManager
from Model.ai_manager import AIManager

from Controller.game_service import GameService

import tkinter as tk
from PIL import Image, ImageTk
from View.ttr_gui_view import TTRGui

import threading
import sys
import time

import global_vars
class MainGameApp:
    def __init__(self, game_controller, main_menu_controller, queue=None, game_id=None):
        self.game_controller = game_controller
        self.queue = queue  # Queue nesnesi
        self.game_id = game_id  # Bu oyunun kimliği

        self.root = tk.Tk()
        self.root.title("Ticket to Ride")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)


        #all views
        self.main_frame = MainFrame(self.root, game_controller)
        self.train_cards = TrainCardSelectionFrame(self.root, game_controller)
        self.claimable_routes = ClaimableRoutesFrame(self.root, game_controller)
        self.draw_ticket = DrawTicketFrame(self.root, game_controller)
        self.header = HeaderInfo(self.root, game_controller)
        self.destination_tickets = DestinationTicketsFrame(self.root, game_controller)
        self.game_end_frame = GameEndFrame(self.root, game_controller)

        #main menu view
        self.main_menu = MainMenu(self.root, main_menu_controller, self.start_game)

        #game_services
        self.game_service = GameService(game_controller)


        if self.queue:
            self.message_thread = threading.Thread(target=self.listen_to_queue)
            self.message_thread.daemon = True  # Programla birlikte kapanacak
            self.message_thread.start()

    def listen_to_queue(self):
        """Queue'den gelen mesajları dinler ve işler."""
        while True:
            if self.queue is not None and not self.queue.empty():
                message = self.queue.get()  # Mesajı al
                self.process_message(message)

    def process_message(self, message):
        """Panelden gelen mesajları işler."""
        if message.startswith(f"printThisInGame_{self.game_id}"):
            _, text = message.split(":", 1)
            print(f"Game {self.game_id}: {text}")

        elif message == f"stop_{self.game_id}":
            print(f"Stopping game {self.game_id}.")
            self.game_controller.game_end = True
            time.sleep(5)
            self.stop_game()

    def setup_ui(self):
        self.train_cards.create_train_card_selection_frame()
        self.claimable_routes.create_claimable_routes_frame()
        self.draw_ticket.create_draw_ticket_frame()
        self.main_frame.create_main_frame()
        self.header.create_header_info_frame()
        self.destination_tickets.create_destination_tickets_frame()

    def run(self):
        self.main_menu.create_menu()
        self.root.mainloop()

    def start_game(self):
        self.setup_ui()
        self.game_controller.start_game()

    def stop_game(self):
        self.root.destroy()

    def withdraw_window(self):
        self.root.withdraw()
        self.game_controller.visualize = False


def main(queue=None, game_id=None, panel=None, console=None, agents=None, visualize=None, test_name=None, time_action=None, time_turn=None):
    # Define Models
    game_manager = GameManager()
    ai_manager = AIManager(None)

    # Define Controllers
    game_controller = GameController(None, game_manager, None, None, test_name)
    main_menu_controller = MainMenuController(None, game_manager, ai_manager)

    # Define Main View
    app = MainGameApp(game_controller, main_menu_controller, queue, game_id)

    ai_manager.game_service = app.game_service

    game_controller.view = app
    game_controller.game_service = app.game_service
    game_controller.ai_manager = ai_manager

    main_menu_controller.view = app.main_menu


    if console:
        console = Console(app)
        console_thread = threading.Thread(target=console.open_console_window)
        console_thread.start()

    if panel:
        game_controller.stop_process_end_game = True

        global_vars.time_turn = time_turn
        global_vars.time_action = time_action

        if not visualize:
            app.withdraw_window()

        for agent in agents:
            agent_type = agent["agent_type"]
            color = agent["color"]

            main_menu_controller.add_player_button(f"AI_{color}", color, True)
            main_menu_controller.add_ai(color, agent_type)

        main_menu_controller.force_start_game()

    app.run()

if __name__ == "__main__":
    main()


