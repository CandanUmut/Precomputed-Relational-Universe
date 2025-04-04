import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import chirp
import IPython.display as ipd

# Create a relational graph with molecular structures (clusters)
def create_relational_graph(num_clusters=3, cluster_size=10, p_intra=0.7, p_inter=0.05):
    G = nx.Graph()
    pos = {}
    node_id = 0
    clusters = []

    for i in range(num_clusters):
        cluster_nodes = []
        center_x, center_y = np.random.rand(2) * 10
        for j in range(cluster_size):
            G.add_node(node_id)
            pos[node_id] = (center_x + np.random.randn() * 0.5, center_y + np.random.randn() * 0.5)
            cluster_nodes.append(node_id)
            node_id += 1
        clusters.append(cluster_nodes)

        for n1 in cluster_nodes:
            for n2 in cluster_nodes:
                if n1 != n2 and np.random.rand() < p_intra:
                    G.add_edge(n1, n2)

    for i in range(num_clusters):
        for j in range(i + 1, num_clusters):
            for n1 in clusters[i]:
                for n2 in clusters[j]:
                    if np.random.rand() < p_inter:
                        G.add_edge(n1, n2)

    return G, pos, clusters

# Apply relational updates to the graph (simulate vibration)
def apply_relational_updates(G, initial_node, steps=50):
    vibrations = {node: 0 for node in G.nodes}
    vibrations[initial_node] = 1.0
    history = [vibrations.copy()]

    for _ in range(steps):
        new_vibrations = {node: 0.0 for node in G.nodes}
        for node in G.nodes:
            for neighbor in G.neighbors(node):
                new_vibrations[neighbor] += vibrations[node] * 0.2
        vibrations = new_vibrations
        history.append(vibrations.copy())
    
    return history

# Generate sound from vibration data
def generate_sound(vibration_history, duration=2.0, sample_rate=44100):
    total_steps = len(vibration_history)
    t = np.linspace(0, duration, int(sample_rate * duration))
    signal = np.zeros_like(t)
    for step, vibrations in enumerate(vibration_history):
        freq = 440 + 100 * np.mean(list(vibrations.values()))
        signal += np.sin(2 * np.pi * freq * t) * (1 / total_steps)
    return signal

# Create the graph and run the simulation
G, pos, clusters = create_relational_graph()
initial_node = list(G.nodes)[0]
vibration_history = apply_relational_updates(G, initial_node)

# Generate sound from the vibrations
sound_wave = generate_sound(vibration_history)
ipd.display(ipd.Audio(sound_wave, rate=44100))
