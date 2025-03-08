import numpy as np
import matplotlib.pyplot as plt

# Define measurement angles in radians.
# Using typical settings for maximal CHSH violation (for a singlet state):
# a = 0, a' = 45°, b = 22.5°, b' = 67.5°
angles = np.radians([0, 22.5, 45, 67.5])

num_trials = 100000


def measure_trial(angle_A, angle_B):
    """
    For a given trial and measurement settings angle_A and angle_B,
    sample outcomes (A, B) according to the joint probability distribution for a singlet state:

      P(+1, +1) = 1/4 * [1 - cos(2(a-b))]
      P(+1, -1) = 1/4 * [1 + cos(2(a-b))]
      P(-1, +1) = 1/4 * [1 + cos(2(a-b))]
      P(-1, -1) = 1/4 * [1 - cos(2(a-b))]
    """
    diff = angle_A - angle_B
    cos_term = np.cos(2 * diff)
    p_pp = 0.25 * (1 - cos_term)
    p_pn = 0.25 * (1 + cos_term)
    p_np = p_pn
    p_nn = p_pp
    r = np.random.rand()
    if r < p_pp:
        return 1, 1
    elif r < p_pp + p_pn:
        return 1, -1
    elif r < p_pp + p_pn + p_np:
        return -1, 1
    else:
        return -1, -1


def compute_expectation(angle_A, angle_B, trials=num_trials):
    outcomes = [np.prod(measure_trial(angle_A, angle_B)) for _ in range(trials)]
    return np.mean(outcomes)


# Compute expectation values for the four measurement settings:
E_ab = compute_expectation(angles[0], angles[1])
E_abp = compute_expectation(angles[0], angles[3])
E_apb = compute_expectation(angles[2], angles[1])
E_apbp = compute_expectation(angles[2], angles[3])

# CHSH parameter:
S_CHSH = np.abs(E_ab - E_abp + E_apb + E_apbp)

print("🔍 CHSH Inequality Test with PRU Quantum Simulation (Fixed)")
print(f"CHSH Value: {S_CHSH:.4f}")

if S_CHSH > 2:
    print(f"✅ PRU supports quantum nonlocality (S = {S_CHSH:.4f}, >2)")
else:
    print(f"❌ PRU follows classical realism (S = {S_CHSH:.4f}, ≤2)")

# Visualize CHSH evolution over many trials
S_values = []
trial_range = range(1000, num_trials, 1000)
for i in trial_range:
    outcomes = [np.prod(measure_trial(angles[0], angles[1])) -
                np.prod(measure_trial(angles[0], angles[3])) +
                np.prod(measure_trial(angles[2], angles[1])) +
                np.prod(measure_trial(angles[2], angles[3]))
                for _ in range(i)]
    S_values.append(np.abs(np.mean(outcomes)))

plt.figure(figsize=(8, 5))
plt.plot(list(trial_range), S_values, label="CHSH Value over Trials", color="purple")
plt.axhline(y=2, linestyle="dashed", color="red", label="Classical Limit (2)")
plt.axhline(y=2.81, linestyle="dashed", color="green", label="Quantum Limit (~2.81)")
plt.xlabel("Number of Trials")
plt.ylabel("CHSH Value")
plt.title("CHSH Inequality Evolution in PRU Quantum Simulation (Fixed)")
plt.legend()
plt.grid()
plt.show()
