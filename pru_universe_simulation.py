from numba import njit, prange
import numpy as np
from scipy.spatial import KDTree
import gc
import matplotlib.pyplot as plt

# Fundamental Constants
c = 3e8  # Speed of light (m/s)
G = 6.67430e-11  # Gravitational constant (m^3/kg/s^2)
h_bar = 1.0545718e-34  # Reduced Planck’s constant (J·s)
proton_mass = 1.6726219e-27  # kg
electron_mass = 9.10938356e-31  # kg
epsilon = 1e-12  # Small value to prevent division by zero errors

# Simulation Parameters
num_particles = 10000  # Scale-up option
batch_size = 100
time_steps = 100
dt = 1e-12  # Time step
neighbors = 10  # KDTree neighborhood search

# Particle Initialization
positions = np.random.rand(num_particles, 3).astype(np.float32) * 1e-9  # Initial positions (nm scale)
velocities = ((np.random.rand(num_particles, 3) - 0.5) * c * 0.8).astype(np.float32)  # Random velocities
masses = np.abs(np.random.randn(num_particles) * 1e-27).astype(np.float32)  # Particle masses
spins = np.random.choice([-1, 1], size=num_particles)  # Random spin states
black_hole_flags = np.zeros(num_particles, dtype=np.int32)  # Black hole tracking

# Initialize neighbor index storage
neighbor_indices = np.full((num_particles, neighbors), -1, dtype=np.int32)

# Function to update the KDTree and get neighbor indices
def update_neighbor_indices():
    kdtree = KDTree(positions)  # Build KDTree for fast nearest-neighbor search
    for i in range(num_particles):
        neighbors_found = kdtree.query(positions[i], k=neighbors)[1]
        neighbor_indices[i, : len(neighbors_found)] = neighbors_found

# Precompute initial neighbor indices
update_neighbor_indices()

@njit(parallel=True)
def update_pru_quantum_relativity(positions, velocities, masses, spins, dt, num_particles, neighbor_indices):
    """PRU model update with quantum entanglement, spin correlation, and relativistic effects."""
    entanglement_correlations = np.zeros(num_particles)
    time_dilation_factors = np.zeros(num_particles)

    for i in prange(num_particles):
        if black_hole_flags[i]:  # Black hole formation stops movement
            continue

        spin_correlation = 0.0
        for j in range(neighbors):
            neighbor = neighbor_indices[i, j]
            if neighbor == -1 or neighbor == i:
                continue

            # Quantum entanglement spin correlation
            angle_diff = np.linalg.norm(positions[i] - positions[neighbor]) / 1e-9
            correlation = np.cos(angle_diff / 2) ** 2
            spin_correlation += spins[i] * spins[neighbor] * correlation

        entanglement_correlations[i] = spin_correlation / max(1, neighbors)

        # Relativistic time dilation factor
        velocity_squared = np.sum(velocities[i] ** 2)
        gamma = 1 / np.sqrt(1 - velocity_squared / c ** 2)
        time_dilation_factors[i] = gamma

        # Update velocity and position
        acceleration = -G * np.sum(masses[neighbor_indices[i]]) / (np.linalg.norm(positions[i]) ** 2 + epsilon)
        velocities[i] += acceleration * dt * gamma
        positions[i] += velocities[i] * dt

    return positions, velocities, entanglement_correlations, time_dilation_factors

# Results Storage
entanglement_history = []
time_dilation_history = []
total_kinetic_energy = []
total_potential_energy = []
total_energy = []

# Run PRU Simulation
for t in range(time_steps):
    # Update neighbor database each iteration
    update_neighbor_indices()

    # Compute PRU quantum-relativistic updates
    positions, velocities, entanglement_correlations, time_dilation_factors = update_pru_quantum_relativity(
        positions, velocities, masses, spins, dt, num_particles, neighbor_indices
    )

    # Compute energy conservation with epsilon correction
    kinetic_E = 0.5 * np.sum(masses * np.sum(velocities**2, axis=1))
    
    # Fix division by zero issue
    distances = np.linalg.norm(positions[:, None] - positions[neighbor_indices], axis=-1)
    distances[distances < epsilon] = epsilon  # Prevent division by zero

    potential_E = -np.sum(G * masses[:, None] * masses[neighbor_indices] / distances)
    
    total_kinetic_energy.append(kinetic_E)
    total_potential_energy.append(potential_E)
    total_energy.append(kinetic_E + potential_E)

    entanglement_history.append(np.mean(entanglement_correlations))
    time_dilation_history.append(np.mean(time_dilation_factors))

# Cleanup
gc.collect()

# Plot Energy Conservation
plt.figure(figsize=(10, 5))
plt.plot(range(time_steps), total_kinetic_energy, label="Kinetic Energy", color="red")
plt.plot(range(time_steps), total_potential_energy, label="Potential Energy", color="blue")
plt.plot(range(time_steps), total_energy, label="Total Energy", color="black", linestyle="dashed")
plt.xlabel("Time Step")
plt.ylabel("Energy (J)")
plt.title("PRU Quantum Relativity Energy Conservation")
plt.legend()
plt.show()

# Display entanglement history
plt.figure(figsize=(10, 5))
plt.plot(range(time_steps), entanglement_history, label="Quantum Entanglement Correlation", color="purple")
plt.xlabel("Time Step")
plt.ylabel("Entanglement Strength")
plt.title("Entanglement Strength Over Time")
plt.legend()
plt.show()

# Display time dilation effects
plt.figure(figsize=(10, 5))
plt.plot(range(time_steps), time_dilation_history, label="Time Dilation Factor", color="green")
plt.xlabel("Time Step")
plt.ylabel("Gamma Factor")
plt.title("Relativistic Time Dilation Over Time")
plt.legend()
plt.show()
