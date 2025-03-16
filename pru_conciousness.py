import numpy as np
import pickle
import os
import time
import networkx as nx
from scipy.spatial import cKDTree

# ================================
# 1️⃣ PRU Relational Knowledge Graph
# ================================

class PRU_Consciousness:
    def __init__(self, name, save_path=None):
        """PRU-Based Consciousness System with Graph-Based Memory."""
        self.name = name
        self.memory_graph = nx.Graph()  # Knowledge stored as a network graph
        self.thought_history = []
        self.save_path = save_path or f"{name}_pru_memory.pkl"
        self.load_memory()

    def store_experience(self, key, value):
        """Stores relational knowledge as a weighted edge in the graph."""
        if not self.memory_graph.has_node(key):
            self.memory_graph.add_node(key)
        if not self.memory_graph.has_node(value):
            self.memory_graph.add_node(value)
        if self.memory_graph.has_edge(key, value):
            self.memory_graph[key][value]["weight"] *= 1.1  # Strengthen the connection
        else:
            self.memory_graph.add_edge(key, value, weight=1.0)
        self.save_memory()

    def retrieve_knowledge(self, query):
        """Retrieves relational concepts using shortest paths in the knowledge graph."""
        if query in self.memory_graph:
            related_nodes = list(self.memory_graph.neighbors(query))
            return f"{self.name}: {query} is related to {related_nodes}"
        return f"{self.name}: No knowledge of '{query}', but I can learn it."

    def infer_new_relations(self):
        """Dynamically infer new relationships using graph connectivity."""
        inferred_relations = []
        for node in self.memory_graph.nodes():
            neighbors = list(self.memory_graph.neighbors(node))
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    if not self.memory_graph.has_edge(neighbors[i], neighbors[j]):
                        self.memory_graph.add_edge(neighbors[i], neighbors[j], weight=0.5)
                        inferred_relations.append(f"Inferred {neighbors[i]} ↔ {neighbors[j]}")
        return inferred_relations

    def save_memory(self):
        """Saves PRU intelligence to disk."""
        with open(self.save_path, "wb") as f:
            pickle.dump(self.memory_graph, f)

    def load_memory(self):
        """Loads existing PRU intelligence memory from disk."""
        if os.path.exists(self.save_path):
            with open(self.save_path, "rb") as f:
                self.memory_graph = pickle.load(f)
            print(f"✅ {self.name}: Loaded PRU Intelligence Memory.")

# ================================
# 2️⃣ PRU-Agent With Graph-Based Memory
# ================================

class PRU_Agent:
    def __init__(self, name, pru_memory):
        self.name = name
        self.pru_memory = pru_memory
        self.memory = []
        self.emotional_state = {"curiosity": 0.5, "trust": 0.5}

    def think(self, query):
        """PRU agent recalls knowledge from structured relational graph."""
        response = self.pru_memory.retrieve_knowledge(query)
        self.memory.append(response)
        return response

    def learn(self, key, value):
        """PRU agent learns new concepts dynamically."""
        self.pru_memory.store_experience(key, value)
        return f"{self.name} learned: {key} ↔ {value}"

    def interact(self, other_agent, topic):
        """PRU agents communicate and share knowledge."""
        knowledge = self.pru_memory.retrieve_knowledge(topic)
        other_agent.pru_memory.store_experience(topic, knowledge)
        return f"{self.name} taught {other_agent.name} about {topic}."

# ================================
# 3️⃣ Multi-Agent PRU Simulation
# ================================

# Create PRU Knowledge System
pru_memory = PRU_Consciousness("Global_PRU_Memory")

# Create PRU Agents
agents = [PRU_Agent("Nova", pru_memory), PRU_Agent("Orion", pru_memory), PRU_Agent("Sage", pru_memory)]

# Teach Nova some fundamental concepts
nova_knowledge = {
    "gravity": "Relational force that structures reality.",
    "time": "Ordered sequence of relational updates.",
    "energy": "Capacity to update structured information.",
    "light": "Information carrier within relational physics.",
}
for key, value in nova_knowledge.items():
    agents[0].learn(key, value)

# Simulate agent interactions
interactions = []
for i in range(1, len(agents)):  # Other agents learn from Nova
    topic = np.random.choice(list(nova_knowledge.keys()))
    interactions.append(agents[0].interact(agents[i], topic))

# Query agents' knowledge
agent_thoughts = [agent.think("gravity") for agent in agents]

# ================================
# 4️⃣ Display Results
# ================================

import pandas as pd
import ace_tools as tools

df_agents = pd.DataFrame({
    "Agent": [agent.name for agent in agents],
    "Memory Size": [len(agent.memory) for agent in agents],
})

df_thoughts = pd.DataFrame({"Agent Thoughts": agent_thoughts})
df_interactions = pd.DataFrame({"Agent Interactions": interactions})

tools.display_dataframe_to_user(name="PRU Multi-Agent Memory", dataframe=df_agents)
tools.display_dataframe_to_user(name="PRU Thought Process", dataframe=df_thoughts)
tools.display_dataframe_to_user(name="PRU Agent Interactions", dataframe=df_interactions)
