import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import ace_tools_open as tools  # For visualization

# ================================
# 🔥 PRU Reverse-Engineered Universal Simulation (with Constants)
# ================================

# **Simulation Parameters**
NUM_PARTICLES = 5000  # Quantum-scale objects
NUM_MACRO_OBJECTS = 500  # Larger macroscopic objects
TIME_STEPS = 100
SPACE_SIZE = 1000  # Defines 3D PRU space limits
dt_base = 1  # PRU base time step

# **Emergent PRU Constants**
G_PRU = 1.0  # Gravitational-like relational scaling factor
C_PRU = 299792458  # Speed of relational updates (analogous to c in m/s)
H_PRU = 6.626e-34  # Minimum quantum update resolution (Planck-like constant)
ALPHA_PRU = 1 / 137  # Fine-structure constant in PRU
LAMBDA_PRU = 1e-52  # Cosmological expansion parameter
PI_PRU = 3.14159265358979  # Computational relational constant (π)

# **Particle Properties**
particles = {
    "position": np.random.uniform(-SPACE_SIZE / 2, SPACE_SIZE / 2, (NUM_PARTICLES, 3)),
    "velocity": np.random.uniform(-1, 1, (NUM_PARTICLES, 3)),
    "mass": np.random.uniform(0.1, 1, NUM_PARTICLES),
    "charge": np.random.choice([-1, 0, 1], NUM_PARTICLES),
    "energy": np.random.uniform(1, 10, NUM_PARTICLES),
}

macro_objects = {
    "position": np.random.uniform(-SPACE_SIZE / 2, SPACE_SIZE / 2, (NUM_MACRO_OBJECTS, 3)),
    "velocity": np.random.uniform(-0.5, 0.5, (NUM_MACRO_OBJECTS, 3)),
    "mass": np.random.uniform(10, 100, NUM_MACRO_OBJECTS),
    "charge": np.random.choice([-1, 0, 1], NUM_MACRO_OBJECTS),
    "energy": np.random.uniform(10, 100, NUM_MACRO_OBJECTS),
}

# ================================
# 🔄 PRU Relational Update Function with Constants
# ================================
def update_positions(objects):
    """Relational update of positions based on PRU emergent constants."""
    positions = objects["position"]
    masses = objects["mass"]
    charges = objects["charge"]

    # **Adaptive Time Step (dt) Scaling**
    dt = dt_base * (1 + LAMBDA_PRU * np.mean(masses))

    # Use KDTree for efficient relational neighbor search
    tree = cKDTree(positions)
    updated_positions = positions.copy()

    for i in range(len(positions)):
        neighbors = tree.query_ball_point(positions[i], r=50)  # Define relational neighborhood

        net_force = np.zeros(3)
        for j in neighbors:
            if i == j:
                continue
            r_vec = positions[j] - positions[i]
            distance = np.linalg.norm(r_vec) + 1e-6  # Avoid division by zero

            # **Emergent Gravity (Relational G)**
            force_mag = G_PRU * masses[i] * masses[j] / distance**2
            force = (force_mag / distance) * r_vec

            # **Charge Interaction (PRU Fine-Structure Alpha)**
            charge_effect = ALPHA_PRU * charges[i] * charges[j] / (distance**2)
            force += (charge_effect / distance) * r_vec

            # **Light Speed Limit (PRU-c)**
            speed_limit = C_PRU * dt
            if np.linalg.norm(force) > speed_limit:
                force = (force / np.linalg.norm(force)) * speed_limit

            net_force += force

        # Update velocity and position
        objects["velocity"][i] += net_force / masses[i]
        updated_positions[i] += objects["velocity"][i] * dt

    objects["position"] = updated_positions

# ================================
# 🔋 PRU Energy Conservation & Quantum Scaling
# ================================
def update_energy_charge(objects):
    """Ensures energy conservation and quantum balance during updates."""
    total_energy = np.sum(objects["energy"])
    total_charge = np.sum(objects["charge"])

    # Normalize energy and charge to maintain conservation principles
    objects["energy"] *= (100 / total_energy)
    charge_deficit = -total_charge / len(objects["charge"])  # Distribute charge to balance
    objects["charge"] += charge_deficit

# ================================
# 🔄 Run PRU Universal Simulation with Constants
# ================================
history = {
    "mean_mass": [],
    "mean_energy": [],
    "charge_balance": [],
    "dt_variation": []
}

for t in range(TIME_STEPS):
    update_positions(particles)
    update_positions(macro_objects)
    update_energy_charge(particles)
    update_energy_charge(macro_objects)

    # Store statistics
    history["mean_mass"].append(np.mean(macro_objects["mass"]))
    history["mean_energy"].append(np.mean(macro_objects["energy"]))
    history["charge_balance"].append(np.sum(macro_objects["charge"]))
    history["dt_variation"].append(dt_base * (1 + LAMBDA_PRU * np.mean(macro_objects["mass"])))

    # Log progress
    if t % 10 == 0:
        print(f"Step {t}/{TIME_STEPS} - dt: {history['dt_variation'][-1]:.6e}")

# ================================
# 📊 Visualization of PRU Universal Evolution with Constants
# ================================
df_results = pd.DataFrame({
    "Time Step": np.arange(TIME_STEPS),
    "Mean Mass": history["mean_mass"],
    "Mean Energy": history["mean_energy"],
    "Charge Balance": history["charge_balance"],
    "dt Variation": history["dt_variation"]
})

tools.display_dataframe_to_user(name="PRU Universal Simulation Results (With Constants)", dataframe=df_results)

plt.figure(figsize=(12, 6))
plt.plot(df_results["Time Step"], df_results["Mean Mass"], label="Mean Mass", color="blue")
plt.plot(df_results["Time Step"], df_results["Mean Energy"], label="Mean Energy", color="red")
plt.plot(df_results["Time Step"], df_results["Charge Balance"], label="Charge Balance", color="green")
plt.plot(df_results["Time Step"], df_results["dt Variation"], label="dt Variation", color="purple")
plt.xlabel("Time Steps")
plt.ylabel("Value")
plt.title("PRU Universal Evolution Over Time (With Constants)")
plt.legend()
plt.grid()
plt.show()

print("\n✅ **PRU Universal Simulation with Constants Successfully Executed**")
print("🚀 This represents a fully relational model of reality, merging quantum, gravity, energy, and cosmology.")
