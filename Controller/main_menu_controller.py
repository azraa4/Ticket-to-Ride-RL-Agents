class MainMenuController:

    def __init__(self, view, game_manager):
        self.view = view
        self.game_manager = game_manager

        return

    def add_player_button(self, player_name, player_color):
        self.game_manager.add_player(player_name, player_color)
