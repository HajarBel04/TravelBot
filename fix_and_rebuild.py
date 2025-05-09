#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

print("Applying fixes to the Travel RAG system (fixed version)...")

# Import and run the beach package fix
from fix_beach_package import fix_beach_package

# Import and run the extractor fix
from fix_extractor import fix_extractor

print("\n1. Fixing Beach Getaway package data...")
fix_beach_package()

print("\n2. Fixing email extractor...")
fix_extractor()

print("\n3. Fixing retriever for better package ranking...")
# Run the retriever fix
retriever_path = Path("src/retrieval/retriever.py")
if retriever_path.exists():
    # Make a backup
    backup_path = retriever_path.with_suffix('.py.bak')
    with open(retriever_path, 'r') as f:
        original_content = f.read()
        
    with open(backup_path, 'w') as f:
        f.write(original_content)

# Now run the fixed version of fix_retriever
from fix_retriever import fix_retriever
fix_retriever()

print("\n4. Rebuilding vector store...")
from rebuild_vector_store import rebuild_vector_store
rebuild_vector_store()

print("\nAll fixes applied successfully!")
print("Run 'python src/main.py' to test the improved system")