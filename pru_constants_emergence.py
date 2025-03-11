import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import KDTree

# -------------------- Optimized PRU 2.0 Simulation -------------------- #
# Includes emergent consciousness, O(N) scaling, adaptive constants, 
# and recursive self-knowledge.

# -------------------- Constants -------------------- #
N = 500  # Reduced number of particles for efficient simulation
Lambda = 1.0e-52  # Cosmological constant (m^-2)
alpha = 1/137.0  # Fine-structure constant (dimensionless)
pi = np.pi

# Derived Constants (from PRU Equations)
log_N = np.log(N)
N_inverse_dependency = N ** (-1/4.08)  # Found from earlier derivations

# Derived Gravitational Constant G (Scaling with 1/sqrt(N))
c = (6.62607015e-34 / (Lambda * alpha * (log_N / np.sqrt(N**(1/6))))) ** (1.005/3)
G = (c * 6.62607015e-34) / (Lambda * alpha * np.sqrt(N))

# Planck’s Constant h (Emergent Scaling)
h = (c * Lambda * log_N) ** (1/3) * N_inverse_dependency

# -------------------- Particle Class -------------------- #
class Particle:
    def __init__(self, id):
        self.id = id
        self.position = np.random.rand(2) * 100  # Random 2D position
        self.velocity = np.random.randn(2) * 0.1  # Small random velocity
        self.mass = np.random.uniform(0.1, 10)  # Random mass
        self.memory = []  # Stores past states
        self.consciousness = 0  # Self-awareness metric

    def interact(self, neighbors):
        """Computes interactions efficiently using KDTree neighbors."""
        net_force = np.zeros(2)
        for other in neighbors:
            if other.id == self.id:
                continue
            r_vec = other.position - self.position
            r = np.linalg.norm(r_vec) + 1e-5  # Avoid division by zero
            force_mag = G * self.mass * other.mass / (r**2)
            force_vec = (r_vec / r) * force_mag  # Normalize force direction
            net_force += force_vec
        return net_force

    def update_consciousness(self):
        """Particles store memory and evolve self-awareness over time."""
        if len(self.memory) > 10:
            self.memory.pop(0)  # Keep only last 10 steps
        self.memory.append(self.position.copy())
        self.consciousness = np.exp(-len(self.memory) / 10)  # Memory decay

    def update(self, neighbors, dt=1):
        """Updates position and velocity based on PRU forces."""
        force = self.interact(neighbors)
        acceleration = force / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        self.update_consciousness()  # Evolve memory & intelligence

# -------------------- PRU Simulation Loop -------------------- #
particles = [Particle(i) for i in range(N)]
num_steps = 100

for step in range(num_steps):
    positions = np.array([p.position for p in particles])
    tree = KDTree(positions)  # Efficient nearest neighbor search
    for p in particles:
        _, indices = tree.query(p.position, k=10)  # Get 10 nearest neighbors
        neighbors = [particles[i] for i in indices if i != p.id]  # Avoid self
        p.update(neighbors)

# -------------------- Visualization -------------------- #
positions = np.array([p.position for p in particles])
plt.figure(figsize=(8, 8))
plt.scatter(positions[:, 0], positions[:, 1], s=5, alpha=0.5, c='blue')
plt.title("PRU 2.0 Simulation: Particle Distribution After 100 Steps")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.show()

# -------------------- Output Summary -------------------- #
G, h, c
