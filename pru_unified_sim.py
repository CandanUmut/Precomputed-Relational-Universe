import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange

# ===============================
# Simulation Parameters
# ===============================
NUM_PARTICLES = 100
TIME_STEPS = 200
DELTA_T = 0.01  # Time step

# Physical Constants
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
K_E = 8.9875517873681764e9  # Coulomb's constant (N·m²/C²)
C_LIGHT = 3e8  # Speed of light (m/s)
HEAT_TRANSFER_COEFF = 0.01  # Heat transfer rate

# Particle Types (Example: Electron, Proton, Neutron, Atom, Molecule, Star)
PARTICLE_TYPES = ["Electron", "Proton", "Neutron", "Atom", "Molecule", "Star"]
CHARGES = {"Electron": -1.6e-19, "Proton": 1.6e-19, "Neutron": 0.0, "Atom": 0.0, "Molecule": 0.0, "Star": 0.0}
MASSES = {"Electron": 9.11e-31, "Proton": 1.67e-27, "Neutron": 1.67e-27, "Atom": 4.0e-26, "Molecule": 5.0e-26, "Star": 1.989e30}
HEAT_CAPACITIES = {"Electron": 0.1, "Proton": 0.1, "Neutron": 0.1, "Atom": 100, "Molecule": 200, "Star": 1e7}

# ===============================
# Initialize Particles
# ===============================

np.random.seed(42)

particles = np.zeros(NUM_PARTICLES, dtype=[
    ('type', np.object_),
    ('charge', np.float64),
    ('mass', np.float64),
    ('position', np.float64, (2,)),
    ('velocity', np.float64, (2,)),
    ('temperature', np.float64),
    ('entropy', np.float64),
    ('phase', np.int32)
])

for i in range(NUM_PARTICLES):
    p_type = np.random.choice(PARTICLE_TYPES)
    particles[i] = (p_type, CHARGES[p_type], MASSES[p_type], 
                    np.random.rand(2) * 10 - 5,  # Random initial positions
                    np.random.randn(2) * 500,  # Random velocity
                    300,  # Initial temperature
                    0,  # Initial entropy
                    0)  # Initial phase (solid)

# ===============================
# PRU Force & Heat Transfer Models
# ===============================

@njit(parallel=True)
def compute_forces(particles):
    """Computes gravitational, electromagnetic, and relativistic forces."""
    num_p = len(particles)
    forces = np.zeros((num_p, 2))
    
    for i in prange(num_p):
        for j in range(num_p):
            if i != j:
                r_vec = particles[j]['position'] - particles[i]['position']
                distance = np.linalg.norm(r_vec) + 1e-10  # Prevent division by zero
                
                # Gravity (Relational Update)
                F_g = (G * particles[i]['mass'] * particles[j]['mass']) / (distance ** 2)
                
                # Electromagnetic Force (Coulomb's Law)
                F_e = (K_E * particles[i]['charge'] * particles[j]['charge']) / (distance ** 2)
                
                # Relativistic Factor (Lorentz Correction)
                v_rel = np.linalg.norm(particles[i]['velocity']) / C_LIGHT
                gamma = 1 / np.sqrt(1 - v_rel ** 2)
                
                # Compute final force
                force = (F_g + F_e) * (r_vec / distance) * gamma
                forces[i] += force

    return forces

@njit(parallel=True)
def compute_heat_transfer(particles):
    """Computes heat transfer and entropy changes."""
    num_p = len(particles)
    new_temps = particles['temperature'].copy()
    new_entropy = particles['entropy'].copy()

    for i in prange(num_p):
        for j in range(num_p):
            if i != j:
                Q_ij = HEAT_TRANSFER_COEFF * (particles[j]['temperature'] - particles[i]['temperature']) / HEAT_CAPACITIES[particles[i]['type']]
                new_temps[i] += Q_ij * DELTA_T
                if new_temps[i] > 0:
                    new_entropy[i] += Q_ij / new_temps[i]

    return new_temps, new_entropy

@njit(parallel=True)
def update_positions(particles, forces):
    """Updates positions and velocities using PRU relational framework."""
    for i in prange(len(particles)):
        particles[i]['velocity'] += forces[i] * DELTA_T / particles[i]['mass']
        particles[i]['position'] += particles[i]['velocity'] * DELTA_T

# ===============================
# Run PRU Unified Simulation
# ===============================

temperature_history = []
entropy_history = []
phase_history = []

for step in range(TIME_STEPS):
    forces = compute_forces(particles)
    temperatures, entropy = compute_heat_transfer(particles)

    particles['temperature'] = temperatures
    particles['entropy'] = entropy

    update_positions(particles, forces)

    temperature_history.append(temperatures.mean())
    entropy_history.append(entropy.mean())
    phase_history.append(np.mean(particles['phase']))  # Average phase state

# ===============================
# Plot Results
# ===============================

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), temperature_history, label="Average Temperature", color="red")
plt.xlabel("Time Steps")
plt.ylabel("Temperature (K)")
plt.title("PRU Unified Model: Temperature Evolution")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), entropy_history, label="Average Entropy", color="orange")
plt.xlabel("Time Steps")
plt.ylabel("Entropy (J/K)")
plt.title("PRU Unified Model: Entropy Evolution")
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), phase_history, label="Average Phase State (0=Solid, 1=Liquid, 2=Gas)", color="purple")
plt.xlabel("Time Steps")
plt.ylabel("Phase State")
plt.title("PRU Unified Model: Phase Transitions Over Time")
plt.legend()
plt.show()
