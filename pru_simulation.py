import pygame
import numpy as np
import math
import random
from scipy.spatial import KDTree
from numba import jit

# =============================================================================
# Fundamental Constants & Simulation Parameters
# =============================================================================
PI = math.pi  # Circular motion, etc.
C = 299792458  # Speed of light (limit)
H = 6.626e-34  # Planck's constant
ALPHA = 1 / 137  # Fine-structure constant
PHI = (1 + math.sqrt(5)) / 2  # Golden Ratio
LAMBDA = 1e-9  # Cosmological constant (set to 0 in solar mode if desired)
EULER_IDENTITY = math.e ** (1j * math.pi) + 1

WIDTH, HEIGHT = 1200, 800  # Screen dimensions
FPS = 60
DT = 86400  # Base time step: 1 day (in seconds)
time_speed = 1.0  # Multiplier for time progression

# Interaction scaling parameters (for the cosmic simulation)
G_SIM = 6e-11  # Adjusted gravitational constant (in SI, scaled)
EPSILON = 1e-2  # Softening constant to avoid singularities
EM_SIM = 0.0  # No electromagnetic forces for our large-scale simulation
QUANTUM_JITTER = 0.0  # No jitter for a clean simulation
QUANTUM_SCALE = 1  # Discrete space unit
ENTANGLEMENT_COEFF = 0.0  # Disabled in this simulation for realism
NUM_RANDOM_PARTICLES = 100
# For adding radiation pressure (if desired, here we keep it off)
R_PRESSURE = 0.005
LIGHT_EFFECT_RADIUS = 150

# Visualization scaling: 300 pixels represent 4500e6 km (approximate)
AU_TO_PIXELS = 300 / 4500e6
MASS_SCALE = 1e-27  # Scale down real masses

# =============================================================================
# Modes: "solar" or "galaxy"
# =============================================================================
mode = "solar"  # Start in solar system mode

# =============================================================================
# Solar System Data (Scaled, PRU Method)
# =============================================================================
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PURPLE = (80, 0, 80)

SOLAR_SYSTEM = [
    {"name": "Sun", "mass": 1.989e30, "radius": 50, "color": YELLOW,
     "pos": np.array([WIDTH // 2, HEIGHT // 2], dtype=np.float64)},
    {"name": "Mercury", "mass": 3.285e23, "radius": 5, "color": WHITE, "distance": 57.9e6},
    {"name": "Venus", "mass": 4.867e24, "radius": 10, "color": BLUE, "distance": 108.2e6},
    {"name": "Earth", "mass": 5.972e24, "radius": 12, "color": BLUE, "distance": 149.6e6},
    {"name": "Mars", "mass": 6.39e23, "radius": 8, "color": RED, "distance": 227.9e6},
    {"name": "Jupiter", "mass": 1.898e27, "radius": 30, "color": WHITE, "distance": 778.5e6},
    {"name": "Saturn", "mass": 5.683e26, "radius": 28, "color": WHITE, "distance": 1434e6},
    {"name": "Uranus", "mass": 8.681e25, "radius": 20, "color": BLUE, "distance": 2871e6},
    {"name": "Neptune", "mass": 1.024e26, "radius": 18, "color": BLUE, "distance": 4495e6},
]

# Compute initial positions and orbital velocities for planets (except the Sun)
for planet in SOLAR_SYSTEM[1:]:
    angle = random.uniform(0, 2 * PI)
    planet["pos"] = np.array([
        WIDTH // 2 + planet["distance"] * AU_TO_PIXELS * math.cos(angle),
        HEIGHT // 2 + planet["distance"] * AU_TO_PIXELS * math.sin(angle)
    ], dtype=np.float64)
    planet["angle"] = angle
    sun_mass_scaled = SOLAR_SYSTEM[0]["mass"] * MASS_SCALE
    r = planet["distance"] * AU_TO_PIXELS
    v_mag = math.sqrt(G_SIM * sun_mass_scaled / (r + EPSILON))
    planet["velocity"] = np.array([-math.sin(angle), math.cos(angle)]) * v_mag

# =============================================================================
# Pygame Initialization & Global Variables
# =============================================================================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PRU-Controlled Universe Sandbox")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)

# Camera for cosmic view
camera_x, camera_y = WIDTH / 2, HEIGHT / 2
zoom = 1.0

# Global list for particles (our cosmic objects)
particles = []
# We'll also allow adding black holes later.
# Global list for light sources (if needed)
lights = []

# Pre-generate a star field (for the galaxy background)
NUM_STARS = 300
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(NUM_STARS)]


# =============================================================================
# Particle Class – Represents a Celestial Body in our PRU Simulation
# =============================================================================
class Particle:
    def __init__(self, name, position, mass, velocity, charge, color, visual_radius, fixed=False):
        self.name = name
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.mass = mass  # Scaled mass
        self.charge = charge  # For our solar system bodies, usually 0
        self.color = color
        self.visual_radius = visual_radius  # For drawing and collisions
        self.fixed = fixed  # Fixed bodies (like the Sun) don't move
        self.size = visual_radius  # Visual size for drawing
        self.trail = []  # (Trails are not drawn in this version)

    def draw(self, surface):
        x_screen = int((self.position[0] - camera_x) * zoom + WIDTH / 2)
        y_screen = int((self.position[1] - camera_y) * zoom + HEIGHT / 2)
        pygame.draw.circle(surface, self.color, (x_screen, y_screen), max(1, int(self.size * zoom)))


# =============================================================================
# Vectorized PRU Update Function using KDTree and Numba acceleration
# =============================================================================
@jit(nopython=True)
def compute_force(pos, neighbor_pos, neighbor_mass, G_val, eps):
    total = np.zeros(2)
    for k in range(neighbor_pos.shape[0]):
        diff0 = neighbor_pos[k, 0] - pos[0]
        diff1 = neighbor_pos[k, 1] - pos[1]
        dist = math.sqrt(diff0 * diff0 + diff1 * diff1) + eps
        total[0] += G_val * neighbor_mass[k] * diff0 / (dist * dist * dist)
        total[1] += G_val * neighbor_mass[k] * diff1 / (dist * dist * dist)
    return total


def update_universe():
    # Rebuild KDTree from current positions of all particles
    positions = np.array([p.position for p in particles])
    kdtree = KDTree(positions)
    # For each particle (skip fixed ones), query nearest neighbors (k=4: itself + 3 neighbors)
    for i, p in enumerate(particles):
        if p.fixed:
            continue
        neighbors_idx = kdtree.query(positions[i], k=4)[1]
        # Exclude self if present
        neighbor_list = [particles[j] for j in neighbors_idx if j != i]
        if len(neighbor_list) == 0:
            continue
        neighbor_positions = np.array([n.position for n in neighbor_list])
        neighbor_masses = np.array([n.mass for n in neighbor_list])
        force = compute_force(p.position, neighbor_positions, neighbor_masses, G_SIM, EPSILON)
        # Update velocity and position using simple Euler integration
        p.velocity += force * DT * time_speed  # DT scaled by time_speed
        p.position += p.velocity * DT * time_speed


# =============================================================================
# Collision Handling – Merge Non-Fixed Particles That Are Too Close
# =============================================================================
def handle_collisions():
    global particles
    merged = []
    to_remove = set()
    N = len(particles)
    for i in range(N):
        for j in range(i + 1, N):
            p1 = particles[i]
            p2 = particles[j]
            if p1.fixed or p2.fixed:
                continue
            if np.linalg.norm(p1.position - p2.position) < (p1.visual_radius + p2.visual_radius) * 0.5:
                new_mass = p1.mass + p2.mass
                new_velocity = (p1.mass * p1.velocity + p2.mass * p2.velocity) / new_mass
                new_color = tuple(min(255, int((p1.color[k] * p1.mass + p2.color[k] * p2.mass) / new_mass))
                                  for k in range(3))
                new_radius = (p1.visual_radius ** 3 + p2.visual_radius ** 3) ** (1 / 3)
                new_position = (p1.mass * p1.position + p2.mass * p2.position) / new_mass
                merged.append(
                    Particle(p1.name + "+" + p2.name, new_position, new_mass, new_velocity, 0, new_color, new_radius))
                to_remove.add(i)
                to_remove.add(j)
    if to_remove:
        particles = [particles[i] for i in range(N) if i not in to_remove]
        particles.extend(merged)


# =============================================================================
# Utility Functions to Create Particles, Black Holes, etc.
# =============================================================================
def create_particle_from_dict(planet):
    name = planet["name"]
    color = planet["color"]
    if name == "Sun":
        pos = planet["pos"]
        velocity = np.array([0, 0])
        fixed = True
    else:
        angle = random.uniform(0, 2 * PI)
        pos = np.array([
            WIDTH // 2 + planet["distance"] * AU_TO_PIXELS * math.cos(angle),
            HEIGHT // 2 + planet["distance"] * AU_TO_PIXELS * math.sin(angle)
        ], dtype=np.float64)
        sun = next((p for p in particles if p.name == "Sun"), None)
        if sun is not None:
            r = np.linalg.norm(pos - sun.position)
            v_mag = math.sqrt(G_SIM * sun.mass / (r + EPSILON))
        else:
            v_mag = 0.3
        velocity = np.array([-math.sin(angle), math.cos(angle)]) * v_mag
        fixed = False
    mass = planet["mass"] * MASS_SCALE
    visual_radius = planet["radius"]
    particles.append(Particle(name, pos, mass, velocity, 0, color, visual_radius, fixed))


def create_initial_particles():
    for planet in SOLAR_SYSTEM:
        create_particle_from_dict(planet)
    # Add random particles to fill the universe (so total ≈ 100)
    for _ in range(NUM_RANDOM_PARTICLES):
        pos = np.array([random.uniform(0, WIDTH), random.uniform(0, HEIGHT)], dtype=np.float64)
        mass = random.uniform(50, 1000) * MASS_SCALE
        velocity = np.array([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])
        color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        visual_radius = random.uniform(3, 8)
        particles.append(Particle("Asteroid", pos, mass, velocity, 0, color, visual_radius))


def create_random_particle(position):
    pos = np.array(position, dtype=np.float64)
    sun = next((p for p in particles if p.name == "Sun"), None)
    if sun:
        r_vec = pos - sun.position
        r = np.linalg.norm(r_vec)
        if r > EPSILON:
            angle = math.atan2(r_vec[1], r_vec[0])
            v_dir = np.array([-math.sin(angle), math.cos(angle)])
            v_mag = math.sqrt(G_SIM * sun.mass / (r + EPSILON))
            velocity = v_dir * v_mag
        else:
            velocity = np.array([0, 0])
    else:
        velocity = np.array([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])
    mass = random.uniform(50, 1000) * MASS_SCALE
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    visual_radius = random.uniform(5, 20)
    particles.append(Particle("Custom", pos, mass, velocity, 0, color, visual_radius))


def create_random_blackhole(position):
    # Create a black hole: very high mass, small visual radius, distinct color
    pos = np.array(position, dtype=np.float64)
    mass = random.uniform(1e29, 5e29) * MASS_SCALE
    velocity = np.array([0, 0])  # Initially stationary
    color = PURPLE
    visual_radius = random.uniform(8, 15)
    particles.append(Particle("BlackHole", pos, mass, velocity, 0, color, visual_radius, fixed=False))


def create_random_light(position):
    lights.append(position)


# =============================================================================
# Terrestrial Environment: Simple Sky, Ground, and a Moving Sun
# =============================================================================
def draw_earth_environment(surface, current_time):
    # Draw a sky gradient (top 3/4 of the screen)
    for y in range(0, int(HEIGHT * 0.75)):
        ratio = y / (HEIGHT * 0.75)
        sky_color = (int(10 + 20 * ratio), int(10 + 30 * ratio), int(40 + 60 * ratio))
        pygame.draw.line(surface, sky_color, (0, y), (WIDTH, y))
    # Draw a ground gradient (bottom 1/4)
    for y in range(int(HEIGHT * 0.75), HEIGHT):
        ratio = (y - HEIGHT * 0.75) / (HEIGHT * 0.25)
        ground_color = (int(30 + 50 * ratio), int(100 + 80 * ratio), int(30 + 50 * ratio))
        pygame.draw.line(surface, ground_color, (0, y), (WIDTH, y))
    # Compute sun position based on time_of_day (0-24 hours)
    sun_angle = (current_time - 6) / 12 * PI  # At 6h: left horizon, 12h: top, 18h: right horizon
    sun_orbit_radius = 300
    sun_x = WIDTH / 2 + sun_orbit_radius * math.cos(sun_angle - PI)
    sun_y = HEIGHT * 0.75 - sun_orbit_radius * math.sin(sun_angle - PI)
    brightness = max(0, min(255, int(255 * math.sin(sun_angle))))
    sun_color = (brightness, brightness, 0)
    pygame.draw.circle(surface, sun_color, (int(sun_x), int(sun_y)), 40)


# =============================================================================
# Main Simulation Loop – Integrated Cosmic & Terrestrial Views with Galaxy Mode
# =============================================================================
def main():
    global camera_x, camera_y, zoom, DT, time_speed, mode
    create_initial_particles()
    simulation_time = 0.0
    time_of_day = 12.0  # Start at noon in solar mode
    paused = False
    running = True

    while running:
        # Clear cosmic surface
        cosmic_surface = pygame.Surface((WIDTH, HEIGHT))
        cosmic_surface.fill(BLACK)
        # Draw star field background on cosmic surface
        for star in stars:
            pygame.draw.circle(cosmic_surface, WHITE, star, 1)

        if not paused:
            update_universe()
            simulation_time += DT * time_speed
            handle_collisions()
            if mode == "solar":
                time_of_day = (time_of_day + 0.01 * time_speed * DT) % 24

        # Draw cosmic particles on cosmic surface
        for p in particles:
            p.draw(cosmic_surface)
        for light in lights:
            lx = int((light[0] - camera_x) * zoom + WIDTH / 2)
            ly = int((light[1] - camera_y) * zoom + HEIGHT / 2)
            pygame.draw.circle(cosmic_surface, (255, 255, 100), (lx, ly), 6)

        # Mode switching: in "solar" mode, draw Earth environment and overlay cosmic sky
        if mode == "solar":
            screen.fill(BLACK)
            draw_earth_environment(screen, time_of_day)
            sky_rect = pygame.Rect(0, 0, WIDTH, int(HEIGHT * 0.75))
            cosmic_part = cosmic_surface.subsurface(sky_rect)
            screen.blit(cosmic_part, (0, 0))
        else:
            # In "galaxy" mode, show full cosmic view
            screen.blit(cosmic_surface, (0, 0))

        # Debug Overlay
        total_mass = sum(p.mass for p in particles)
        info_text = f"Time: {simulation_time:.1f}s | Mode: {mode} | Particles: {len(particles)} | DT: {DT:.3e} | Total Mass: {total_mass:.3e}"
        info_text += f" | TimeSpeed: {time_speed:.2f}"
        if mode == "solar":
            info_text += f" | Hour: {time_of_day:.1f}"
        overlay = font.render(info_text, True, WHITE)
        screen.blit(overlay, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle pause
                if event.key == pygame.K_SPACE:
                    paused = not paused
                # Adjust time speed
                elif event.key == pygame.K_UP:
                    time_speed *= 1.1
                elif event.key == pygame.K_DOWN:
                    time_speed /= 1.1
                # Switch mode between "solar" and "galaxy"
                elif event.key == pygame.K_m:
                    mode = "galaxy" if mode == "solar" else "solar"
                # Add a new black hole with key "b"
                elif event.key == pygame.K_b:
                    # Place black hole at random cosmic coordinates
                    pos = np.array([random.uniform(0, WIDTH), random.uniform(0, HEIGHT)], dtype=np.float64)
                    create_random_blackhole(pos)
                # Adjust time-of-day in solar mode with left/right arrows
                elif event.key == pygame.K_LEFT and mode == "solar":
                    time_of_day = (time_of_day - 0.5) % 24
                elif event.key == pygame.K_RIGHT and mode == "solar":
                    time_of_day = (time_of_day + 0.5) % 24
                # Add a new planet with key "n"
                elif event.key == pygame.K_n:
                    # Add a planet with random properties at a random position relative to the Sun
                    sun = next((p for p in particles if p.name == "Sun"), None)
                    if sun is not None:
                        angle = random.uniform(0, 2 * PI)
                        distance = random.uniform(1e8, 4e9)
                        pos = np.array([
                            WIDTH // 2 + distance * AU_TO_PIXELS * math.cos(angle),
                            HEIGHT // 2 + distance * AU_TO_PIXELS * math.sin(angle)
                        ], dtype=np.float64)
                        new_planet = {
                            "name": f"Planet-{len(particles)}",
                            "mass": 5.972e24,
                            "radius": 10,
                            "color": WHITE,
                            "distance": distance,
                            "pos": pos,
                            "angle": angle,
                            "velocity": np.array([-math.sin(angle), math.cos(angle)]) * 0.3
                        }
                        # Create from dict
                        create_particle_from_dict(new_planet)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                world_x = (mx - WIDTH / 2) / zoom + camera_x
                world_y = (my - HEIGHT / 2) / zoom + camera_y
                # Left-click: add a new cosmic particle
                if event.button == 1:
                    create_random_particle([world_x, world_y])
                # Right-click: add a new light source
                elif event.button == 3:
                    create_random_light([world_x, world_y])
            elif event.type == pygame.MOUSEWHEEL:
                zoom *= 1.1 if event.y > 0 else 0.9

        # Camera Movement (WASD)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            camera_y -= 10 / zoom
        if keys[pygame.K_s]:
            camera_y += 10 / zoom
        if keys[pygame.K_a]:
            camera_x -= 10 / zoom
        if keys[pygame.K_d]:
            camera_x += 10 / zoom

    pygame.quit()


if __name__ == '__main__':
    main()
