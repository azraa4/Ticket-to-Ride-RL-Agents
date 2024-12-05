from Model.agent import Agent


class AIManager:
    def __init__(self, game_service):
        self.game_service = game_service
        self.agents = []

    def add_ai(self, color):
        """Yeni bir yapay zekâ oyuncusu ekler."""
        agent = Agent(color, self.game_service)
        self.agents.append(agent)
        print(f"AI Agent Added with color {color}")
        print(self.agents)

    def reset_ai_list(self):
        self.agents.clear()
