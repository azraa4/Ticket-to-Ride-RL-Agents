from View.destination_tickets_view import DestinationTicketsFrame
from header_info_view import HeaderInfo
from train_card_selection_view import TrainCardSelectionFrame
from claimable_routes_view import ClaimableRoutesFrame
from draw_ticket_frame_view import DrawTicketFrame
from destination_tickets_view import DestinationTicketsFrame
from main_frame_view import MainFrame
from main_menu import MainMenu
from game_end_frame import GameEndFrame

from Controller.game_controller import GameController
from Controller.main_menu_controller import MainMenuController
from console import Console

from Model.game_manager import GameManager
from Model.ai_manager import AIManager

from Controller.game_service import GameService

import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

import threading

class MainGameApp:
    def __init__(self, game_controller, main_menu_controller):
        self.game_controller = game_controller

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


if __name__ == "__main__":
    #Define Models
    game_manager = GameManager()
    ai_manager = AIManager(None)


    #Define Controllerso
    game_controller = GameController(None, game_manager, None, None)
    main_menu_controller = MainMenuController(None, game_manager, ai_manager)

    # Define Main View
    app = MainGameApp(game_controller, main_menu_controller)

    ai_manager.game_service = app.game_service


    game_controller.view = app
    game_controller.game_service = app.game_service
    game_controller.ai_manager = ai_manager

    console = Console(app)
    console_thread = threading.Thread(target=console.open_console_window)
    console_thread.start()

    app.run()
