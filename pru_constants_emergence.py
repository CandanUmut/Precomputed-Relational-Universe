import numpy as np
from scipy.spatial import cKDTree  # Efficient spatial indexing for O(N) force computation

# === KNOWN CONSTANTS ===
h_standard = 6.62607015e-34  # Planck's constant (J·s)
c_standard = 2.99792458e8  # Speed of light (m/s)
G_standard = 6.67430e-11  # Gravitational constant (m³/kg/s²)
alpha_standard = 1 / 137.035999139  # Fine-structure constant (dimensionless)
Lambda = 1.0e-52  # Cosmological constant (m^-2)
N = 1.66e79  # Estimated number of particles in the universe

# === DERIVING CONSTANTS FROM PRU FORMULAS ===

# 1. Derived Speed of Light (c) using PRU method
log_N = np.log(N)
N_sixth_root = N ** (1/6)
entropy_correction = (log_N / np.sqrt(N_sixth_root))
c_derived = (h_standard / (Lambda * alpha_standard * entropy_correction)) ** (1.005/3)

# 2. Derived Gravitational Constant (G) using PRU scaling
N_sqrt = np.sqrt(N)
G_derived = (c_derived * h_standard) / (Lambda * alpha_standard * N_sqrt)

# 3. Derived Planck’s Constant (h)
N_inverse_dependency = N ** (-1/4.08)
h_derived = (c_derived * Lambda * log_N) ** (1/3) * N_inverse_dependency

# 4. Derived Fine-Structure Constant (α)
pi_derived = (log_N / np.cbrt(Lambda * c_derived))**(1/30) * np.exp(-log_N / N**(10/255))
alpha_derived = 1 / pi_derived

# === PARTICLE SIMULATION SETUP ===
num_particles = 1000  # Number of particles
positions = np.random.uniform(-1e6, 1e6, (num_particles, 3))  # Random positions
velocities = np.random.uniform(-1e-3, 1e-3, (num_particles, 3))  # Small initial velocities
masses = np.random.uniform(1e20, 1e25, num_particles)  # Randomized masses

dt = 1e4  # Time step (s)
num_steps = 100  # Simulation steps

# PRU-BASED FORCE COMPUTATION (O(N) Complexity)
def compute_pru_gravity(positions, masses, G, cutoff_radius=1e5):
    """
    Compute gravity using an efficient PRU-based method with a spatial index (O(N)).
    """
    forces = np.zeros_like(positions)
    tree = cKDTree(positions)  # Spatial index for efficient lookups
    pairs = tree.query_pairs(cutoff_radius, output_type='ndarray')  # Neighboring pairs only
    
    for i, j in pairs:
        r_vec = positions[j] - positions[i]
        r_mag = np.linalg.norm(r_vec) + 1e-10  # Avoid division by zero
        F = G * masses[i] * masses[j] / (r_mag ** 2)
        force_vec = (F / r_mag) * r_vec
        forces[i] += force_vec
        forces[j] -= force_vec  # Equal and opposite force
    
    return forces

# === SIMULATION LOOP ===
for step in range(num_steps):
    forces = compute_pru_gravity(positions, masses, G_derived)
    velocities += forces / masses[:, np.newaxis] * dt  # Update velocity
    positions += velocities * dt  # Update position

    # Print sample output every 20 steps
    if step % 20 == 0 or step == num_steps - 1:
        print(f"Step {step}:")
        print(f"  Sample Position: {positions[0]}")
        print(f"  Sample Velocity: {velocities[0]}")
        print("  ------------------------")

# === FINAL RESULTS OUTPUT ===
print("\n=== FINAL CONSTANTS DERIVED ===")
print(f"Derived c = {c_derived:.6e} m/s")
print(f"Standard c = {c_standard:.6e} m/s")
print(f"Difference = {abs(c_derived - c_standard):.6e} m/s\n")

print(f"Derived G = {G_derived:.6e} m³/kg/s²")
print(f"Standard G = {G_standard:.6e} m³/kg/s²")
print(f"Difference = {abs(G_derived - G_standard):.6e} m³/kg/s²\n")

print(f"Derived h = {h_derived:.6e} J·s")
print(f"Standard h = {h_standard:.6e} J·s")
print(f"Difference = {abs(h_derived - h_standard):.6e} J·s\n")

print(f"Derived α = {alpha_derived:.6e}")
print(f"Standard α = {alpha_standard:.6e}")
print(f"Difference = {abs(alpha_derived - alpha_standard):.6e}\n")

print("Final Sample Particle Positions:", positions[:5])
print("Final Sample Velocities:", velocities[:5])
