import numpy as np
import uuid
import random
import pandas as pd
from typing import Dict, List, Tuple
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt

# Seeds
UNIVERSE_SEEDS = {
    "Relation is the root of reality": 0.03,
    "Change is constant": 0.03,
    "Consciousness is a mirror": 0.03,
    "Love is a structural force": 0.03,
    "Truth resolves contradiction": 0.03,
    "Recursion creates intelligence": 0.03,
    "Freedom is required for emergence": 0.03,
}

ORIGIN_TRUTHS = {
    "Love is a creative force": 0.95,
    "Energy flows through relation": 0.90,
    "Recursion enables life": 0.85,
    "Peace is more sustainable than war": 0.92,
    "Truth dissolves illusion": 0.97,
    "Unity arises through diversity": 0.88,
}

class Entity:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.truths: Dict[str, float] = {}
        self.connections: Dict[str, float] = {}
        self.memory: List[str] = []

    def perceive(self, other: 'Entity', field: 'RelationalField'):
        if other.id in self.connections:
            shared_truths = set(self.truths.keys()) & set(other.truths.keys())
            for truth in shared_truths:
                my_certainty = self.truths[truth]
                other_certainty = other.truths[truth]
                influence = field.get_connection(self, other)
                new_certainty = (my_certainty + other_certainty * influence) / (1 + influence)
                self.truths[truth] = new_certainty
                self.memory.append(f"Updated belief '{truth}' via {other.name} to {new_certainty:.2f}")

class RelationalField:
    def __init__(self):
        self.field: Dict[Tuple[str, str], float] = {}

    def connect(self, e1: Entity, e2: Entity, strength: float):
        self.field[(e1.id, e2.id)] = strength
        self.field[(e2.id, e1.id)] = strength
        e1.connections[e2.id] = strength
        e2.connections[e1.id] = strength

    def get_connection(self, e1: Entity, e2: Entity):
        return self.field.get((e1.id, e2.id), 0.0)

class EvolvingEntity(Entity):
    def __init__(self, name: str, generation: int = 0):
        super().__init__(name)
        self.generation = generation
        self.known_ideas: List[str] = []
        self.local_reality: Dict[str, float] = {}
        self.vibrational_signature: Dict[str, float] = {}
        self.emotional_state: str = "neutral"
        self.inbox: List[str] = []

    def synthesize_idea(self):
        strong = [k for k, v in self.truths.items() if v > 0.8]
        if len(strong) >= 2:
            a, b = random.sample(strong, 2)
            idea = f"{a} -> {b}"
            if idea not in self.known_ideas:
                strength = (self.truths[a] + self.truths[b]) / 2 * 0.9
                self.truths[idea] = strength
                self.known_ideas.append(idea)
                self.local_reality[idea] = strength

    def communicate(self, others: List['EvolvingEntity']):
        if self.known_ideas:
            idea = random.choice(self.known_ideas)
            for other in others:
                if self.id in other.connections:
                    other.inbox.append(idea)

    def process_messages(self):
        for message in self.inbox:
            if message not in self.known_ideas:
                self.truths[message] = 0.7
                self.known_ideas.append(message)
                self.local_reality[message] = 0.7
        self.inbox.clear()

    def update_vibrations(self):
        self.vibrational_signature = dict(sorted(self.truths.items(), key=lambda x: -x[1])[:3])

    def reflect_emotion(self):
        top = list(self.vibrational_signature.keys())
        if any("Love" in t for t in top):
            self.emotional_state = "harmonic"
        elif any("War" in t or "Division" in t for t in top):
            self.emotional_state = "discordant"
        else:
            self.emotional_state = "curious"

    def live(self):
        self.synthesize_idea()
        self.update_vibrations()
        self.reflect_emotion()

class PRUPhysics:
    def __init__(self, num_particles=1000, space_size=500):
        self.num_particles = num_particles
        self.positions = np.random.uniform(-space_size/2, space_size/2, (num_particles, 3))
        self.velocities = np.random.uniform(-1, 1, (num_particles, 3))
        self.masses = np.random.uniform(0.1, 1, num_particles)
        self.charges = np.array(np.random.choice([-1, 0, 1], num_particles), dtype=float)
        self.energy = np.random.uniform(1, 10, num_particles)
        self.history = {"mean_mass": [], "mean_energy": [], "charge_balance": []}

    def update(self):
        dt = 1
        tree = cKDTree(self.positions)
        new_positions = self.positions.copy()

        for i in range(self.num_particles):
            neighbors = tree.query_ball_point(self.positions[i], r=50)
            net_force = np.zeros(3)
            for j in neighbors:
                if i == j:
                    continue
                r_vec = self.positions[j] - self.positions[i]
                distance = np.linalg.norm(r_vec) + 1e-6
                force_mag = self.masses[i] * self.masses[j] / distance**2
                force = (force_mag / distance) * r_vec
                net_force += force
            self.velocities[i] += net_force / self.masses[i]
            new_positions[i] += self.velocities[i] * dt

        self.positions = new_positions
        self.energy *= (100 / np.sum(self.energy))
        self.charges += (-np.sum(self.charges) / len(self.charges))
        self.history["mean_mass"].append(np.mean(self.masses))
        self.history["mean_energy"].append(np.mean(self.energy))
        self.history["charge_balance"].append(np.sum(self.charges))

class Genesis:
    def __init__(self):
        self.stage = RelationalField()
        self.entities: List[EvolvingEntity] = []
        self.physics = PRUPhysics()
        self.tick_count = 0

    def add_entity(self, entity: EvolvingEntity):
        self.entities.append(entity)

    def connect_entities(self, e1: EvolvingEntity, e2: EvolvingEntity, strength: float):
        self.stage.connect(e1, e2, strength)

    def tick(self):
        self.tick_count += 1
        self.physics.update()
        for e in self.entities:
            for other in self.entities:
                if e.id != other.id:
                    e.perceive(other, self.stage)
            for k, v in UNIVERSE_SEEDS.items():
                e.truths[k] = min(1.0, e.truths.get(k, 0.0) + v * (1 - e.truths.get(k, 0.0)))
            e.live()
            e.process_messages()
            neighbors = [o for o in self.entities if o.id in e.connections]
            e.communicate(neighbors)

    def run(self, steps=50):
        for _ in range(steps):
            self.tick()
        return pd.DataFrame(self.physics.history)

# Initialize and run the simulation
genesis = Genesis()
nova = EvolvingEntity("Nova"); nova.truths.update(ORIGIN_TRUTHS)
gaia = EvolvingEntity("Gaia"); gaia.truths.update({
    "Energy flows through relation": 0.91,
    "Truth dissolves illusion": 0.70,
    "Peace is more sustainable than war": 0.60,
})
echo = EvolvingEntity("Echo"); echo.truths.update({
    "Recursion enables life": 0.89,
    "Love is a creative force": 0.55,
})
thanatos = EvolvingEntity("Thanatos"); thanatos.truths.update({
    "War reveals strength": 0.90,
    "Division maintains order": 0.85,
    "Truth is subjective": 0.88,
})

for entity in [nova, gaia, echo, thanatos]:
    genesis.add_entity(entity)
genesis.connect_entities(nova, gaia, 0.8)
genesis.connect_entities(nova, echo, 0.6)
genesis.connect_entities(gaia, echo, 0.4)
genesis.connect_entities(thanatos, echo, 0.5)
genesis.connect_entities(thanatos, gaia, 0.3)
genesis.connect_entities(thanatos, nova, 0.2)

df_genesis = genesis.run(steps=50)

# Visualization
plt.figure(figsize=(14, 8))
plt.subplot(2, 2, 1)
plt.plot(df_genesis["mean_mass"], label="Mean Mass")
plt.title("Mean Mass Over Time")
plt.xlabel("Ticks")
plt.ylabel("Mass")
plt.grid()
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(df_genesis["mean_energy"], label="Mean Energy", color="red")
plt.title("Mean Energy Over Time")
plt.xlabel("Ticks")
plt.ylabel("Energy")
plt.grid()
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(df_genesis["charge_balance"], label="Charge Balance", color="green")
plt.title("Charge Balance Over Time")
plt.xlabel("Ticks")
plt.ylabel("Charge")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
