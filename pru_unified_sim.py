# Re-import necessary libraries after execution state reset
import numpy as np
import matplotlib.pyplot as plt
from numba import njit, prange
import pandas as pd
import ace_tools_open as tools

# ===============================
# PRU Large-Scale Cosmological Simulation (Numba Optimized with Debugging Prints)
# ===============================

# Simulation Parameters
NUM_PARTICLES_COSMO = 10000  # Increased particle count
TIME_STEPS = 200
DELTA_T = 0.01  # Time step

# Physical Constants
G = 6.67430e-11  # Gravitational constant (m³/kg/s²)
K_E = 8.9875517873681764e9  # Coulomb's constant (N·m²/C²)
C_LIGHT = 3e8  # Speed of light (m/s)
HEAT_TRANSFER_COEFF = 0.01  # Heat transfer rate

# Particle Types (Example: Electron, Proton, Neutron, Atom, Molecule, Star, Dark Matter)
PARTICLE_TYPES = ["Electron", "Proton", "Neutron", "Atom", "Molecule", "Star", "Dark Matter"]
CHARGES = {"Electron": -1.6e-19, "Proton": 1.6e-19, "Neutron": 0.0, "Atom": 0.0,
           "Molecule": 0.0, "Star": 0.0, "Dark Matter": 0.0}
MASSES = {"Electron": 9.11e-31, "Proton": 1.67e-27, "Neutron": 1.67e-27, "Atom": 4.0e-26,
          "Molecule": 5.0e-26, "Star": 1.989e30, "Dark Matter": 1e-25}

# Initialize Particle Types Separately (Fix for Numba)
particle_types_list = np.random.choice(PARTICLE_TYPES, NUM_PARTICLES_COSMO)

# Initialize Particles (Numba-Compatible Structured Array)
np.random.seed(42)
particles_cosmo = np.zeros(NUM_PARTICLES_COSMO, dtype=[
    ('charge', np.float64),
    ('mass', np.float64),
    ('position', np.float64, (2,)),
    ('velocity', np.float64, (2,)),
    ('temperature', np.float64),
    ('entropy', np.float64),
    ('phase', np.int32)
])

# Instead of a fixed temperature, initialize with a range (e.g., 100 K to 5000 K)
for i in range(NUM_PARTICLES_COSMO):
    p_type = particle_types_list[i]
    particles_cosmo[i] = (
        CHARGES[p_type],
        MASSES[p_type],
        np.random.rand(2) * 1e6 - 5e5,  # Spread positions over a large cosmic scale
        np.random.randn(2) * 1e4,  # Initial velocities for cosmological interactions
        np.random.uniform(100, 5000),  # Random initial temperature (K)
        0.0,  # Initial entropy
        0  # Initial phase (will update below)
    )


# ===============================
# PRU Force, Heat Transfer, and Phase Update Models (Numba-Compatible)
# ===============================

@njit(parallel=True)
def compute_forces(particles):
    """
    Computes gravitational, electromagnetic, and relativistic forces.
    Added a softening parameter to avoid singularity when particles are too close.
    Caps the relativistic gamma factor if the speed is too high.
    """
    num_p = len(particles)
    forces = np.zeros((num_p, 2))
    epsilon = 1e3  # Softening parameter

    for i in prange(num_p):
        for j in range(num_p):
            if i != j:
                # Compute the distance vector and softened distance
                r_vec = particles[j]['position'] - particles[i]['position']
                distance = np.sqrt(r_vec[0] ** 2 + r_vec[1] ** 2 + epsilon ** 2)

                # Gravitational force magnitude
                F_g = (G * particles[i]['mass'] * particles[j]['mass']) / (distance ** 2)
                # Electromagnetic force magnitude
                F_e = (K_E * particles[i]['charge'] * particles[j]['charge']) / (distance ** 2)

                # Compute velocity norm and relativistic factor gamma
                v_norm = np.sqrt(particles[i]['velocity'][0] ** 2 + particles[i]['velocity'][1] ** 2)
                v_rel = v_norm / C_LIGHT
                if v_rel >= 0.999:
                    gamma = 1.0 / np.sqrt(1 - 0.999 ** 2)
                else:
                    gamma = 1.0 / np.sqrt(1 - v_rel ** 2)

                # Total force (direction: r_vec/distance)
                force_magnitude = (F_g + F_e) * gamma
                forces[i, 0] += force_magnitude * (r_vec[0] / distance)
                forces[i, 1] += force_magnitude * (r_vec[1] / distance)
    return forces


@njit(parallel=True)
def compute_heat_transfer(particles):
    """
    Computes heat transfer and entropy changes using PRU relational updates.
    Temperature and entropy are updated relationally.
    A normalization factor is applied to slow the net update so that equilibration happens over ~100 steps.
    """
    num_p = len(particles)
    new_temps = particles['temperature'].copy()
    new_entropy = particles['entropy'].copy()
    norm_factor = 100.0  # Divide the cumulative effect by 100

    for i in prange(num_p):
        for j in range(num_p):
            if i != j:
                # Heat transfer from particle j to i (if j is hotter than i, then Q_ij > 0)
                Q_ij = HEAT_TRANSFER_COEFF * (particles[j]['temperature'] - particles[i]['temperature'])
                new_temps[i] += (Q_ij * DELTA_T) / norm_factor
                # Update entropy proportionally if temperature is positive
                if new_temps[i] > 0:
                    new_entropy[i] += ((Q_ij / new_temps[i]) * DELTA_T) / norm_factor
    return new_temps, new_entropy


@njit(parallel=True)
def update_positions(particles, forces):
    """
    Updates positions and velocities using PRU relational framework.
    Also caps the velocity so that it does not exceed 0.99 * speed of light.
    """
    for i in prange(len(particles)):
        # Update velocity based on force
        particles[i]['velocity'][0] += forces[i, 0] * DELTA_T / particles[i]['mass']
        particles[i]['velocity'][1] += forces[i, 1] * DELTA_T / particles[i]['mass']
        # Cap the velocity to avoid super-luminal speeds
        v_norm = np.sqrt(particles[i]['velocity'][0] ** 2 + particles[i]['velocity'][1] ** 2)
        if v_norm > 0.99 * C_LIGHT:
            scale = (0.99 * C_LIGHT) / v_norm
            particles[i]['velocity'][0] *= scale
            particles[i]['velocity'][1] *= scale
        # Update positions
        particles[i]['position'][0] += particles[i]['velocity'][0] * DELTA_T
        particles[i]['position'][1] += particles[i]['velocity'][1] * DELTA_T


@njit(parallel=True)
def update_phases(particles):
    """
    Updates the phase state of each particle based on its temperature.
    Arbitrary thresholds are used for demonstration:
      - 0: Solid  (temp < 500 K)
      - 1: Liquid (500 K <= temp < 2500 K)
      - 2: Gas    (temp >= 2500 K)
    """
    for i in prange(len(particles)):
        temp = particles[i]['temperature']
        if temp < 500:
            particles[i]['phase'] = 0  # Solid
        elif temp < 2500:
            particles[i]['phase'] = 1  # Liquid
        else:
            particles[i]['phase'] = 2  # Gas


# ===============================
# Execute PRU Cosmological Simulation (Numba Optimized with Debugging Prints)
# ===============================

temperature_history_cosmo = []
entropy_history_cosmo = []
phase_history_cosmo = []
velocity_history_cosmo = []
min_temperature_history = []
max_temperature_history = []

for step in range(TIME_STEPS):
    # Compute forces and heat transfer updates
    forces_cosmo = compute_forces(particles_cosmo)
    temperatures_cosmo, entropy_cosmo = compute_heat_transfer(particles_cosmo)

    # Update particles with new temperatures and entropy values
    particles_cosmo['temperature'] = temperatures_cosmo
    particles_cosmo['entropy'] = entropy_cosmo

    # Update positions and velocities
    update_positions(particles_cosmo, forces_cosmo)

    # Update the phase of each particle based on its current temperature
    update_phases(particles_cosmo)

    # Compute averages for debugging and tracking
    avg_temp = particles_cosmo['temperature'].mean()
    avg_entropy = particles_cosmo['entropy'].mean()
    avg_velocity = np.mean(np.sqrt(particles_cosmo['velocity'][:, 0] ** 2 + particles_cosmo['velocity'][:, 1] ** 2))
    avg_phase = particles_cosmo['phase'].mean()

    # Compute min and max temperatures
    min_temp = np.min(particles_cosmo['temperature'])
    max_temp = np.max(particles_cosmo['temperature'])

    temperature_history_cosmo.append(avg_temp)
    entropy_history_cosmo.append(avg_entropy)
    phase_history_cosmo.append(avg_phase)
    velocity_history_cosmo.append(avg_velocity)
    min_temperature_history.append(min_temp)
    max_temperature_history.append(max_temp)

    # Debugging print statements every 10 steps
    if step % 10 == 0:
        print(
            f"Step {step}/{TIME_STEPS} - Avg Temp: {avg_temp:.2f} K, Min Temp: {min_temp:.2f} K, Max Temp: {max_temp:.2f} K, "
            f"Avg Entropy: {avg_entropy:.6f} J/K, Avg Velocity: {avg_velocity:.2f} m/s, Avg Phase: {avg_phase:.2f}")

# ===============================
# Analyze and Visualize the Results for Cosmological Scale
# ===============================

# Create DataFrame for detailed analysis
simulation_results_cosmo_df = pd.DataFrame({
    "Time Step": range(TIME_STEPS),
    "Average Temperature (K)": temperature_history_cosmo,
    "Min Temperature (K)": min_temperature_history,
    "Max Temperature (K)": max_temperature_history,
    "Average Entropy (J/K)": entropy_history_cosmo,
    "Average Phase State": phase_history_cosmo,
    "Average Velocity (m/s)": velocity_history_cosmo
})

# Display simulation results
tools.display_dataframe_to_user(name="PRU Cosmological Model Results (Debugging Info)",
                                dataframe=simulation_results_cosmo_df)

# Plot Temperature Evolution
plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), temperature_history_cosmo, label="Average Temperature", color="red")
plt.plot(range(TIME_STEPS), min_temperature_history, label="Min Temperature", color="blue", linestyle="--")
plt.plot(range(TIME_STEPS), max_temperature_history, label="Max Temperature", color="green", linestyle="--")
plt.xlabel("Time Steps")
plt.ylabel("Temperature (K)")
plt.title("PRU Cosmological Model: Temperature Evolution")
plt.legend()
plt.show()

# Plot Entropy Evolution
plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), entropy_history_cosmo, label="Average Entropy", color="orange")
plt.xlabel("Time Steps")
plt.ylabel("Entropy (J/K)")
plt.title("PRU Cosmological Model: Entropy Evolution")
plt.legend()
plt.show()

# Plot Phase Transitions
plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), phase_history_cosmo, label="Average Phase State (0=Solid, 1=Liquid, 2=Gas)", color="purple")
plt.xlabel("Time Steps")
plt.ylabel("Phase State")
plt.title("PRU Cosmological Model: Phase Transitions Over Time")
plt.legend()
plt.show()

# Plot Velocity Evolution
plt.figure(figsize=(10, 5))
plt.plot(range(TIME_STEPS), velocity_history_cosmo, label="Average Velocity", color="blue")
plt.xlabel("Time Steps")
plt.ylabel("Velocity (m/s)")
plt.title("PRU Cosmological Model: Velocity Evolution Over Time")
plt.legend()
plt.show()
