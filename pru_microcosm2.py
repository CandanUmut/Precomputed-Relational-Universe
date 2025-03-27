import numpy as np
import networkx as nx
import random
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# =============================================================================
# Masters: Emergent Influences Governing the Universe
# =============================================================================
# These masters drive the simulation by influencing state, velocity,
# dimensional transitions, and time dilation—all via relational rules.
MASTERS = {
    "Master of Quantum Relativity": {
         "knowledge_force_coefficient": 0.05,  # Pseudo-force factor from knowledge differences
         "entanglement_influence": 0.2,
    },
    "Lord of Infinity": {
         "sense_expansion": 1.0,              # Expands an entity's sensing range as knowledge grows
         "phase_shift_threshold": 20,         # Threshold multiplier for phase-shifting dimensions
    },
    "Keeper of Space-Time": {
         "adjust_velocity": 0.5,              # Random velocity adjustments
         "time_dilation_factor": 0.1,           # Global time step modulation
         "speed_limit": 1.0,                  # Emergent speed limit for computing time dilation
    },
    "Master of Harmony": {
         "balance_entropy": True,             # Dissipates excess entropy for stability
         "entropy_dissipation": 0.05,
    },
}

# =============================================================================
# Entity Class: Nodes of Knowledge with Dimensional Perception
# =============================================================================
class Entity:
    def __init__(self, name, position, senses, state, dimension=3, memory_size=5):
        self.name = name
        self.position = np.array(position, dtype=float)   # Multi-dimensional position (starting in 3D)
        self.velocity = np.random.uniform(-0.1, 0.1, size=self.position.shape)
        self.senses = senses.copy()                         # e.g., {"range": 5}
        self.state = {"knowledge": state[0], "entropy": state[1], "alignment": state[2]}
        self.memory = []                                    # Record of past states for recursive learning
        self.memory_size = memory_size
        self.dimension = dimension                          # Current dimensional level (e.g., 3 = 3D)
        # Emergent mass derived from entropy (avoid zero mass)
        self.mass = self.state["entropy"] if self.state["entropy"] > 0 else 1.0
        self.local_time_factor = 1.0                        # Entity-specific time dilation factor

    def sense_environment(self, entities):
        """Sense nearby entities within the multi-dimensional range."""
        perceived = []
        for entity in entities:
            if entity.name == self.name:
                continue
            dist = np.linalg.norm(self.position - entity.position)
            if dist <= self.senses.get("range", 5):
                perceived.append((entity.name, entity.state))
        return perceived

    def update_memory(self):
        """Store current state into memory (with fixed memory size)."""
        if len(self.memory) >= self.memory_size:
            self.memory.pop(0)
        self.memory.append(self.state.copy())

    def apply_master_influences(self, masters):
        """Apply universal master influences to update state and properties."""
        # Lord of Infinity: expand sensing range proportional to knowledge.
        if "Lord of Infinity" in masters:
            expansion = masters["Lord of Infinity"].get("sense_expansion", 0)
            self.senses["range"] += expansion * (self.state["knowledge"] / 100.0)
        
        # Master of Harmony: dissipate some entropy for stability.
        if "Master of Harmony" in masters:
            if masters["Master of Harmony"].get("balance_entropy", False):
                dissipation = masters["Master of Harmony"].get("entropy_dissipation", 0)
                self.state["entropy"] = max(self.state["entropy"] - dissipation, 0)
                self.mass = self.state["entropy"] if self.state["entropy"] > 0 else self.mass
        
        # Keeper of Space-Time: apply slight random adjustments to velocity.
        if "Keeper of Space-Time" in masters:
            adjust = masters["Keeper of Space-Time"].get("adjust_velocity", 0)
            self.velocity += np.random.uniform(-0.05, 0.05, size=self.velocity.shape) * adjust
        
        self.update_memory()

    def evolve(self, perceived):
        """Update state based on knowledge propagation from nearby entities."""
        if perceived:
            knowledge_boost = np.mean([p[1]["knowledge"] for p in perceived])
            entropy_change = np.mean([p[1]["entropy"] for p in perceived])
        else:
            knowledge_boost = 0
            entropy_change = 0

        self.state["knowledge"] += knowledge_boost * 0.1  # Propagate knowledge
        self.state["entropy"] += (entropy_change * 0.05)   # Absorb some entropy from neighbors
        self.state["alignment"] = (self.state["alignment"] + self.state["knowledge"] - self.state["entropy"]) / 2
        self.update_memory()

    def check_dimension_transition(self, masters):
        """Ascend to a higher dimension if knowledge exceeds a threshold."""
        threshold = masters.get("Lord of Infinity", {}).get("phase_shift_threshold", 20)
        if self.state["knowledge"] > threshold * self.dimension:
            self.dimension += 1
            # Enhance sensing range and reduce entropy slightly upon transition.
            self.senses["range"] *= 1.5
            self.state["entropy"] *= 0.9
            print(f"{self.name} has ascended to dimension {self.dimension}!")

    def update_time_dilation(self, masters):
        """Compute local time dilation factor based on velocity and entropy."""
        speed_limit = masters.get("Keeper of Space-Time", {}).get("speed_limit", 1.0)
        v_norm = np.linalg.norm(self.velocity)
        # Compute gamma factor for time dilation (avoid division by zero)
        if v_norm >= speed_limit:
            gamma = 1e-3
        else:
            gamma = np.sqrt(max(0, 1 - (v_norm / speed_limit)**2))
        # Modulate by entropy (higher entropy implies slower local time)
        self.local_time_factor = gamma * (1 - 0.01 * self.state["entropy"])
    
    def update_position(self, dt):
        """Update position using velocity scaled by local time dilation."""
        self.position += self.velocity * dt * self.local_time_factor

# =============================================================================
# Universe Class: The Cosmic Simulation Engine
# =============================================================================
class Universe:
    def __init__(self, entities, masters, dt=0.1):
        self.entities = entities
        self.masters = masters
        self.dt = dt           # Global time step
        self.time = 0.0
        self.graph = nx.Graph()
        self.initialize_relationships()

    def initialize_relationships(self):
        """Precompute the relational graph (fully connected with random weights)."""
        n = len(self.entities)
        for i in range(n):
            for j in range(i+1, n):
                weight = random.uniform(0.1, 1.0)
                self.graph.add_edge(self.entities[i].name, self.entities[j].name, weight=weight)

    def update_relationships(self):
        """Update the relational graph using KDTree for efficient neighbor lookups."""
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
        """Apply master influences to every entity."""
        for entity in self.entities:
            entity.apply_master_influences(self.masters)

    def update_emergent_dynamics(self):
        """
        Compute pseudo-forces from knowledge differences.
        Each pair of entities interacts via a force similar to gravity:
            F = k * (ΔK) / r²
        where k is set by the Master of Quantum Relativity.
        """
        for i, entity in enumerate(self.entities):
            net_force = np.zeros_like(entity.position)
            for j, other in enumerate(self.entities):
                if entity.name == other.name:
                    continue
                r = np.linalg.norm(entity.position - other.position)
                if r == 0:
                    continue
                k_force_coeff = self.masters.get("Master of Quantum Relativity", {}).get("knowledge_force_coefficient", 0.05)
                delta_k = other.state["knowledge"] - entity.state["knowledge"]
                force_magnitude = k_force_coeff * delta_k / (r**2)
                direction = (other.position - entity.position) / r
                net_force += force_magnitude * direction
            acceleration = net_force / entity.mass
            entity.velocity += acceleration * self.dt

    def update_entities(self):
        """Update each entity: evolve state, check dimensional shifts, update time dilation, and move."""
        for entity in self.entities:
            perceived = entity.sense_environment(self.entities)
            entity.evolve(perceived)
            entity.check_dimension_transition(self.masters)
            entity.update_time_dilation(self.masters)
            entity.update_position(self.dt)

    def adjust_global_time(self):
        """
        Adjust the global time step based on average entity time dilation.
        Influenced by the Keeper of Space-Time.
        """
        avg_time_factor = np.mean([e.local_time_factor for e in self.entities])
        dilation = self.masters.get("Keeper of Space-Time", {}).get("time_dilation_factor", 0)
        self.dt *= (1 + dilation * (1 - avg_time_factor))
    
    def simulate_cycle(self, cycle):
        print(f"\nCycle {cycle+1} | Global Time: {self.time:.3f} | dt: {self.dt:.3f}")
        self.apply_masters()
        self.update_emergent_dynamics()
        self.update_entities()
        self.update_relationships()
        self.adjust_global_time()
        self.time += self.dt
        # Debug output for each entity.
        for entity in self.entities:
            print(f"{entity.name} | Pos: {np.round(entity.position,2)} | Vel: {np.round(entity.velocity,2)} "
                  f"| Dim: {entity.dimension} | Time Factor: {entity.local_time_factor:.3f} | State: {entity.state}")

    def run_simulation(self, cycles):
        for cycle in range(cycles):
            self.simulate_cycle(cycle)

    def visualize_entities(self):
        """
        Visualize a 2D projection (first two dimensions) of entity positions.
        Color indicates the current dimensional level.
        """
        plt.figure(figsize=(10, 8))
        x = [e.position[0] for e in self.entities]
        y = [e.position[1] for e in self.entities]
        dims = [e.dimension for e in self.entities]
        scatter = plt.scatter(x, y, c=dims, cmap="viridis", s=100)
        plt.colorbar(scatter, label="Dimension Level")
        plt.title("Entity Positions and Dimensional Levels")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

    def visualize_relationship_graph(self):
        """Visualize the precomputed relational graph."""
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
        plt.title("Precomputed Relational Universe Graph")
        plt.show()

# =============================================================================
# Simulation Setup and Execution
# =============================================================================
# Create entities with 3D positions, initial sensing range, and a starting state.
NUM_ENTITIES = 10
INITIAL_SENSE_RANGE = 5
entities = [
    Entity(
        name=f"Entity-{i}",
        position=np.random.uniform(0, 10, size=3),  # 3D; later can extend to higher dimensions
        senses={"range": INITIAL_SENSE_RANGE},
        state=[random.uniform(5, 15), random.uniform(1, 10), random.choice([-1, 1])]
    )
    for i in range(NUM_ENTITIES)
]

# Create the Universe with the defined masters and initial global time step.
universe = Universe(entities, MASTERS, dt=0.1)

# Run the simulation for a number of cycles.
NUM_CYCLES = 50
universe.run_simulation(NUM_CYCLES)

# Visualize the final state: entity positions and the relational graph.
universe.visualize_entities()
universe.visualize_relationship_graph()
