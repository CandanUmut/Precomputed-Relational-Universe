import numpy as np
import networkx as nx
import pickle
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from tqdm import tqdm
from Bio.PDB import PDBParser  # For protein structure handling

# ================================
# 1️⃣ PRU Chemistry Knowledge Storage
# ================================

class PRU_Chemistry_DB:
    def __init__(self, storage_file="pru_chemistry_db.pkl"):
        self.graph = nx.Graph()
        self.entity_map = {}  # Stores relations
        self.storage_file = storage_file
        self.load_data()

    # ========= Periodic Table Storage =========
    def store_periodic_table(self):
        """Stores periodic table elements with atomic properties"""
        periodic_data = pd.DataFrame([
            ("H", 1.008, 1), ("He", 4.0026, 2), ("Li", 6.94, 3), ("Be", 9.0122, 4), ("B", 10.81, 5),
            ("C", 12.011, 6), ("N", 14.007, 7), ("O", 15.999, 8), ("F", 18.998, 9), ("Ne", 20.180, 10),
            ("Na", 22.990, 11), ("Mg", 24.305, 12), ("Al", 26.982, 13), ("Si", 28.085, 14), ("P", 30.974, 15),
            ("S", 32.06, 16), ("Cl", 35.45, 17), ("Ar", 39.948, 18), ("K", 39.098, 19), ("Ca", 40.078, 20),
        ], columns=["Element", "AtomicMass", "AtomicNumber"])

        for _, row in periodic_data.iterrows():
            self._add_entity(row["Element"], {"AtomicMass": row["AtomicMass"], "AtomicNumber": row["AtomicNumber"]})

        print(f"✅ Stored {len(periodic_data)} elements in PRU-DB.")

    # ========= Molecule Storage & Analysis =========
    def store_molecule(self, smiles, label):
        """Stores a molecule using its SMILES representation"""
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"⚠️ Invalid SMILES: {smiles}")
            return
        
        molecular_weight = Descriptors.MolWt(mol)
        num_atoms = mol.GetNumAtoms()
        elements = {atom.GetSymbol() for atom in mol.GetAtoms()}

        # Store molecule relations
        self._add_entity(label, {
            "SMILES": smiles,
            "MolecularWeight": molecular_weight,
            "NumAtoms": num_atoms,
            "Elements": list(elements)
        })

        print(f"✅ Stored molecule '{label}' ({smiles}) in PRU-DB.")

    # ========= Protein Structure Storage =========
    def store_protein(self, pdb_path, label):
        """Extracts amino acid relations from a PDB file and stores it"""
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure(label, pdb_path)

        residues = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    res_name = residue.get_resname()
                    if res_name not in residues:
                        residues.append(res_name)

        self._add_entity(label, {"Residues": residues})
        print(f"✅ Stored protein '{label}' with {len(residues)} unique residues.")

    # ========= Generate New Molecular Structures =========
    def generate_new_molecule(self, base_molecule, new_label):
        """Generates a new molecule based on relational variations of a given molecule"""
        related_entities = self.lookup(base_molecule)

        # Ensure we have related molecules
        if not related_entities:
            print(f"⚠️ No related molecules found for '{base_molecule}'.")
            return None

        base_data = self.entity_map.get(base_molecule, {})
        if "Elements" not in base_data:
            print(f"⚠️ Cannot generate a new molecule from '{base_molecule}'.")
            return None

        # Modify molecule elements slightly
        new_elements = base_data["Elements"][:]
        if len(new_elements) > 1:
            new_elements[0] = "Si"  # Replace an atom with Silicon to test new structure

        # Create new molecule
        new_smiles = "".join(new_elements) + "O"  # Example modification
        self._add_entity(new_label, {"SMILES": new_smiles, "DerivedFrom": base_molecule})

        print(f"🧪 New molecule '{new_label}' generated with relation to '{base_molecule}'.")
        return new_label

    # ========= Core PRU Relational System =========
    def _add_entity(self, entity, relations):
        """Generalized method to add knowledge into PRU."""
        if entity not in self.entity_map:
            self.entity_map[entity] = relations

        for rel_key, rel_value in relations.items():
            rel_str = f"{rel_key}:{rel_value}"
            if rel_str not in self.entity_map:
                self.entity_map[rel_str] = {}
            self.graph.add_edge(entity, rel_str, weight=1)

        self.save_data()

    def lookup(self, entity):
        """Retrieve related knowledge instantly."""
        return list(self.graph.neighbors(entity)) if entity in self.graph else []

    def save_data(self):
        """Persist PRU-DB to disk."""
        with open(self.storage_file, "wb") as f:
            pickle.dump((self.graph, self.entity_map), f)

    def load_data(self):
        """Load existing PRU-DB if available."""
        try:
            with open(self.storage_file, "rb") as f:
                self.graph, self.entity_map = pickle.load(f)
            print("✅ Loaded PRU Chemistry DB from Storage.")
        except FileNotFoundError:
            print("⚠️ No existing PRU-DB found. Starting fresh.")

# ================================
# 2️⃣ Running PRU Chemistry DB
# ================================

if __name__ == "__main__":
    pru_chem = PRU_Chemistry_DB()

    # Store Periodic Table
    pru_chem.store_periodic_table()

    # Store Molecules (Water, Glucose, Aspirin)
    pru_chem.store_molecule("O", "Oxygen")
    pru_chem.store_molecule("H2O", "Water")
    pru_chem.store_molecule("C6H12O6", "Glucose")
    pru_chem.store_molecule("CC(=O)OC1=CC=CC=C1C(=O)O", "Aspirin")

    # Store Protein (Example PDB file)
    pru_chem.store_protein("example_protein.pdb", "Example_Protein")

    # Generate a new molecule
    new_molecule = pru_chem.generate_new_molecule("Water", "Modified_Water")

    # Lookup an element
    print("\n🔎 Lookup: Oxygen →", pru_chem.lookup("Oxygen"))
