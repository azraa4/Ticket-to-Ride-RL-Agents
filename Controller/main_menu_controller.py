import global_vars
class MainMenuController:

    def __init__(self, view, game_manager, ai_manager):
        self.view = view
        self.game_manager = game_manager
        self.ai_manager = ai_manager
        global_vars.time_action = 5
        global_vars.time_turn = 5
        return

    def add_player_button(self, player_name, player_color, ai):
        self.game_manager.add_player(player_name, player_color, ai)

    def reset_player_list_button(self):
        self.game_manager.reset_players_list()
        self.ai_manager.reset_ai_list()

    def add_ai(self, ai_color, ai_type):
        self.ai_manager.add_ai(ai_color, ai_type)

    def force_start_game(self):
        self.view.force_start_game()