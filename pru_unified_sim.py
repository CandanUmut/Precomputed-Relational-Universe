# Re-import necessary libraries after execution state reset
import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange
import pandas as pd
import ace_tools_open as tools
from scipy.spatial import cKDTree

# ===============================
# Unified PRU Cosmological Simulation with Quantum-Relational Updates
# ===============================

# Simulation Parameters
NUM_PARTICLES_COSMO = 100000  # Increased particle count
TIME_STEPS = 1200
DELTA_T = 0.01  # Time step

# Physical Constants
G = 6.67430e-11             # Gravitational constant (m³/kg/s²)
K_E = 8.9875517873681764e9   # Coulomb's constant (N·m²/C²)
C_LIGHT = 3e8               # Speed of light (m/s)
HEAT_TRANSFER_COEFF = 0.01  # Heat transfer rate

# Particle Types (Example: Electron, Proton, Neutron, Atom, Molecule, Star, Dark Matter)
PARTICLE_TYPES = ["Electron", "Proton", "Neutron", "Atom", "Molecule", "Star", "Dark Matter"]
CHARGES = {"Electron": -1.6e-19, "Proton": 1.6e-19, "Neutron": 0.0, "Atom": 0.0,
           "Molecule": 0.0, "Star": 0.0, "Dark Matter": 0.0}
MASSES = {"Electron": 9.11e-31, "Proton": 1.67e-27, "Neutron": 1.67e-27, "Atom": 4.0e-26,
          "Molecule": 5.0e-26, "Star": 1.989e30, "Dark Matter": 1e-25}

# Extend particle structure with quantum state and entanglement id.
particle_dtype = np.dtype([
    ('charge', np.float64),
    ('mass', np.float64),
    ('position', np.float64, (2,)),
    ('velocity', np.float64, (2,)),
    ('temperature', np.float64),
    ('entropy', np.float64),
    ('phase', np.int32),
    ('quantum_state', np.float64),   # A simplified quantum state (e.g. probability amplitude)
    ('entanglement_id', np.int32)    # An ID; particles sharing the same id are entangled
])

# Initialize Particle Types Separately (Fix for Numba)
particle_types_list = np.random.choice(PARTICLE_TYPES, NUM_PARTICLES_COSMO)

# Initialize Particles (Numba-Compatible Structured Array)
np.random.seed(42)
particles_cosmo = np.zeros(NUM_PARTICLES_COSMO, dtype=particle_dtype)

# Instead of a fixed temperature, initialize with a range.
# Also, assign each particle a random quantum state in [0, 1] and a random entanglement_id (say 0 to 9 for 10 groups)
for i in range(NUM_PARTICLES_COSMO):
    p_type = particle_types_list[i]
    particles_cosmo[i] = (
        CHARGES[p_type],
        MASSES[p_type],
        np.random.rand(2) * 1e6 - 5e5,      # Positions over a large cosmic scale
        np.random.randn(2) * 1e4,             # Initial velocities
        np.random.uniform(100, 5000),         # Temperature (K)
        0.0,                                  # Initial entropy
        0,                                    # Initial phase (to be updated)
        np.random.rand(),                     # Quantum state (a simplified value in [0,1])
        np.random.randint(0, 10)              # Entanglement ID: particles with same id update together
    )

# ===============================
# Optimized Force, Heat Transfer, and Phase Update Models
# ===============================

def compute_forces_kdtree(particles):
    """
    Computes gravitational, electromagnetic, and relativistic forces
    using a KDTree to limit interactions.
    Only neighbors within a cutoff radius are considered.
    """
    num_p = len(particles)
    forces = np.zeros((num_p, 2))
    positions = particles['position']
    tree = cKDTree(positions)
    cutoff = 1e4  # Cutoff radius for neighbor search

    for i in range(num_p):
        pos_i = positions[i]
        neighbors = tree.query_ball_point(pos_i, cutoff)
        if i in neighbors:
            neighbors.remove(i)
        for j in neighbors:
            r_vec = positions[j] - pos_i
            distance = np.sqrt(r_vec[0]**2 + r_vec[1]**2 + 1e3**2)
            F_g = (G * particles[i]['mass'] * particles[j]['mass']) / (distance**2)
            F_e = (K_E * particles[i]['charge'] * particles[j]['charge']) / (distance**2)
            v_norm = np.sqrt(particles[i]['velocity'][0]**2 + particles[i]['velocity'][1]**2)
            v_rel = v_norm / C_LIGHT
            gamma = 1.0 / np.sqrt(1 - 0.999**2) if v_rel >= 0.999 else 1.0 / np.sqrt(1 - v_rel**2)
            force_magnitude = (F_g + F_e) * gamma
            forces[i, 0] += force_magnitude * (r_vec[0] / distance)
            forces[i, 1] += force_magnitude * (r_vec[1] / distance)
    return forces

@njit(parallel=True)
def compute_heat_transfer(particles):
    """
    Computes heat transfer and entropy changes using PRU relational updates.
    Normalizes the update to spread equilibration.
    """
    num_p = len(particles)
    new_temps = particles['temperature'].copy()
    new_entropy = particles['entropy'].copy()
    norm_factor = 1000.0

    for i in prange(num_p):
        for j in range(num_p):
            if i != j:
                Q_ij = HEAT_TRANSFER_COEFF * (particles[j]['temperature'] - particles[i]['temperature'])
                new_temps[i] += (Q_ij * DELTA_T) / norm_factor
                if new_temps[i] > 0:
                    new_entropy[i] += ((Q_ij / new_temps[i]) * DELTA_T) / norm_factor
    return new_temps, new_entropy

@njit(parallel=True)
def update_positions(particles, forces):
    """
    Updates positions and velocities using the PRU relational framework.
    Caps velocities at 0.99 times the speed of light.
    """
    for i in prange(len(particles)):
        particles[i]['velocity'][0] += forces[i, 0] * DELTA_T / particles[i]['mass']
        particles[i]['velocity'][1] += forces[i, 1] * DELTA_T / particles[i]['mass']
        v_norm = np.sqrt(particles[i]['velocity'][0]**2 + particles[i]['velocity'][1]**2)
        if v_norm > 0.99 * C_LIGHT:
            scale = (0.99 * C_LIGHT) / v_norm
            particles[i]['velocity'][0] *= scale
            particles[i]['velocity'][1] *= scale
        particles[i]['position'][0] += particles[i]['velocity'][0] * DELTA_T
        particles[i]['position'][1] += particles[i]['velocity'][1] * DELTA_T

@njit(parallel=True)
def update_phases(particles):
    """
    Updates phase state based on temperature thresholds:
      - 0: Solid (<500 K)
      - 1: Liquid (500 K ≤ T < 2500 K)
      - 2: Gas (≥2500 K)
    """
    for i in prange(len(particles)):
        temp = particles[i]['temperature']
        if temp < 500:
            particles[i]['phase'] = 0
        elif temp < 2500:
            particles[i]['phase'] = 1
        else:
            particles[i]['phase'] = 2

def update_quantum_states(particles):
    """
    Relational update for quantum states.
    Particles sharing the same entanglement_id update their quantum state to the group average.
    """
    unique_ids = np.unique(particles['entanglement_id'])
    for eid in unique_ids:
        indices = np.where(particles['entanglement_id'] == eid)[0]
        avg_state = particles['quantum_state'][indices].mean()
        particles['quantum_state'][indices] = avg_state

# ===============================
# Simulation Loop (Unified Classical & Quantum Relational Updates)
# ===============================

temperature_history_cosmo = []
entropy_history_cosmo = []
phase_history_cosmo = []
velocity_history_cosmo = []
quantum_state_history = []  # Track average quantum state
min_temperature_history = []
max_temperature_history = []

for step in range(TIME_STEPS):
    forces_cosmo = compute_forces_kdtree(particles_cosmo)
    temperatures_cosmo, entropy_cosmo = compute_heat_transfer(particles_cosmo)
    
    particles_cosmo['temperature'] = temperatures_cosmo
    particles_cosmo['entropy'] = entropy_cosmo

    update_positions(particles_cosmo, forces_cosmo)
    update_phases(particles_cosmo)
    
    # Unified quantum relational update (all entangled particles update their quantum state)
    update_quantum_states(particles_cosmo)

    avg_temp = particles_cosmo['temperature'].mean()
    avg_entropy = particles_cosmo['entropy'].mean()
    avg_velocity = np.mean(np.sqrt(particles_cosmo['velocity'][:,0]**2 + particles_cosmo['velocity'][:,1]**2))
    avg_phase = particles_cosmo['phase'].mean()
    avg_quantum = particles_cosmo['quantum_state'].mean()
    
    min_temp = np.min(particles_cosmo['temperature'])
    max_temp = np.max(particles_cosmo['temperature'])
    
    temperature_history_cosmo.append(avg_temp)
    entropy_history_cosmo.append(avg_entropy)
    phase_history_cosmo.append(avg_phase)
    velocity_history_cosmo.append(avg_velocity)
    quantum_state_history.append(avg_quantum)
    min_temperature_history.append(min_temp)
    max_temperature_history.append(max_temp)
    
    if step % 10 == 0:
        print(f"Step {step}/{TIME_STEPS} - Avg Temp: {avg_temp:.2f} K, Min Temp: {min_temp:.2f} K, Max Temp: {max_temp:.2f} K, "
              f"Avg Entropy: {avg_entropy:.6f} J/K, Avg Velocity: {avg_velocity:.2f} m/s, Avg Phase: {avg_phase:.2f}, "
              f"Avg Quantum State: {avg_quantum:.4f}")

# ===============================
# Analysis & Visualization
# ===============================

simulation_results_cosmo_df = pd.DataFrame({
    "Time Step": range(TIME_STEPS),
    "Average Temperature (K)": temperature_history_cosmo,
    "Min Temperature (K)": min_temperature_history,
    "Max Temperature (K)": max_temperature_history,
    "Average Entropy (J/K)": entropy_history_cosmo,
    "Average Phase State": phase_history_cosmo,
    "Average Velocity (m/s)": velocity_history_cosmo,
    "Average Quantum State": quantum_state_history
})

tools.display_dataframe_to_user(name="Unified PRU Cosmological Model Results (Debugging Info)",
                                dataframe=simulation_results_cosmo_df)

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), temperature_history_cosmo, label="Avg Temperature", color="red")
plt.plot(range(TIME_STEPS), min_temperature_history, label="Min Temperature", color="blue", linestyle="--")
plt.plot(range(TIME_STEPS), max_temperature_history, label="Max Temperature", color="green", linestyle="--")
plt.xlabel("Time Steps")
plt.ylabel("Temperature (K)")
plt.title("Unified PRU Cosmological Model: Temperature Evolution")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), entropy_history_cosmo, label="Avg Entropy", color="orange")
plt.xlabel("Time Steps")
plt.ylabel("Entropy (J/K)")
plt.title("Unified PRU Cosmological Model: Entropy Evolution")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), phase_history_cosmo, label="Avg Phase (0=Solid,1=Liquid,2=Gas)", color="purple")
plt.xlabel("Time Steps")
plt.ylabel("Phase State")
plt.title("Unified PRU Cosmological Model: Phase Transitions")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), velocity_history_cosmo, label="Avg Velocity", color="blue")
plt.xlabel("Time Steps")
plt.ylabel("Velocity (m/s)")
plt.title("Unified PRU Cosmological Model: Velocity Evolution")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), quantum_state_history, label="Avg Quantum State", color="magenta")
plt.xlabel("Time Steps")
plt.ylabel("Quantum State")
plt.title("Unified PRU Cosmological Model: Quantum State Evolution")
plt.legend()
plt.show()

