import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# Define the Masters with improved, emergent influences.
# Note: Rather than fixed physical constants, these factors serve as emergent coefficients.
MASTERS = {
    "Master of Hidden Magic": {"invert_state": True, "entropy_boost": 3},
    "Lord of Life": {"grant_freedom": True, "increase_potential": 5},
    "Master of Progress": {"balance_weights": True, "achieve_equilibrium": True},
    "Lord of Light": {"amplify_knowledge": 2},
    "Keeper of Space-Time": {"adjust_position": 1, "adjust_velocity": 0.5, "time_dilation": 0.1},
    "Master of Harmony": {"align_entropy": -1, "restore_balance": True},
    "Lord of Infinity": {"expand_senses": 1, "extend_memory": 2},
    "Master of Quantum Relativity": {"emergent_force": 0.05, "entanglement_influence": 0.2},
}

# Enhanced Entity class with velocity and an emergent mass computed from its state.
class Entity:
    def __init__(self, name, position, senses, state, memory_size=5):
        self.name = name
        self.position = np.array(position, dtype=float)
        self.velocity = np.random.uniform(-0.5, 0.5, size=self.position.shape)  # small random initial velocity
        self.senses = senses.copy()
        self.state = {"knowledge": state[0], "entropy": state[1], "alignment": state[2]}
        self.memory = []  # Record of past states
        self.memory_size = memory_size
        # Emergent mass (for dynamics) derived from entropy
        self.mass = self.state["entropy"] if self.state["entropy"] > 0 else 1

    def sense_environment(self, entities):
        """Detect nearby entities within the sensing range."""
        perceived = []
        for entity in entities:
            if entity.name != self.name:
                distance = np.linalg.norm(self.position - entity.position)
                if distance <= self.senses["range"]:
                    perceived.append((entity.name, entity.state))
        return perceived

    def update_memory(self):
        """Record the current state, respecting the memory size limit."""
        if len(self.memory) >= self.memory_size:
            self.memory.pop(0)
        self.memory.append(self.state.copy())

    def apply_master_influence(self, influence):
        """Modify state, position, and velocity based on a master influence."""
        if influence.get("invert_state"):
            self.state["alignment"] *= -1
        if influence.get("entropy_boost"):
            self.state["entropy"] += influence["entropy_boost"]
            self.mass = self.state["entropy"] if self.state["entropy"] > 0 else self.mass
        if influence.get("grant_freedom"):
            self.state["alignment"] = 0
        if influence.get("increase_potential"):
            self.state["knowledge"] += influence["increase_potential"]
        if influence.get("balance_weights"):
            self.state["alignment"] = (self.state["alignment"] + self.state["entropy"]) / 2
        if influence.get("achieve_equilibrium"):
            self.state["alignment"] = 0
        if influence.get("amplify_knowledge"):
            self.state["knowledge"] *= influence["amplify_knowledge"]
        if influence.get("adjust_position"):
            self.position += np.random.uniform(-1, 1, size=self.position.shape) * influence["adjust_position"]
        if influence.get("adjust_velocity"):
            self.velocity += np.random.uniform(-0.5, 0.5, size=self.velocity.shape) * influence["adjust_velocity"]
        if influence.get("align_entropy"):
            self.state["entropy"] += influence["align_entropy"]
            self.mass = self.state["entropy"] if self.state["entropy"] > 0 else self.mass
        if influence.get("expand_senses"):
            self.senses["range"] += influence["expand_senses"]
        if influence.get("extend_memory"):
            self.memory_size += influence["extend_memory"]

    def evolve(self, perceived):
        """Evolve internal state based on local interactions."""
        if perceived:
            knowledge_boost = sum(p[1]["knowledge"] for p in perceived) / len(perceived)
            entropy_drain = sum(p[1]["entropy"] for p in perceived) / len(perceived)
        else:
            knowledge_boost = 0
            entropy_drain = 0
        self.state["knowledge"] += knowledge_boost * 0.1
        self.state["entropy"] -= entropy_drain * 0.05
        self.update_memory()

    def learn_from_memory(self):
        """A simple learning process using the past states."""
        if self.memory:
            avg_knowledge = np.mean([m["knowledge"] for m in self.memory])
            self.state["knowledge"] = (self.state["knowledge"] + avg_knowledge) / 2

    def update_position(self, dt):
        """Update position using the current velocity and time step dt."""
        self.position += self.velocity * dt

# Universe class that manages entities, inter-relationships, and emergent dynamics.
class Universe:
    def __init__(self, entities, masters, dt=1.0):
        self.entities = entities
        self.masters = masters
        self.graph = nx.Graph()
        self.time = 0.0
        self.dt = dt  # Global time step, modulated by master influences
        self.initialize_relationships()

    def initialize_relationships(self):
        """Initialize a fully connected relationship graph with random weights."""
        n = len(self.entities)
        for i in range(n):
            for j in range(i + 1, n):
                weight = random.uniform(0.1, 1.0)
                self.graph.add_edge(self.entities[i].name, self.entities[j].name, weight=weight)

    def update_relationships(self):
        """Update the relationship graph using KDTree for efficient neighbor search."""
        positions = np.array([e.position for e in self.entities])
        tree = KDTree(positions)
        for i, entity in enumerate(self.entities):
            distances, indices = tree.query(entity.position, k=len(self.entities))
            for j in indices:
                if j == i: 
                    continue
                new_weight = 1 / (1 + distances[j])
                if self.graph.has_edge(entity.name, self.entities[j].name):
                    self.graph[entity.name][self.entities[j].name]["weight"] = new_weight

    def apply_masters(self):
        """Apply all master influences to every entity."""
        for entity in self.entities:
            for influence in self.masters.values():
                entity.apply_master_influence(influence)

    def update_entities(self):
        """Let entities sense, evolve, and learn from memory."""
        for entity in self.entities:
            perceived = entity.sense_environment(self.entities)
            entity.evolve(perceived)
            entity.learn_from_memory()

    def update_emergent_dynamics(self):
        """
        Compute emergent acceleration from interactions.
        Here, differences in 'knowledge' drive an emergent force, modulated by relationship weights.
        """
        for i, entity in enumerate(self.entities):
            net_acceleration = np.zeros_like(entity.position)
            for j, other in enumerate(self.entities):
                if entity.name == other.name:
                    continue
                distance = np.linalg.norm(entity.position - other.position)
                if distance == 0:
                    continue
                # Use the emergent_force coefficient from the Master of Quantum Relativity.
                force_coeff = self.masters.get("Master of Quantum Relativity", {}).get("emergent_force", 0.05)
                # Compute a pseudo-force based on the difference in 'knowledge'
                force = force_coeff * (other.state["knowledge"] - entity.state["knowledge"]) / distance
                direction = (other.position - entity.position) / distance
                net_acceleration += force * direction
            # Update velocity and then position.
            entity.velocity += net_acceleration * self.dt
            entity.update_position(self.dt)

    def simulate_cycle(self, cycle):
        print(f"\nCycle {cycle+1}: Global Time = {self.time:.2f}")
        self.apply_masters()
        self.update_emergent_dynamics()
        self.update_entities()
        self.update_relationships()
        # Dynamically adjust the global time step based on the Keeper of Space-Time influence.
        time_dilation = self.masters.get("Keeper of Space-Time", {}).get("time_dilation", 0)
        self.dt *= (1 + time_dilation)
        for entity in self.entities:
            print(f"{entity.name} | Pos: {entity.position} | Vel: {entity.velocity} | State: {entity.state} | Mem: {len(entity.memory)}")
        self.time += self.dt

    def run_simulation(self, cycles):
        for cycle in range(cycles):
            self.simulate_cycle(cycle)

    def visualize_relationships(self):
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(self.graph)
        weights = [d["weight"] * 2 for (_, _, d) in self.graph.edges(data=True)]
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color="lightblue",
            edge_color="gray",
            font_size=10,
            width=weights,
        )
        plt.title("Emergent Space-Time: Entity Relationship Graph")
        plt.show()

# Create entities with emergent properties.
NUM_ENTITIES = 10
SENSE_RANGE = 5
entities = [
    Entity(
        name=f"Entity-{i}",
        position=[random.uniform(0, 10), random.uniform(0, 10)],
        senses={"range": SENSE_RANGE},
        state=[random.uniform(5, 15), random.uniform(1, 10), random.choice([-1, 1])],
    )
    for i in range(NUM_ENTITIES)
]

# Initialize the Universe with the improved masters and emergent dynamics.
universe = Universe(entities, MASTERS, dt=1.0)

# Run the simulation for a number of cycles.
NUM_CYCLES = 50
universe.run_simulation(NUM_CYCLES)

# Visualize the final relationship graph.
universe.visualize_relationships()
