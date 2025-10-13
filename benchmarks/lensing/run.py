
import numpy as np

G = 6.6743e-11
c = 299792458.0

def deflection_angles(M=1.0e30, b_min=1.0e9, b_max=1.0e11, num=10):
    b = np.linspace(b_min, b_max, num)
    theta = 4*G*M/(c**2*b)  # radians
    return b, theta

if __name__ == "__main__":
    b, th = deflection_angles()
    print("# impact_parameter_m, deflection_rad")
    for bi, ti in zip(b, th):
        print(f"{bi:.6e}, {ti:.6e}")
