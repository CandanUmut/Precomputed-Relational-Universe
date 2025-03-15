import numpy as np
import matplotlib.pyplot as plt

# Known physical constants as initial seed values
c = 2.99792458e8  # Speed of light (m/s)
hbar = 6.62607015e-34  # Planck's constant (J·s)
eps0 = 8.854187817e-12  # Vacuum permittivity (F/m)
N = 1.66e79  # Estimated number of particles in the universe

# Expected values for comparison
expected_G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
expected_alpha = 1 / 137  # Fine-structure constant (dimensionless)
expected_Lambda = 1.1e-52  # Cosmological constant (m^-2)
expected_e = 1.602176634e-19  # Elementary charge (C)

# Initial seed values for the fundamental constants
G_init = expected_G
alpha_init = expected_alpha
Lambda_init = expected_Lambda
e_init = expected_e

# Number of iterations
iterations = 100000
damping_factor = 0.0000001  # To stabilize iterations

# Arrays to store values over iterations
G_vals = [G_init]
alpha_vals = [alpha_init]
Lambda_vals = [Lambda_init]
e_vals = [e_init]

# Recursive iteration process
for _ in range(iterations):
    G_new = (c * hbar) / ((Lambda_vals[-1]) * (alpha_vals[-1]) * np.sqrt(N))
    alpha_new = (c * hbar) / ((G_vals[-1]) * (Lambda_vals[-1]) * np.sqrt(N))
    Lambda_new = (c * hbar) / ((G_vals[-1]) * np.sqrt(N) * (alpha_vals[-1]))
    e_new = np.sqrt((4 * np.pi * c ** 2 * hbar ** 2 * eps0) / ((G_vals[-1]) * (Lambda_vals[-1]) * np.sqrt(N)))

    # Apply adaptive damping factor to allow controlled convergence
    G_next = G_vals[-1] + damping_factor * (G_new - G_vals[-1])
    alpha_next = alpha_vals[-1] + damping_factor * (alpha_new - alpha_vals[-1])
    Lambda_next = Lambda_vals[-1] + damping_factor * (Lambda_new - Lambda_vals[-1])
    e_next = e_vals[-1] + damping_factor * (e_new - e_vals[-1])

    # Append new values
    G_vals.append(G_next)
    alpha_vals.append(alpha_next)
    Lambda_vals.append(Lambda_next)
    e_vals.append(e_next)

# Print final results
print(f"AFTER THIS MANY ITERATIONS :{iterations}")
print(f"Final G: {G_vals[-1]} (Expected: {expected_G})")
print(f"Final α: {alpha_vals[-1]} (Expected: {expected_alpha})")
print(f"Final Λ: {Lambda_vals[-1]} (Expected: {expected_Lambda})")
print(f"Final e: {e_vals[-1]} (Expected: {expected_e})")

# Plot results to visualize convergence
plt.figure(figsize=(12, 6))
plt.subplot(2, 2, 1)
plt.plot(G_vals, label='G (Gravitational Constant)')
plt.axhline(expected_G, color='r', linestyle='--', label='Expected G')
plt.xlabel('Iteration')
plt.ylabel('Value')
plt.legend()

plt.subplot(2, 2, 2)
plt.plot(alpha_vals, label='α (Fine-Structure Constant)')
plt.axhline(expected_alpha, color='r', linestyle='--', label='Expected α')
plt.xlabel('Iteration')
plt.ylabel('Value')
plt.legend()

plt.subplot(2, 2, 3)
plt.plot(Lambda_vals, label='Λ (Cosmological Constant)')
plt.axhline(expected_Lambda, color='r', linestyle='--', label='Expected Λ')
plt.xlabel('Iteration')
plt.ylabel('Value')
plt.legend()

plt.subplot(2, 2, 4)
plt.plot(e_vals, label='e (Elementary Charge)')
plt.axhline(expected_e, color='r', linestyle='--', label='Expected e')
plt.xlabel('Iteration')
plt.ylabel('Value')
plt.legend()

plt.suptitle('Evolution of Fundamental Constants Over Recursive Iterations')
plt.tight_layout()
plt.show()
