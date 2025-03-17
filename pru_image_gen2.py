import numpy as np
import cv2
import networkx as nx
import pickle
import random
import matplotlib.pyplot as plt
from skimage import io
from skimage.color import rgb2lab, lab2rgb
from scipy.spatial import KDTree

# ============================================
# PRU Image Knowledge System
# ============================================

class PRU_Image_Generator:
    def __init__(self, storage_file="pru_image_knowledge.pkl"):
        self.storage_file = storage_file
        self.graph = nx.Graph()  # PRU Relational Graph
        self.image_database = {}  # Store image metadata & pixel data
        self.load_knowledge()

    def load_knowledge(self):
        """Load PRU image knowledge from storage."""
        try:
            with open(self.storage_file, "rb") as f:
                self.graph, self.image_database = pickle.load(f)
            print("✅ PRU Image Knowledge Loaded.")
        except FileNotFoundError:
            print("⚠️ No existing knowledge found. Initializing new database.")

    def save_knowledge(self):
        """Save PRU image knowledge to disk."""
        with open(self.storage_file, "wb") as f:
            pickle.dump((self.graph, self.image_database), f)
        print("💾 Knowledge Saved!")

    def process_image(self, image_url, label, artist, style):
        """Convert an image into PRU format and store it."""
        image = io.imread(image_url)
        image = cv2.resize(image, (256, 256))  # Standardize size
        lab_image = rgb2lab(image)  # Convert to LAB color space for better similarity
        pixel_data = lab_image.reshape(-1, 3)  # Flatten pixels
        tree = KDTree(pixel_data)  # Efficient nearest neighbor search

        # Store image metadata
        self.image_database[label] = {
            "artist": artist,
            "style": style,
            "pixels": pixel_data,
            "tree": tree
        }

        # Build PRU relational graph (connecting similar colors)
        for i in range(len(pixel_data)):
            neighbors = tree.query(pixel_data[i], k=5)[1]  # Find closest neighbors
            for n in neighbors:
                self.graph.add_edge(f"{label}_{i}", f"{label}_{n}", weight=1.0)

        print(f"📸 Processed image: {label} | Artist: {artist} | Style: {style}")
        self.save_knowledge()

    def generate_image(self, label, output_size=(256, 256)):
        """Generate a new image based on stored knowledge."""
        if label not in self.image_database:
            print("❌ No stored image data found for:", label)
            return None

        base_pixels = self.image_database[label]["pixels"]
        generated_pixels = np.zeros_like(base_pixels)

        for i in range(len(base_pixels)):
            # Retrieve similar color from PRU knowledge
            neighbors = list(self.graph.neighbors(f"{label}_{i}"))
            if neighbors:
                selected_neighbor = random.choice(neighbors)
                selected_idx = int(selected_neighbor.split("_")[-1])
                generated_pixels[i] = base_pixels[selected_idx]
            else:
                generated_pixels[i] = base_pixels[i]  # Default to original

        # Convert back to RGB
        generated_image = lab2rgb(generated_pixels.reshape(output_size + (3,)))
        return generated_image

    def visualize_generated_image(self, label):
        """Display the generated image."""
        generated_image = self.generate_image(label)
        if generated_image is not None:
            plt.imshow(generated_image)
            plt.axis("off")
            plt.title(f"Generated Image Based on {label}")
            plt.show()
        else:
            print("⚠️ Could not generate an image.")

# ============================================
# Running the Experiment
# ============================================

# Initialize PRU Image System
pru_image_system = PRU_Image_Generator()

# Example: Process public domain artworks
pru_image_system.process_image(
    image_url="https://upload.wikimedia.org/wikipedia/commons/6/66/VanGogh-starry_night_ballance1.jpg",
    label="Starry_Night",
    artist="Vincent van Gogh",
    style="Post-Impressionism"
)

pru_image_system.process_image(
    image_url="https://upload.wikimedia.org/wikipedia/commons/9/98/Mona_Lisa%2C_by_Leonardo_da_Vinci%2C_from_C2RMF_retouched.jpg",
    label="Mona_Lisa",
    artist="Leonardo da Vinci",
    style="Renaissance"
)

# Generate new image
pru_image_system.visualize_generated_image("Starry_Night")
pru_image_system.visualize_generated_image("Mona_Lisa")
