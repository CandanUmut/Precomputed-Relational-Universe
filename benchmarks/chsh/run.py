
import numpy as np

def quantum_E(thetaA, thetaB):
    return -np.cos(thetaA - thetaB)

def sample_pair(E, n=10000, rng=None):
    rng = np.random.default_rng(rng)
    same = rng.random(n) < (1+E)/2.0
    a = rng.choice([-1, 1], size=n)
    b = np.where(same, a, -a)
    return a, b

def corr(a, b):
    return np.mean(a * b)

def chsh_S():
    a0, a1 = 0.0, np.pi/2
    b0, b1 = np.pi/4, -np.pi/4
    pairs = [(a0,b0),(a0,b1),(a1,b0),(a1,b1)]
    Es = []
    for (A,B) in pairs:
        E = quantum_E(A,B)
        a,b = sample_pair(E, n=20000, rng=42)
        Es.append(corr(a,b))
    S = Es[0] + Es[1] + Es[2] - Es[3]
    return S, Es

if __name__ == "__main__":
    S, Es = chsh_S()
    print(f"CHSH S ≈ {S:.3f}  (target ≈ 2.828).  E's={['%.3f'%e for e in Es]}")
