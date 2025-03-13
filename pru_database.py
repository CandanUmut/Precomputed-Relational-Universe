import numpy as np
import pickle
import time
import os

# ================================
# PRU Dynamic Expansion Model
# ================================

class PRUConstructor:
    def __init__(self, database_size=0, save_path="pru_database.pkl"):
        """Initialize PRU Constructor with dynamic expansion capability."""
        self.database_size = database_size
        self.save_path = save_path
        self.database = []
        self.relational_map = {}

        # Try loading existing PRU database if available
        self.load_database()

    def construct_database(self, initial_size):
        """Constructs a PRU relational database and saves it for future lookups."""
        if len(self.database) == 0:  # Only build if it doesn't exist
            print("🔄 Constructing PRU Database...")
            start_time = time.time()
            
            # Generate a dataset (unique values)
            self.database = list(np.random.choice(range(initial_size), initial_size, replace=False))
            
            # Create relational mappings (O(N) only once)
            self.relational_map = {value: i for i, value in enumerate(self.database)}
            
            build_time = time.time() - start_time
            print(f"✅ PRU Database Built in {build_time:.4f} sec. Saving to disk...")
            
            # Save the PRU database for future use
            self.save_database()

    def save_database(self):
        """Saves the PRU database and relational map to disk."""
        with open(self.save_path, "wb") as f:
            pickle.dump((self.database, self.relational_map), f)
        print("✅ PRU Database Saved Successfully!")

    def load_database(self):
        """Loads an existing PRU database from disk if available."""
        if os.path.exists(self.save_path):
            with open(self.save_path, "rb") as f:
                self.database, self.relational_map = pickle.load(f)
            print("✅ Loaded Existing PRU Database from Disk.")
        else:
            print("⚠️ No Existing PRU Database Found. Please Construct a New One.")

    def extract_index(self, value):
        """Retrieves the index dynamically through direct relational lookup."""
        return self.relational_map.get(value, -1)  # O(1) lookup

    def add_new_data(self, new_values):
        """Dynamically adds new values to PRU without full reconstruction."""
        print(f"🔄 Adding {len(new_values)} new entries to PRU...")
        start_time = time.time()

        for value in new_values:
            if value not in self.relational_map:  # Only add if it doesn't exist
                new_index = len(self.database)  # Assign the next available index
                self.database.append(value)
                self.relational_map[value] = new_index  # Update relational map

        self.save_database()  # Save updated PRU database
        update_time = time.time() - start_time
        print(f"✅ PRU Database Updated in {update_time:.4f} sec.")

# ================================
# Benchmark PRU Expansion
# ================================

# Set initial database size
initial_database_size = 10_000_000  # 10 million elements

# Initialize PRU constructor (loads or builds database)
pru = PRUConstructor(initial_database_size)

# Generate new data to be added dynamically
num_new_entries = 100_000  # Adding 100,000 new elements
new_values = list(np.random.choice(range(20_000_000, 20_100_000), num_new_entries, replace=False))

# Add new data to PRU
pru.add_new_data(new_values)

# Test search on new values
start_time = time.time()
pru_results = [pru.extract_index(value) for value in new_values]
pru_time = time.time() - start_time

# ================================
# Final Results
# ================================
results = {
    "Number of New Entries Added": num_new_entries,
    "PRU Update Time for New Entries": pru_time,
    "Search Time for New Entries (O(1))": pru_time / num_new_entries,
    "Correct Predictions": all(index != -1 for index in pru_results),
}

print(results)
