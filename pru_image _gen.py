import numpy as np
import matplotlib.pyplot as plt
import pickle
import networkx as nx
from PIL import Image

# ================================
# 1️⃣ PRU Image Storage System
# ================================

class PRU_Image_Storage:
    def __init__(self, storage_file="pru_image_data.pkl"):
        self.graph = nx.Graph()
        self.pixel_map = {}
        self.storage_file = storage_file
        self.load_data()

    def process_image(self, image_path, downscale_factor=2):
        """ Convert an image into a relational knowledge matrix and store it """
        img = Image.open(image_path)
        img = img.convert("RGB")  # Convert to RGB if needed
        img = img.resize((img.width // downscale_factor, img.height // downscale_factor))  # Downscale for efficiency
        pixels = np.array(img)

        h, w, _ = pixels.shape
        for i in range(h):
            for j in range(w):
                pixel_value = tuple(pixels[i, j])  # Store as (R, G, B)
                self.pixel_map[(i, j)] = pixel_value  # Store pixel in map
                
                # Establish relations with neighboring pixels
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-connectivity
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < h and 0 <= nj < w:
                        self.graph.add_edge((i, j), (ni, nj), weight=np.linalg.norm(np.array(pixel_value) - np.array(pixels[ni, nj])))

        self.save_data()
        print("✅ Image processed and stored in PRU.")

    def reconstruct_image(self):
        """ Reconstruct an image from PRU stored knowledge """
        if not self.pixel_map:
            print("⚠️ No image data found in PRU storage.")
            return
        
        h = max([key[0] for key in self.pixel_map.keys()]) + 1
        w = max([key[1] for key in self.pixel_map.keys()]) + 1
        reconstructed_pixels = np.zeros((h, w, 3), dtype=np.uint8)

        for (i, j), color in self.pixel_map.items():
            reconstructed_pixels[i, j] = color  # Retrieve stored color

        reconstructed_img = Image.fromarray(reconstructed_pixels)
        return reconstructed_img

    def save_data(self):
        """ Save PRU knowledge to disk """
        with open(self.storage_file, "wb") as f:
            pickle.dump((self.graph, self.pixel_map), f)

    def load_data(self):
        """ Load PRU knowledge if available """
        try:
            with open(self.storage_file, "rb") as f:
                self.graph, self.pixel_map = pickle.load(f)
            print("✅ PRU Image Data Loaded from Storage.")
        except FileNotFoundError:
            print("⚠️ No existing PRU Image Data found. Starting fresh.")

# ================================
# 2️⃣ Running PRU Image Storage & Retrieval
# ================================

if __name__ == "__main__":
    image_path = "/mnt/data/93384955-AE92-468E-813A-FDA52184B571.jpeg"  # Update with your image path
    pru_storage = PRU_Image_Storage()

    # Process and store image
    pru_storage.process_image(image_path, downscale_factor=4)

    # Reconstruct and display stored image
    reconstructed_img = pru_storage.reconstruct_image()
    if reconstructed_img:
        plt.imshow(reconstructed_img)
        plt.axis("off")
        plt.title("Reconstructed Image from PRU")
        plt.show()
