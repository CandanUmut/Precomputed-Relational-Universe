import pygame
import numpy as np
import sys
from scipy.spatial import KDTree

# -------------------- Fundamental Constants & PRU Derived Values -------------------- #
# Given (SI) values:
c_standard = 2.99792458e8             # speed of light (m/s)
h_standard = 6.62607015e-34           # Planck's constant (J·s)
Lambda = 1.0e-52                    # Cosmological constant (m^-2)
alpha = 1/137.0                     # Fine-structure constant (dimensionless)
N_total = 1.66e79                   # Estimated total number of particles in the universe

sqrt_N = np.sqrt(N_total)
log_N = np.log(N_total)

# Derived constants using the PRU formulas:
G = (c_standard * h_standard) / (Lambda * alpha * sqrt_N)
entropy_correction = log_N / np.sqrt(N_total**(1/6))
c_derived = (h_standard / (Lambda * alpha * entropy_correction))**(1.005/3)
h_derived = (c_standard * Lambda * log_N)**(1/3) * (N_total**(-1/4.08))
decay_correction = np.exp(-log_N / (N_total**(10/255)))
pi_derived = (log_N / ((Lambda * c_standard)**0.5))**(1/6) * decay_correction

# -------------------- Simulation & Display Setup -------------------- #
sim_width, sim_height = 100.0, 100.0  # simulation space dimensions (simulation units)
window_width, window_height = 800, 800  # Pygame window dimensions (pixels)

# Scaling factors (simulation to screen)
scale_x = window_width / sim_width
scale_y = window_height / sim_height

def sim_to_screen(pos):
    """Convert simulation coordinates (origin bottom-left) to screen coordinates (origin top-left)."""
    x, y = pos
    screen_x = int(x * scale_x)
    screen_y = int(window_height - y * scale_y)
    return (screen_x, screen_y)

# -------------------- Particle Type and Phase Definitions -------------------- #
# Define intrinsic properties for different particle types.
particle_types = {
    "electron": {"charge": -1.0, "mass": 0.5, "base_color": (0, 0, 255)},
    "proton":   {"charge": 1.0, "mass": 10.0, "base_color": (255, 0, 0)},
    "quantum":  {"charge": 0.0, "mass": 1.0, "base_color": (255, 255, 0)},
    "qubit":    {"charge": 0.0, "mass": 0.8, "base_color": (0, 255, 255)}
}
available_types = list(particle_types.keys())

def determine_phase(temperature):
    """Assign a phase based on temperature."""
    if temperature < 290:
        return "solid"
    elif temperature < 310:
        return "liquid"
    else:
        return "gas"

# Phase-dependent friction (damping) factors:
phase_friction = {
    "solid": 0.9,
    "liquid": 0.5,
    "gas": 0.1
}

# -------------------- Particle Class -------------------- #
class Particle:
    def __init__(self, pid):
        self.id = pid
        self.position = np.random.rand(2) * np.array([sim_width, sim_height])
        self.velocity = np.random.randn(2) * 0.1
        # Assign a random type and use its properties (with slight random variations)
        self.particle_type = np.random.choice(available_types)
        type_props = particle_types[self.particle_type]
        self.mass = type_props["mass"] * np.random.uniform(0.9, 1.1)
        self.charge = type_props["charge"]
        self.temperature = np.random.uniform(280, 320)
        self.phase = determine_phase(self.temperature)
        self.memory = []
        self.consciousness = 0
        # For entanglement: will hold the partner's particle ID (or None if not entangled)
        self.entangled_partner = None

    def interact(self, neighbors):
        """Compute net force from emergent gravitational and electromagnetic interactions."""
        net_force = np.zeros(2)
        for other in neighbors:
            if other.id == self.id:
                continue
            r_vec = other.position - self.position
            r = np.linalg.norm(r_vec) + 1e-5  # avoid division by zero
            # Gravitational force (using derived G)
            grav_force_mag = G * self.mass * other.mass / (r**2)
            grav_force = (r_vec / r) * grav_force_mag
            # Electromagnetic force (Coulomb)
            em_force_mag = 8.9875517923e9 * self.charge * other.charge / (r**2)
            em_force = (r_vec / r) * em_force_mag
            net_force += (grav_force + em_force)
        return net_force

    def update_consciousness(self):
        """Store a short-term memory of positions and update the 'consciousness' metric."""
        if len(self.memory) > 10:
            self.memory.pop(0)
        self.memory.append(self.position.copy())
        self.consciousness = np.exp(-len(self.memory) / 10)

    def update_temperature(self, neighbors, dt):
        """Simple thermal conduction: adjust temperature toward the local average."""
        if neighbors:
            avg_temp = np.mean([n.temperature for n in neighbors])
            self.temperature += 0.01 * (avg_temp - self.temperature) * dt

    def update_phase(self):
        """Update phase based on current temperature."""
        self.phase = determine_phase(self.temperature)

    def update(self, neighbors, dt):
        """Update the particle's state: position, velocity, temperature, and phase."""
        force = self.interact(neighbors)
        acceleration = force / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        self.update_consciousness()
        self.update_temperature(neighbors, dt)
        self.update_phase()
        # Apply phase-dependent friction (simulate cohesive or constrained behavior)
        friction = phase_friction[self.phase]
        self.velocity *= (1 - friction * dt * 0.01)
        # Wrap-around boundaries
        self.position[0] %= sim_width
        self.position[1] %= sim_height

# -------------------- Particle Initialization with Entanglement -------------------- #
def init_particles(num_particles=500, entanglement_fraction=0.1):
    particles = [Particle(i) for i in range(num_particles)]
    # Determine the number of entangled pairs
    num_pairs = int(entanglement_fraction * num_particles / 2)
    if num_pairs > 0:
        # Randomly select 2*num_pairs unique indices
        indices = np.random.choice(num_particles, size=2*num_pairs, replace=False)
        # Pair them up
        for i in range(0, len(indices), 2):
            a, b = indices[i], indices[i+1]
            particles[a].entangled_partner = b
            particles[b].entangled_partner = a
    return particles

particles = init_particles()

# -------------------- Pygame Setup -------------------- #
pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Comprehensive PRU Universe with Entanglement")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Simulation control variables
dt = 1.0          # time step
paused = False    # pause flag
draw_trails = True  # trail toggle
step_count = 0

# -------------------- Main Simulation Loop -------------------- #
running = True
while running:
    clock.tick(60)  # limit to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Keyboard controls:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                particles = init_particles()
                step_count = 0
            elif event.key == pygame.K_UP:
                dt *= 1.1
            elif event.key == pygame.K_DOWN:
                dt /= 1.1
            elif event.key == pygame.K_t:
                draw_trails = not draw_trails

    if not paused:
        # Update particles using KDTree for neighbor search.
        positions = np.array([p.position for p in particles])
        tree = KDTree(positions)
        for p in particles:
            _, indices = tree.query(p.position, k=10)
            neighbors = [particles[i] for i in indices if i != p.id]
            p.update(neighbors, dt)
        step_count += 1

        # -------------------- Entanglement Update --------------------
        # For each entangled pair (process only once per pair), synchronize state.
        for p in particles:
            if p.entangled_partner is not None and p.id < p.entangled_partner:
                partner = particles[int(p.entangled_partner)]
                # Average the states (position, velocity, temperature)
                new_position = (p.position + partner.position) / 2.0
                new_velocity = (p.velocity + partner.velocity) / 2.0
                new_temperature = (p.temperature + partner.temperature) / 2.0
                p.position = new_position.copy()
                partner.position = new_position.copy()
                p.velocity = new_velocity.copy()
                partner.velocity = new_velocity.copy()
                p.temperature = new_temperature
                partner.temperature = new_temperature
                # Update phases accordingly
                p.phase = determine_phase(new_temperature)
                partner.phase = determine_phase(new_temperature)

    # --------------- Drawing Section ---------------
    screen.fill((0, 0, 0))  # clear screen

    if draw_trails:
        for p in particles:
            if len(p.memory) > 1:
                trail_points = [sim_to_screen(pos) for pos in p.memory]
                pygame.draw.lines(screen, (0, 255, 0), False, trail_points, 1)

    # Draw particles with color determined by type, temperature, and phase.
    for p in particles:
        pos = sim_to_screen(p.position)
        # Base color from particle type
        base_color = np.array(particle_types[p.particle_type]["base_color"])
        # Adjust color based on temperature: cooler vs. hotter
        temp_norm = np.clip((p.temperature - 300) / 100, -1, 1)
        red = int(base_color[0] + 128 * temp_norm)
        blue = int(base_color[2] - 128 * temp_norm)
        green = int(255 * p.consciousness)
        color = (np.clip(red, 0, 255), np.clip(green, 0, 255), np.clip(blue, 0, 255))
        pygame.draw.circle(screen, color, pos, 3)

    # Display simulation info and derived constants
    info_text = [
        f"Steps: {step_count}",
        f"dt: {dt:.3f}",
        f"Particles: {len(particles)}",
        f"Paused: {paused}",
        f"Trails: {draw_trails}",
        f"G (derived): {G:.3e} m^3/kg/s^2",
        f"c (derived): {c_derived:.3e} m/s",
        f"h (derived): {h_derived:.3e} J·s",
        f"π (derived): {pi_derived:.6f}",
        "Controls: SPACE pause, R reset, UP/DOWN dt, T trails"
    ]
    for i, line in enumerate(info_text):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10 + i * 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
