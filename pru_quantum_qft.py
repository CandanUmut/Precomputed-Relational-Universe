import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from numba import njit
import ace_tools_open as tools  # For visualization

# ================================
# PRU-QFT Setup: Number of Qubits and Initial State
# ================================
N_QUBITS = 12  # You can adjust this for testing.
N_STATES = 2 ** N_QUBITS  # Total computational basis states.

# Initialize the quantum state in PRU-style relational encoding.
state_vector = np.zeros(N_STATES, dtype=np.complex128)
state_vector[0] = 1.0  # Start in the |0...0⟩ state.


# ================================
# Standard QFT Implementation (O(N^2))
# ================================
def standard_qft(state_vector):
    """
    Implements the QFT via direct matrix multiplication (O(N^2)).
    This is used for validation.
    """
    N = len(state_vector)
    new_state = np.zeros(N, dtype=np.complex128)
    for k in range(N):
        for j in range(N):
            new_state[k] += state_vector[j] * np.exp(2j * np.pi * j * k / N)
        new_state[k] /= np.sqrt(N)
    return new_state


# ================================
# PRU Relational Update QFT Version 1: Using FFT
# ================================
def pru_qft_fft(state_vector):
    """
    In our PRU approach, we assume every basis state already “knows” the state
    of every other basis state. In a massively parallel implementation, each
    amplitude could update in O(1), so the entire update would be O(N).

    Here we use np.fft.fft (which is O(N log N) serially) as a stand-in for a
    fully parallel relational update.
    """
    return np.fft.fft(state_vector) / np.sqrt(len(state_vector))


# ================================
# PRU Relational Update QFT Version 2: Vectorized Outer Product
# ================================
def pru_qft_relational(state_vector):
    """
    Implements the QFT via a fully vectorized update. We precompute the phase factors
    in an outer product and then perform a matrix-vector multiplication. In a PRU
    framework where each “particle” computes its amplitude in parallel, this update
    would be O(N) time.

    (Note: This method requires O(N^2) memory and is provided for conceptual clarity.)
    """
    N = len(state_vector)
    indices = np.arange(N)
    k = indices.reshape((N, 1))
    # Build the Fourier matrix (each entry is exp(2pi i j k / N)/sqrt(N))
    phases = np.exp(2j * np.pi * k * indices / N) / np.sqrt(N)
    return phases @ state_vector


# ================================
# 3. Compute QFT Outputs
# ================================
# You can choose either PRU approach:
pru_qft_result = pru_qft_fft(state_vector)
# Alternatively, for the fully vectorized relational update:
# pru_qft_result = pru_qft_relational(state_vector)

standard_qft_result = standard_qft(state_vector)

# ================================
# 4. Compare PRU-QFT vs Standard QFT
# ================================
differences = np.abs(pru_qft_result - standard_qft_result)

df_comparison = pd.DataFrame({
    "PRU-QFT Magnitudes": np.abs(pru_qft_result),
    "Standard QFT Magnitudes": np.abs(standard_qft_result),
    "Absolute Differences": differences
}).round(6)

tools.display_dataframe_to_user(name="PRU-QFT vs Standard QFT Comparison", dataframe=df_comparison)

# ================================
# 5. Visualization of QFT Output
# ================================
x_values = np.arange(N_STATES)
plt.figure(figsize=(12, 6))
plt.plot(x_values, np.abs(pru_qft_result), label="PRU-QFT", linestyle="dashed", marker="o", color="blue")
plt.plot(x_values, np.abs(standard_qft_result), label="Standard QFT", linestyle="solid", marker="x", color="red")
plt.xlabel("Basis States")
plt.ylabel("Probability Amplitude")
plt.title(f"PRU-QFT vs Standard QFT ({N_QUBITS} Qubits)")
plt.legend()
plt.grid()
plt.show()

# ================================
# 6. Results Summary (Fidelity)
# ================================
fidelity = np.abs(np.dot(np.conjugate(pru_qft_result), standard_qft_result)) ** 2
print(f"✅ PRU-QFT Fidelity with Standard QFT: {fidelity:.6f}")
print(
    "🚀 In a PRU framework, if every particle updates in parallel, the update scales as O(N) (conceptually), compared to O(N²) for a serial full-matrix computation.")
