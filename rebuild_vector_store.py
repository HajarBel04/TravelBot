#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path
import faiss
import numpy as np

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def rebuild_vector_store():
    """Rebuild the vector store with enhanced text representations."""
    print("Rebuilding vector store with enhanced text representations...")
    
    # Try to delete existing vector store
    vector_store_path = Path("data/embeddings/vector_store.pkl")
    if vector_store_path.exists():
        os.remove(vector_store_path)
        print(f"Removed existing vector store: {vector_store_path}")
    
    # Load packages directly
    enriched_path = Path("data/synthetic/enriched_travel_packages.json")
    standard_path = Path("data/synthetic/travel_packages.json")
    
    path_to_use = enriched_path if enriched_path.exists() else standard_path
    
    with open(path_to_use, 'r') as f:
        data = json.load(f)
        packages = data.get('packages', [])
    
    print(f"Loaded {len(packages)} packages from {path_to_use}")
    
    # Import OllamaWrapper directly
    from src.generation.llm_wrapper import OllamaWrapper
    
    # Create embeddings for each package
    ollama = OllamaWrapper()
    
    print("Creating text representations and embeddings...")
    texts = []
    for package in packages:
        # Create text representation
        text = f"Package Name: {package.get('name', '')}\n"
        
        # Handle both location and destination fields
        location = package.get('location', '')
        destination = package.get('destination', '')
        text += f"Destination: {location or destination}\n"
        
        text += f"Duration: {package.get('duration', '')}\n"
        
        # Handle different price formats
        if isinstance(package.get('price'), dict):
            text += f"Price: ${package['price'].get('amount', 0)}\n"
        else:
            text += f"Price: ${package.get('price', 0)}\n"
        
        # Handle different activities formats
        activities = []
        if isinstance(package.get('activities'), list):
            for activity in package.get('activities'):
                if isinstance(activity, dict) and 'name' in activity:
                    activities.append(activity['name'])
                elif isinstance(activity, str):
                    activities.append(activity)
        
        if activities:
            text += f"Activities: {', '.join(activities)}\n"
        
        # Add enriched data if available
        if package.get('country') and package.get('country') != 'Unknown':
            text += f"Country: {package.get('country')}\n"
            
        if package.get('continent') and package.get('continent') != 'Unknown':
            text += f"Continent: {package.get('continent')}\n"
        
        # Add description - make this more prominent for better topic matching
        description = package.get('description', '')
        if description:
            text += f"Description: {description}\n"
            # Also add the description again with keywords to enhance retrieval
            text += f"Keywords: {description}\n"
        
        # Explicitly add key words for better matching
        if "beach" in description.lower() or any("beach" in act.lower() for act in activities):
            text += "Type: Beach vacation, seaside, ocean, tropical\n"
            
        if "mountain" in description.lower() or any("hik" in act.lower() for act in activities):
            text += "Type: Mountain vacation, hiking, nature, outdoor\n"
            
        if "city" in description.lower() or any("museum" in act.lower() for act in activities):
            text += "Type: City vacation, urban, sightseeing, cultural\n"
        
        texts.append(text)
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = ollama.get_embeddings(texts)
    
    # Create FAISS index
    vector_dim = len(embeddings[0])
    index = faiss.IndexFlatL2(vector_dim)
    
    # Add vectors to the index
    vectors_np = np.array(embeddings).astype('float32')
    index.add(vectors_np)
    
    # Save the index and packages
    vector_store_data = (embeddings, packages)
    
    vector_store_path.parent.mkdir(parents=True, exist_ok=True)
    with open(vector_store_path, 'wb') as f:
        import pickle
        pickle.dump(vector_store_data, f)
    
    print(f"Saved vector store with {len(packages)} packages to {vector_store_path}")
    return True

if __name__ == "__main__":
    rebuild_vector_store()