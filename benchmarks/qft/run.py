
import numpy as np
import time

def qft_matrix(N):
    omega = np.exp(2j * np.pi / N)
    j = np.arange(N).reshape(N,1)
    k = np.arange(N).reshape(1,N)
    U = omega**(j*k) / np.sqrt(N)
    return U

def run_qft_check(N=256, rng=0):
    rng = np.random.default_rng(rng)
    x = rng.normal(size=N) + 1j*rng.normal(size=N)
    U = qft_matrix(N)
    t0 = time.time()
    y_qft = U @ x
    t1 = time.time()
    t2 = time.time()
    y_fft = np.fft.fft(x)/np.sqrt(N)
    t3 = time.time()
    err = np.linalg.norm(y_qft - y_fft) / np.linalg.norm(y_fft)
    return err, (t1-t0), (t3-t2)

if __name__ == "__main__":
    for N in [64,128,256,512]:
        err, tqft, tfft = run_qft_check(N)
        print(f"N={N:4d}  L2-error={err:.3e}  time(QFT-mat)={tqft*1000:.1f} ms  time(FFT)={tfft*1000:.1f} ms")
