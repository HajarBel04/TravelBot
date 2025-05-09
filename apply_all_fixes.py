#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

print("Applying all fixes to the Travel RAG system...")

# Import and run each fix
from fix_beach_package import fix_beach_package
from fix_extractor import fix_extractor
from fix_retriever import fix_retriever

# Apply fixes
print("\n1. Fixing Beach Getaway package data...")
fix_beach_package()

print("\n2. Fixing email extractor...")
fix_extractor()

print("\n3. Fixing retriever for better package ranking...")
fix_retriever()

print("\n4. Rebuilding vector store with enhanced text...")
# Remove existing vector store
vector_store_path = Path("data/embeddings/vector_store.pkl")
if vector_store_path.exists():
    os.remove(vector_store_path)
    print(f"Removed existing vector store: {vector_store_path}")

# Import and run the necessary functions to rebuild
from src.main import load_travel_packages, initialize_vector_store
packages = load_travel_packages(
    "data/synthetic/enriched_travel_packages.json",
    fallback_path="data/synthetic/travel_packages.json"
)
vector_store = initialize_vector_store(packages)
print(f"Rebuilt vector store with {len(packages)} packages")

print("\nAll fixes applied successfully!")
print("Run 'python src/main.py' to test the improved system")