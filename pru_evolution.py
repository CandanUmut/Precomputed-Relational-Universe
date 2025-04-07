import numpy as np
import pandas as pd
from numba import njit, prange
import matplotlib.pyplot as plt

# =====================================================
# 🌌 PRU Network-Based Relational Simulation (Optimized)
# =====================================================

NUM_NODES = 2000
DIM = 3
TIME_STEPS = 100
RELATION_RADIUS = 75.0
CREATION_THRESHOLD = 1.2
CONFLICT_THRESHOLD = 0.4

positions = np.random.uniform(-500, 500, (NUM_NODES, DIM))
resonance = np.random.uniform(0.5, 1.0, NUM_NODES)
polarity = np.random.choice([-1, 1], NUM_NODES)
truth = np.random.uniform(0.3, 0.9, NUM_NODES)
alignment = np.random.uniform(-1, 1, NUM_NODES)

@njit(parallel=True)
def build_relation_map(pos, radius):
    N = pos.shape[0]
    relation_map = np.zeros((N, N), dtype=np.bool_)
    for i in prange(N):
        for j in range(i + 1, N):
            dist = np.linalg.norm(pos[i] - pos[j])
            if dist < radius:
                relation_map[i, j] = True
                relation_map[j, i] = True
    return relation_map

@njit(parallel=True)
def compute_field_influence(resonance, polarity, truth, alignment, relation_map):
    N = len(resonance)
    new_resonance = resonance.copy()
    new_truth = truth.copy()

    for i in prange(N):
        sum_res, sum_truth, count = 0.0, 0.0, 0
        for j in range(N):
            if relation_map[i, j]:
                influence = 1.0 + polarity[i] * polarity[j] * alignment[j]
                sum_res += resonance[j] * influence
                sum_truth += truth[j] * influence
                count += 1
        if count > 0:
            new_resonance[i] += 0.05 * (sum_res / count - resonance[i])
            new_truth[i] += 0.05 * (sum_truth / count - truth[i])

    return new_resonance, new_truth

# Track evolution
history = {
    "mean_resonance": [],
    "mean_truth": [],
    "light_ratio": [],
    "node_count": []
}

relation_map = build_relation_map(positions, RELATION_RADIUS)

for t in range(TIME_STEPS):
    resonance, truth = compute_field_influence(resonance, polarity, truth, alignment, relation_map)

    # Evaluate harmony/conflict AFTER updates
    harmony_index = resonance * truth
    create_mask = harmony_index > CREATION_THRESHOLD
    conflict_mask = harmony_index < CONFLICT_THRESHOLD

    # New nodes (before conflict removal)
    if np.any(create_mask):
        num_new = np.sum(create_mask)
        new_pos = positions[create_mask] + np.random.normal(0, 5, (num_new, DIM))
        new_res = resonance[create_mask] * 0.95
        new_pol = polarity[create_mask] * -1
        new_truth = truth[create_mask] * 0.98
        new_align = alignment[create_mask]

        positions = np.vstack((positions, new_pos))
        resonance = np.hstack((resonance, new_res))
        polarity = np.hstack((polarity, new_pol))
        truth = np.hstack((truth, new_truth))
        alignment = np.hstack((alignment, new_align))

    # Update conflict_mask after new nodes are added
    harmony_index = resonance * truth
    conflict_mask = harmony_index < CONFLICT_THRESHOLD

    if np.any(conflict_mask):
        keep = ~conflict_mask
        positions = positions[keep]
        resonance = resonance[keep]
        polarity = polarity[keep]
        truth = truth[keep]
        alignment = alignment[keep]

    if t % 10 == 0:
        relation_map = build_relation_map(positions, RELATION_RADIUS)

    history["mean_resonance"].append(np.mean(resonance))
    history["mean_truth"].append(np.mean(truth))
    history["light_ratio"].append(np.mean(polarity < 0))
    history["node_count"].append(len(resonance))

# Visualization
df = pd.DataFrame(history)
df["Time"] = np.arange(TIME_STEPS)

df.plot(x="Time", y=["mean_resonance", "mean_truth", "light_ratio", "node_count"], figsize=(12, 6), title="PRU Evolution - Network Based Consciousness")
plt.ylabel("Value / Ratio")
plt.grid(True)
plt.tight_layout()
plt.show()
