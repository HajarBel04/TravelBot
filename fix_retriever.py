#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def fix_retriever():
    """Fix the retriever to prioritize beach packages for beach vacation queries."""
    
    retriever_path = Path("src/retrieval/retriever.py")
    if not retriever_path.exists():
        print(f"Error: Cannot find retriever file at {retriever_path}")
        return False
    
    # Instead of trying to patch the existing file which resulted in syntax errors,
    # let's replace the entire file with a correct version
    
    new_content = """import logging
from src.email_processing.extractor import EmailExtractor
from src.knowledge_base.vector_store import VectorStore

logger = logging.getLogger(__name__)

class Retriever:
    \"\"\"Retrieves relevant travel packages based on customer needs.\"\"\"
    
    def __init__(self, vector_store=None):
        \"\"\"Initialize the retriever with a vector store.\"\"\"
        self.vector_store = vector_store or VectorStore()
        
    def build_query(self, extracted_info):
        \"\"\"
        Build a search query from extracted email information.
        
        Args:
            extracted_info: Dictionary with extracted information
            
        Returns:
            str: A query string
        \"\"\"
        query_parts = []
        
        # Add destination if available
        if extracted_info.get('destination'):
            query_parts.append(f"destination: {extracted_info['destination']}")
        
        # Check for specific interests or travel types
        interests = ""
        if extracted_info.get('interests'):
            interests = extracted_info['interests'].lower()
        
        travel_type = ""
        if extracted_info.get('travel_type'):
            travel_type = extracted_info['travel_type'].lower()
            
        # Emphasize beach/mountain/city preferences based on interests and travel type
        if 'beach' in interests or 'beach' in travel_type:
            query_parts.append("type: beach vacation seaside ocean tropical")
        elif 'mountain' in interests or 'hik' in interests or 'mountain' in travel_type:
            query_parts.append("type: mountain vacation hiking nature outdoor")
        elif 'city' in interests or 'museum' in interests or 'city' in travel_type:
            query_parts.append("type: city vacation urban sightseeing cultural")
        elif interests:
            query_parts.append(f"interests: {interests}")
        
        # Add budget if available
        if extracted_info.get('budget'):
            query_parts.append(f"budget: {extracted_info['budget']}")
            
        # Add traveler info if available
        if extracted_info.get('travelers'):
            query_parts.append(f"travelers: {extracted_info['travelers']}")
        
        # Add dates if available
        if extracted_info.get('dates'):
            query_parts.append(f"dates: {extracted_info['dates']}")
        
        # Join all parts with spaces
        query = " ".join(query_parts)
        
        # If query is empty, use a fallback
        if not query:
            query = "travel package"
            
        return query
    
    def retrieve_relevant_packages(self, query, top_k=3):
        \"\"\"
        Retrieve relevant travel packages based on the query.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            list: List of relevant travel packages
        \"\"\"
        results = self.vector_store.similarity_search(query, k=top_k*2)  # Get more results to rerank
        
        # Extract documents and scores
        doc_score_pairs = results
        
        # Check if we're looking for a specific type of vacation
        is_beach_query = 'beach' in query.lower() or 'seaside' in query.lower() or 'ocean' in query.lower()
        is_mountain_query = 'mountain' in query.lower() or 'hiking' in query.lower() or 'nature' in query.lower()
        is_city_query = 'city' in query.lower() or 'urban' in query.lower() or 'museum' in query.lower()
        
        if is_beach_query or is_mountain_query or is_city_query:
            # Re-rank results based on vacation type
            reranked_results = []
            
            for doc, score in doc_score_pairs:
                # Check package type
                name = doc.get('name', '').lower()
                description = doc.get('description', '').lower()
                
                # Get activities
                activities = []
                if isinstance(doc.get('activities'), list):
                    for act in doc.get('activities'):
                        if isinstance(act, dict) and 'name' in act:
                            activities.append(act['name'].lower())
                        elif isinstance(act, str):
                            activities.append(act.lower())
                
                # Calculate type match score
                type_boost = 0
                
                if is_beach_query:
                    if 'beach' in name or 'beach' in description:
                        type_boost = 0.5
                    elif any('beach' in act for act in activities):
                        type_boost = 0.3
                        
                elif is_mountain_query:
                    if 'mountain' in name or 'mountain' in description:
                        type_boost = 0.5
                    elif any(('hik' in act or 'mountain' in act) for act in activities):
                        type_boost = 0.3
                        
                elif is_city_query:
                    if 'city' in name or 'city' in description:
                        type_boost = 0.5
                    elif any(('museum' in act or 'sight' in act) for act in activities):
                        type_boost = 0.3
                
                # Apply boost
                reranked_results.append((doc, score + type_boost))
            
            # Sort by new score
            reranked_results.sort(key=lambda x: x[1], reverse=True)
            
            # Take top_k results
            packages = [doc for doc, _ in reranked_results[:top_k]]
        else:
            # Just take top results without reranking
            packages = [doc for doc, _ in doc_score_pairs[:top_k]]
        
        return packages
    
    def get_packages_from_email(self, email_text, top_k=3):
        \"\"\"
        Process an email and retrieve relevant packages.
        
        Args:
            email_text: The customer email text
            top_k: Number of packages to retrieve
            
        Returns:
            tuple: (extracted_info, packages)
        \"\"\"
        # Extract information from email
        extractor = EmailExtractor()
        extracted_info = extractor.extract_from_email(email_text)
        
        # Build search query
        query = self.build_query(extracted_info)
        
        # Retrieve packages
        packages = self.retrieve_relevant_packages(query, top_k=top_k)
        
        return extracted_info, packages
"""
    
    # Make a backup of the original file
    backup_path = retriever_path.with_suffix('.py.bak2')
    with open(retriever_path, 'r') as f:
        original_content = f.read()
        
    with open(backup_path, 'w') as f:
        f.write(original_content)
        
    # Write the new content
    with open(retriever_path, 'w') as f:
        f.write(new_content)
        
    print(f"Completely replaced retriever.py with fixed version")
    print(f"Backup saved to {backup_path}")
    return True

if __name__ == "__main__":
    fix_retriever()