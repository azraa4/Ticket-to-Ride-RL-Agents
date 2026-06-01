# Ticket to AI: Deep Reinforcement Learning for Ticket to Ride

A digitized version of the *Ticket to Ride* board game, extended with Deep Reinforcement Learning agents (DDQN & PPO) capable of strategic, turn-based decision-making. Developed as a Senior Design Project at Özyeğin University.

---

## Academic Context & Authorship

This repository contains the implementation, evaluation, and official documentation for the Senior Design Project developed at **Özyeğin University (CS 402)**.

The project was officially co-authored by **Azra Açıl** and **Emirhan Tandoğan**, under the academic supervision of **Prof. Reyhan Aydoğan**. 

---

## My Role & Focus Area
 
While the codebase was developed collaboratively, my primary focus and contributions were centered around:
 
- **Reinforcement Learning Agent** — implementing the initial RL agent that formed the basis for the project's learning-based gameplay (see the `Added RlAgent` commits authored by `azraa4`).
- **Core Game Mechanics** — developing the destination ticket system and the train card deck logic.
- **System Architecture & Documentation** — contributing to the Model–View–Controller (MVC) structure and documenting the integration of the RL agents.
- **Evaluation & Analysis** — analyzing the cumulative reward plots, smoothed reward trends, and training loss curves of the PPO and DDQN models to benchmark agent performance.
- **Academic Reporting** — compiling the empirical results into the final academic report.
Commits under the author `azraa4` in the commit history reflect part of this work.

---

## Project Abstract

This project focuses on enhancing a digital version of the *Ticket to Ride* board game by developing reinforcement learning (RL) agents capable of strategic decision-making and adapting to gameplay dynamics.

In the **first phase**, the game was digitized using Python and Tkinter, following the Model–View–Controller (MVC) architecture and object-oriented programming principles. A digitized game environment, a tournament panel, and a rule-based agent (AgentX) were developed to support AI-vs-AI and human-vs-AI gameplay.

In the **second phase**, the framework was extended with several RL agents, including Double DQN (DDQN) and Proximal Policy Optimization (PPO). The control panel was redesigned to support automated training loops, model saving/loading, and concurrent game execution. Agent performance was evaluated using cumulative reward plots, smoothed reward trends, and training loss curves.

The system now serves as a comprehensive platform for RL experimentation, agent benchmarking, and ongoing research in game-playing AI within strategic, turn-based environments.

---

## Tech Stack

- **Language:** Python
- **GUI:** Tkinter
- **Deep Learning:** PyTorch (DDQN & PPO)
- **Architecture:** Model–View–Controller (MVC), OOP

---

## Project Structure

```
Controller/   # game flow and agent-environment control logic
Model/        # game state, RL models and training logic
View/         # rendering and UI
Panel/        # tournament panel and UI widgets
Assets/       # images and game assets
console.py    # console entry point
main_view.py  # GUI entry point
global_vars.py
requirements.txt
```

---

## Getting Started

```bash
git clone https://github.com/azraa4/Ticket-to-Ride-RL-Agents.git
cd Ticket-to-Ride-RL-Agents
pip install -r requirements.txt
python main_view.py
```

Pre-trained model weights are included: `ddqn_model_final.pth` and `ppoagent_final.pth`.

---

## Team

- **Azra Açıl** 
- **Emirhan Tandoğan**

*Supervised by Prof. Reyhan Aydoğan, Özyeğin University.*
