# PRU Simulation Engine - Relational Update Based Universe

import random
import math
import time
import networkx as nx
import matplotlib.pyplot as plt

# --- Core Entity ---
class Entity:
    def __init__(self, id, position):
        self.id = id
        self.position = position  # (x, y)
        self.state = 'stable'
        self.energy = random.uniform(0.1, 1.0)
        self.relations = []  # Other entity IDs it relates to

    def distance_to(self, other):
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        return math.sqrt(dx**2 + dy**2)

# --- Universe Engine ---
class Universe:
    def __init__(self, size=100, num_entities=20):
        self.entities = {}
        for i in range(num_entities):
            pos = (random.uniform(0, size), random.uniform(0, size))
            self.entities[i] = Entity(i, pos)
        self.graph = nx.Graph()
        self.update_graph()

    def update_graph(self):
        self.graph.clear()
        for entity in self.entities.values():
            self.graph.add_node(entity.id, pos=entity.position)

        # Create relations based on distance (event-driven)
        threshold = 25.0
        for a in self.entities.values():
            for b in self.entities.values():
                if a.id != b.id:
                    dist = a.distance_to(b)
                    if dist < threshold:
                        self.graph.add_edge(a.id, b.id, weight=1.0/dist)
                        if b.id not in a.relations:
                            a.relations.append(b.id)

    def simulate_tick(self):
        updated = []
        for entity in self.entities.values():
            for related_id in entity.relations:
                related = self.entities[related_id]
                dist = entity.distance_to(related)
                delta_energy = random.uniform(-0.05, 0.05)
                if dist < 15:
                    entity.energy += delta_energy
                    related.energy -= delta_energy
                    updated.append((entity.id, related.id))
        self.update_graph()
        return updated

    def draw(self):
        plt.clf()
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', edge_color='gray')
        plt.pause(0.1)

# --- Run Simulation ---
def run_simulation():
    universe = Universe(size=100, num_entities=15)
    plt.ion()
    plt.figure(figsize=(8, 6))
    for i in range(100):
        updates = universe.simulate_tick()
        universe.draw()
        print(f"Tick {i+1}: {len(updates)} relations updated.")
        time.sleep(0.2)
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    run_simulation()
