from Model.random_agent import RandomAgent
from Model.agent_x import AgentX
from Model.agent_qlearning_basic import QLearningAgent
from Model.DQNModel.dqn_agent import DQNAgent
from Model.DQNModel2.dqn_agent import DQNAgent as DQNAgent2
from Model.DDQNModel_1_0.dqn_agent import DDQNAgent
from Model.DDQNModel_1_1.dqn_agent import DDQNAgent as DDQNAgent_PM
from Model.DDQNModel_1_2.dqn_agent import DDQNAgent as DDQNAgent_1_2
from Model.DDQNModel_1_4.dqn_agent import DDQNAgent as DDQNAgent_1_4
from Model.DDQNModel_1_4_1.dqn_agent import DDQNAgent as DDQNAgent_1_4_1
from Model.PPOModel_1_0.ppo_agent import PPOAgent as PPOAgent_1_0
from Model.PPOModel_1_1.ppo_agent import PPOAgent as PPOAgent_1_1
class AIManager:
    def __init__(self, game_service):
        self.game_service = game_service
        self.agents = []

    def add_ai(self, color, agent_type, persistent_model=None):
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
        if (agent_type == "2DeepQNetworkAgent"):
            deep_q_network_agent = DQNAgent2(color, self.game_service)
            self.agents.append(deep_q_network_agent)
            # console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DDQNAgent"):
            deep_q_network_agent = DDQNAgent(color, self.game_service)
            self.agents.append(deep_q_network_agent)
            # console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "2DDQNAgent"):
            deep_q_network_agent = DDQNAgent(color, self.game_service)
            deep_q_network_agent.model_filename = "2" + deep_q_network_agent.model_filename
            self.agents.append(deep_q_network_agent)
            # console print(f"AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DDQNAgent_PM"):
            deep_q_network_agent_pm = DDQNAgent_PM(color, self.game_service)
            self.agents.append(deep_q_network_agent_pm)
            print(f"DDQNAGENTPM AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DDQNAgent_1_2"):
            deep_q_network_agent_pm = DDQNAgent_1_2(color, self.game_service)
            self.agents.append(deep_q_network_agent_pm)
            print(f"DDQNAgent_1_2 AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DDQNAgent_1_4"):
            deep_q_network_agent_1_4 = DDQNAgent_1_4(color, self.game_service, persistent_model=persistent_model)
            self.agents.append(deep_q_network_agent_1_4)
            print(f"DDQNAgent_1_4 AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "DDQNAgent_1_4_1"):
            deep_q_network_agent_1_4_1 = DDQNAgent_1_4_1(color, self.game_service, persistent_model=persistent_model)
            self.agents.append(deep_q_network_agent_1_4_1)
            print(f"DDQNAgent_1_4 AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "PPOAgent_1_0"):
            ppo_agent_1_0 = PPOAgent_1_0(color, self.game_service)
            self.agents.append(ppo_agent_1_0)
            print(f"ppo_agent_1_0 AI Agent Added with color {color}, and agent type {agent_type}")
        if (agent_type == "PPOAgent_1_1"):
            ppo_agent_1_1 = PPOAgent_1_1(color, self.game_service)
            self.agents.append(ppo_agent_1_1)
            print(f"ppo_agent_1_1 AI Agent Added with color {color}, and agent type {agent_type}")
        #console print(self.agents)

    def reset_ai_list(self):
        self.agents.clear()
