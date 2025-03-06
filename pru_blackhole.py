# Optimizing the PRU quantum-gravity simulation by vectorizing calculations

import numpy as np
import gc
import matplotlib.pyplot as plt

# Fundamental Constants
c = 3e8  # Speed of light (m/s)
G = 6.67430e-11  # Gravitational constant (m^3/kg/s^2)
schwarzschild_limit = 2 * G / (c**2)  # Black hole collapse threshold

# Simulation Parameters
num_particles = 1000  # Adjusted for computational feasibility
time_steps = 100
dt = 1e-12  # Time step

# Particle Initialization
positions = np.random.rand(num_particles, 3) * 1e-9  # Initial positions (nm scale)
velocities = (np.random.rand(num_particles, 3) - 0.5) * c * 0.8  # Random velocities
masses = np.abs(np.random.randn(num_particles) * 1e-27)  # Approximate particle masses
spins = np.random.choice([-1, 1], size=num_particles)  # Random spin states
black_hole_flags = np.zeros(num_particles, dtype=np.int32)  # Black hole tracking

# Energy Conservation Variables
total_kinetic_energy = []
total_potential_energy = []
total_energy = []
black_hole_events = []

def compute_forces_and_black_holes(positions, velocities, masses):
    """Compute forces using vectorized calculations and check for black hole formation."""

    # Compute pairwise distances using broadcasting
    pos_diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    distances = np.linalg.norm(pos_diff, axis=-1) + 1e-12  # Avoid division by zero

    # Compute gravitational force magnitudes
    force_magnitude = G * masses[:, np.newaxis] * masses[np.newaxis, :] / distances**2
    np.fill_diagonal(force_magnitude, 0)  # Remove self-interaction

    # Compute net force vector for each particle
    force_vectors = force_magnitude[:, :, np.newaxis] * pos_diff / distances[:, :, np.newaxis]
    net_forces = np.sum(force_vectors, axis=1)

    # Compute kinetic and potential energy
    kinetic_energy = 0.5 * masses * np.sum(velocities**2, axis=1)
    potential_energy = -0.5 * np.sum(force_magnitude * distances, axis=1)

    # Check for black hole formation using Schwarzschild radius
    schwarzschild_radii = schwarzschild_limit * masses
    collapse_conditions = distances < schwarzschild_radii[:, np.newaxis]
    black_hole_flags[np.any(collapse_conditions, axis=1)] = 1

    # Record black hole formation events
    for i, collapse in enumerate(np.any(collapse_conditions, axis=1)):
        if collapse:
            black_hole_events.append((i, schwarzschild_radii[i]))

    return net_forces, np.sum(kinetic_energy), np.sum(potential_energy)

# Tracking results
for t in range(time_steps):
    # Compute forces and black hole formation check
    forces, kinetic_E, potential_E = compute_forces_and_black_holes(positions, velocities, masses)
    
    # Update velocities and positions using vectorized updates
    velocities += (forces / masses[:, np.newaxis]) * dt
    positions += velocities * dt

    # Store energy values for plotting
    total_kinetic_energy.append(kinetic_E)
    total_potential_energy.append(potential_E)
    total_energy.append(kinetic_E + potential_E)

# Cleanup memory
gc.collect()

# Energy Conservation Plot
plt.figure(figsize=(10, 5))
plt.plot(range(time_steps), total_kinetic_energy, label="Kinetic Energy", color="red")
plt.plot(range(time_steps), total_potential_energy, label="Potential Energy", color="blue")
plt.plot(range(time_steps), total_energy, label="Total Energy", color="black", linestyle="dashed")
plt.xlabel("Time Step")
plt.ylabel("Energy (J)")
plt.title("Energy Conservation in PRU Quantum Relativity Simulation (Vectorized)")
plt.legend()
plt.show()

# Black Hole Formation Report
if black_hole_events:
    print("\n🔥 Black Hole Events Detected!")
    for bh in black_hole_events[:5]:  # Show only the first few for readability
        print(f" - Particle {bh[0]} collapsed into a black hole (R_s = {bh[1]:.2e} m)")

# Results are now computed in a fully vectorized form, improving efficiency dramatically! 🚀
