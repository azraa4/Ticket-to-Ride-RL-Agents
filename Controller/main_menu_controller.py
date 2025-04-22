import global_vars
class MainMenuController:

    def __init__(self, view, game_manager, ai_manager):
        self.view = view
        self.game_manager = game_manager
        self.ai_manager = ai_manager
        global_vars.time_action = 5
        global_vars.time_turn = 5
        self.main_view = None
        return

    def add_player_button(self, player_name, player_color, ai):
        self.game_manager.add_player(player_name, player_color, ai)

    def reset_player_list_button(self):
        self.game_manager.reset_players_list()
        self.ai_manager.reset_ai_list()

    def add_ai(self, ai_color, ai_type, persistent_model = None):
        self.ai_manager.add_ai(ai_color, ai_type, persistent_model)

    def force_start_game(self):
        self.view.force_start_game()

    def block_human_vision(self, b):
        if b:
            self.main_view.main_frame.block_humans = True
        else:
            self.main_view.main_frame.block_humans = False