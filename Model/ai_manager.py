from Model.random_agent import RandomAgent
from Model.agent_x import AgentX
from Model.agent_qlearning_basic import QLearningAgent
from Model.DQNModel.dqn_agent import DQNAgent

class AIManager:
    def __init__(self, game_service):
        self.game_service = game_service
        self.agents = []

    def add_ai(self, color, agent_type):
        """Yeni bir yapay zekâ oyuncusu ekler."""

        if(agent_type == "RandomAgent"):
            random_agent = RandomAgent(color, self.game_service)
            self.agents.append(random_agent)
            #console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "AgentX"):
            agent_x = AgentX(color, self.game_service)
            self.agents.append(agent_x)
            #console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "QLearningAgent"):
            agent_q_learning_basic = QLearningAgent(color, self.game_service)
            self.agents.append(agent_q_learning_basic)
            #console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DeepQNetworkAgent"):
            deep_q_network_agent = DQNAgent(color, self.game_service)
            self.agents.append(deep_q_network_agent)
            #console print(f"AI Agent Added with color {color}, and agent type {agent_type}")

        #console print(self.agents)

    def reset_ai_list(self):
        self.agents.clear()
