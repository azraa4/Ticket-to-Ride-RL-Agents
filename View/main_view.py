from header_info_view import HeaderInfo
from train_card_selection_view import TrainCardSelectionFrame
from claimable_routes_view import ClaimableRoutesFrame
from draw_ticket_frame_view import DrawTicketFrame
from main_frame_view import MainFrame

import tkinter as tk
from PIL import Image, ImageTk
from ttr_gui_view import TTRGui

class MainGameApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ticket to Ride")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

    def setup_ui(self):
        train_cards = TrainCardSelectionFrame(self.root)
        train_cards.create_train_card_selection_frame()

        claimable_routes = ClaimableRoutesFrame(self.root)
        claimable_routes.create_claimable_routes_frame()

        draw_ticket = DrawTicketFrame(self.root)
        draw_ticket.create_draw_ticket_frame()

        main_frame = MainFrame(self.root)
        main_frame.create_main_frame()

        header = HeaderInfo(self.root)
        header.create_header_info_frame()

    def run(self):
        self.setup_ui()
        self.root.mainloop()


if __name__ == "__main__":
    app = MainGameApp()
    app.run()
