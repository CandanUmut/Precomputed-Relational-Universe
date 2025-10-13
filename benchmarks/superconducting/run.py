
import numpy as np
from scipy.sparse import diags
from scipy.linalg import eigh_tridiagonal

def potential(phi, EJ=1.0, EL=0.05, phi_ext=np.pi):
    return EJ*(1-np.cos(phi)) + 0.5*EL*(phi - phi_ext)**2

def eigenlevels(N=1024, L=4*np.pi, EJ=1.0, EL=0.05, phi_ext=np.pi, mass=1.0, hbar=1.0, k=6):
    x = np.linspace(-L/2, L/2, N)
    dx = x[1]-x[0]
    V = potential(x, EJ, EL, phi_ext)
    c = (hbar**2)/(2*mass*dx**2)
    main = 2*c + V
    off  = -c*np.ones(N-1)
    w, _ = eigh_tridiagonal(main, off, select='i', select_range=(0, k-1))
    return w, x, V

if __name__ == "__main__":
    w, x, V = eigenlevels(N=512, EJ=1.0, EL=0.05, phi_ext=np.pi, mass=1.0, hbar=1.0, k=6)
    print("First 6 eigenlevels (arb. units):")
    for i, e in enumerate(w):
        print(f"  E{i} = {e:.6f}")
