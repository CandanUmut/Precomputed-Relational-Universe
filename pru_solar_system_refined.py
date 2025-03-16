import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ===============================
# PRU-Based Solar System Simulation (O(N) Scaling)
# ===============================

# Fundamental Constants (PRU-based)
c = 3e8  # Speed of light (m/s)
h = 6.62607015e-34  # Planck's constant (J·s)
Lambda = 1.0e-52  # Cosmological constant (m^-2)
alpha = 1/137.0  # Fine-structure constant (dimensionless)
N_universe = 1.66e79  # Estimated number of particles in the universe

# PRU Gravitational Constant
G_pru = (h * c) / (Lambda * alpha * np.sqrt(N_universe))

# Solar System Data (AU and Days)
planet_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
semi_major_axes = np.array([0.39, 0.72, 1.0, 1.52, 5.2, 9.58, 19.22, 30.05]) * 1.496e11  # AU to meters
orbital_periods = np.array([88, 225, 365, 687, 4333, 10759, 30687, 60190]) * 86400  # Days to seconds

# Sun's Mass (kg)
M_sun = 1.989e30

# Compute PRU Masses of Planets
M_planets_pru = []
for i in range(len(planet_names)):
    g_surface = (6.67430e-11 * M_sun) / (semi_major_axes[i]**2)  # Approximate surface gravity
    radius_planet = semi_major_axes[i] / 50  # Rough estimate for planetary radius
    M_planets_pru.append((g_surface * radius_planet**2) / G_pru)

M_planets_pru = np.array(M_planets_pru)

# Compute Initial Velocities (Orbital Velocity from PRU Gravity)
V_planets = np.sqrt(G_pru * M_sun / semi_major_axes)

# Initialize Positions and Velocities
positions = np.zeros((len(planet_names), 2))
velocities = np.zeros((len(planet_names), 2))

# Assign initial conditions
for i in range(len(planet_names)):
    positions[i, 0] = semi_major_axes[i]  # Start at perihelion (x-axis)
    velocities[i, 1] = V_planets[i]  # Circular orbit velocity (y-axis)

# Simulation Parameters
time_steps = 1000
dt = 1.0e6  # Time step in seconds

# Store Planet Trajectories
trajectories = np.zeros((len(planet_names), time_steps, 2))

# PRU-Based Orbit Simulation (O(N) Scaling)
for t in range(time_steps):
    for i in range(len(planet_names)):
        r = np.sqrt(positions[i, 0]**2 + positions[i, 1]**2)
        F = (G_pru * M_sun * M_planets_pru[i]) / r**2
        acc = F / M_planets_pru[i]
        acc_vector = -acc * positions[i] / r
        velocities[i] += acc_vector * dt
        positions[i] += velocities[i] * dt
        trajectories[i, t, :] = positions[i]

# ===============================
# Visualization of PRU Solar System
# ===============================

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-35 * 1.496e11, 35 * 1.496e11)
ax.set_ylim(-35 * 1.496e11, 35 * 1.496e11)
ax.set_xlabel("X Position (m)")
ax.set_ylabel("Y Position (m)")
ax.set_title("PRU-Based Solar System Simulation")

# Plot Sun
ax.scatter(0, 0, color="yellow", label="Sun", s=200)

# Plot Planetary Orbits
planet_plots = [ax.plot([], [], label=planet)[0] for planet in planet_names]
planet_dots = [ax.scatter([], [], s=50) for _ in planet_names]

def update(frame):
    for i, plot in enumerate(planet_plots):
        plot.set_data(trajectories[i, :frame, 0], trajectories[i, :frame, 1])
        planet_dots[i].set_offsets([trajectories[i, frame, 0], trajectories[i, frame, 1]])
    return planet_plots + planet_dots

# Animate
ani = FuncAnimation(fig, update, frames=time_steps, interval=30, blit=True)
plt.legend()
plt.show()
