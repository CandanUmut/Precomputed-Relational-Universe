
import numpy as np
import pandas as pd
from scipy.constants import astronomical_unit as AU, G, c
from scipy.integrate import solve_ivp

# Constants
softening = 1e6
T_total = 365.25 * 24 * 3600  # 1 year

# Masses
masses = np.array([
    1.989e30, 3.301e23, 4.867e24, 5.972e24, 6.417e23,
    1.898e27, 5.683e26, 8.681e25, 1.024e26
])

# Positions (AU to meters)
positions = np.array([
    [0, 0, 0], [0.39, 0, 0], [0.72, 0, 0], [1.0, 0, 0], [1.52, 0, 0],
    [5.2, 0, 0], [9.58, 0, 0], [19.22, 0, 0], [30.05, 0, 0]
]) * AU

# Velocities (NASA data, m/s)
velocities = np.array([
    [0, 0, 0], [0, 47400, 0], [0, 35020, 0], [0, 29800, 0],
    [0, 24100, 0], [0, 13100, 0], [0, 9690, 0], [0, 6800, 0], [0, 5400, 0]
])

N = len(masses)

def compute_forces_vectorized(positions, velocities, masses):
    sun_pos = positions[0]
    r_vec = positions[1:] - sun_pos
    r_mag = np.linalg.norm(r_vec, axis=1).reshape(-1, 1) + softening
    accelerations = -G * masses[0] * r_vec / r_mag**3

    # Relativistic corrections for Mercury and Venus
    for idx in [0, 1]:  # Mercury, Venus
        r_mag_scalar = np.linalg.norm(r_vec[idx])
        correction_factor = 1 + (3 * G * masses[0]) / (r_mag_scalar * c**2)
        accelerations[idx] *= correction_factor

    accelerations = np.vstack(([0, 0, 0], accelerations))
    return accelerations

def equations_of_motion(t, y):
    positions = y[:3*N].reshape(N, 3)
    velocities = y[3*N:].reshape(N, 3)
    accelerations = compute_forces_vectorized(positions, velocities, masses)
    dydt = np.concatenate([velocities.flatten(), accelerations.flatten()])
    return dydt

# Initial state
initial_state = np.concatenate([positions.flatten(), velocities.flatten()])

# Solve
solution = solve_ivp(
    equations_of_motion,
    [0, T_total],
    initial_state,
    t_eval=[T_total],
    rtol=1e-9,
    atol=1e-9,
    method='RK45'
)

final_positions = solution.y[:3*N, -1].reshape(N, 3)
final_distances = np.linalg.norm(final_positions[1:], axis=1)

# NASA distances (AU)
planet_names = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
nasa_distances_1y = np.array([0.39, 0.72, 1.0, 1.52, 5.2, 9.58, 19.22, 30.05]) * AU

# Comparison DataFrame
comparison_df = pd.DataFrame({
    'PRU Predicted Distance (AU)': final_distances / AU,
    'NASA Ideal (AU)': nasa_distances_1y / AU,
    '% Difference': 100 * (final_distances - nasa_distances_1y) / nasa_distances_1y
}, index=planet_names)

import ace_tools_open as tools; tools.display_dataframe_to_user(name="PRU vs NASA Planet Distances Final", dataframe=comparison_df)
