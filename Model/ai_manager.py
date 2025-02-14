from Model.random_agent import RandomAgent
from Model.agent_x import AgentX
from Model.RLagent import RLAgent

class AIManager:
    def __init__(self, game_service):
        self.game_service = game_service
        self.agents = []

    def add_ai(self, color, agent_type):
        """Yeni bir yapay zekâ oyuncusu ekler."""

        if(agent_type == "RandomAgent"):
            random_agent = RandomAgent(color, self.game_service)
            self.agents.append(random_agent)
            print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "AgentX"):
            agent_x = AgentX(color, self.game_service)
            self.agents.append(agent_x)
            print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "RLAgent"):
            rl_agent = RLAgent(color, self.game_service)
            self.agents.append(rl_agent)
            print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        print(self.agents)

    def reset_ai_list(self):
        self.agents.clear()
