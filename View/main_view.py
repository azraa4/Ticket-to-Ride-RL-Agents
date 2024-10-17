from header_info_view import HeaderInfo
from train_card_selection_view import TrainCardSelectionFrame
from claimable_routes_view import ClaimableRoutesFrame
from draw_ticket_frame_view import DrawTicketFrame
from main_frame_view import MainFrame
from Model.Board import Board

from Controller.game_controller import GameController
import console

import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

import threading

class MainGameApp:
    def __init__(self, game_controller):

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

    def setup_ui(self):
        self.train_cards.create_train_card_selection_frame()
        self.claimable_routes.create_claimable_routes_frame()
        self.draw_ticket.create_draw_ticket_frame()
        self.main_frame.create_main_frame()
        self.header.create_header_info_frame()

    def run(self):
        self.setup_ui()
        self.root.mainloop()


if __name__ == "__main__":
    #Define Models
    board = Board()


    #Defin Controller
    game_controller = GameController(None, board)

    # Define Main View
    app = MainGameApp(game_controller)

    game_controller.view = app

    console_thread = threading.Thread(target=console.open_console_window, args=(app, ))
    console_thread.start()

    app.run()