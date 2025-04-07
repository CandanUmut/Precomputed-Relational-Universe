import numpy as np
import pandas as pd
from numba import njit, prange
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
import ace_tools as tools

# === Simulation Parameters ===
NUM_ENTITIES = 500
SPACE_SIZE = 1000
TIME_STEPS = 100
DT = 1.0
RELATION_RADIUS = 50

# === Initialization ===
np.random.seed(42)
positions = np.random.uniform(-SPACE_SIZE/2, SPACE_SIZE/2, (NUM_ENTITIES, 3))
velocities = np.random.uniform(-1, 1, (NUM_ENTITIES, 3))
masses = np.random.uniform(1.0, 5.0, NUM_ENTITIES)
truth_values = np.random.uniform(0.5, 1.0, NUM_ENTITIES)
memory_decay = np.random.uniform(0.95, 0.99, NUM_ENTITIES)
memories = np.zeros((NUM_ENTITIES, 3))
perceptions = np.zeros((NUM_ENTITIES, 3))

# History tracking
history = {
    "step": [],
    "mean_truth": [],
    "truth_std_dev": [],
    "global_awareness": []
}

# === Numba-compatible update function ===
@njit(parallel=True)
def update_entities_flat(
    positions, velocities, masses, truth_values,
    memories, perceptions, memory_decay,
    neighbors_flat, neighbor_start_idx, neighbor_counts, dt
):
    new_positions = np.empty_like(positions)
    new_velocities = np.empty_like(velocities)
    new_truth = np.copy(truth_values)
    new_memories = np.copy(memories)
    new_perceptions = np.zeros_like(perceptions)

    for i in prange(len(positions)):
        start = neighbor_start_idx[i]
        count = neighbor_counts[i]
        influence = np.zeros(3)
        truth_influence = 0.0

        for j in range(start, start + count):
            neighbor_idx = neighbors_flat[j]
            if i == neighbor_idx:
                continue
            delta = positions[neighbor_idx] - positions[i]
            influence += delta * truth_values[neighbor_idx]
            truth_influence += truth_values[neighbor_idx]

        if count > 1:
            influence /= (count - 1)
            truth_influence /= (count - 1)

        new_velocities[i] += 0.01 * influence
        new_positions[i] = positions[i] + new_velocities[i] * dt
        new_perceptions[i] = influence
        new_memories[i] = memory_decay[i] * memories[i] + (1 - memory_decay[i]) * influence
        new_truth[i] += 0.001 * (truth_influence - new_truth[i])
        new_truth[i] = min(1.0, max(0.0, new_truth[i]))  # Clamp

    return new_positions, new_velocities, new_truth, new_memories, new_perceptions

# === Simulation loop ===
for step in range(TIME_STEPS):
    tree = cKDTree(positions)
    neighbor_lists = tree.query_ball_point(positions, r=RELATION_RADIUS)

    # Flatten neighbor lists for Numba
    neighbors_flat = np.array([j for sublist in neighbor_lists for j in sublist], dtype=np.int64)
    neighbor_start_idx = np.zeros(NUM_ENTITIES, dtype=np.int64)
    neighbor_counts = np.zeros(NUM_ENTITIES, dtype=np.int64)
    counter = 0
    for i, neighbors in enumerate(neighbor_lists):
        neighbor_start_idx[i] = counter
        neighbor_counts[i] = len(neighbors)
        counter += len(neighbors)

    positions, velocities, truth_values, memories, perceptions = update_entities_flat(
        positions, velocities, masses, truth_values, memories, perceptions,
        memory_decay, neighbors_flat, neighbor_start_idx, neighbor_counts, DT
    )

    history["step"].append(step)
    history["mean_truth"].append(np.mean(truth_values))
    history["truth_std_dev"].append(np.std(truth_values))
    history["global_awareness"].append(np.mean(np.linalg.norm(perceptions, axis=1)))

# === Display & Plot ===
df = pd.DataFrame(history)
tools.display_dataframe_to_user(name="Relational Evolution Log", dataframe=df)

plt.figure(figsize=(12, 6))
plt.plot(df["step"], df["mean_truth"], label="Mean Truth", color="gold")
plt.plot(df["step"], df["truth_std_dev"], label="Truth Std Dev", color="red")
plt.plot(df["step"], df["global_awareness"], label="Global Awareness", color="cyan")
plt.title("Relational Network Evolution (Optimized)")
plt.xlabel("Step")
plt.ylabel("Metric")
plt.legend()
plt.grid(True)
plt.show()
