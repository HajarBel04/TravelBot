#!/usr/bin/env python3

import os
import sys
import json
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.generation.llm_wrapper import OllamaWrapper
from src.email_processing.extractor import EmailExtractor
from src.retrieval.retriever import Retriever
from src.generation.proposal_generator import ProposalGenerator
from src.knowledge_base.vector_store import VectorStore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def test_ollama_connection():
    """Test if Ollama is running and the required models are available."""
    try:
        # Test basic generation
        ollama = OllamaWrapper()
        response = ollama.generate("Hello, this is a test.", "Test connection")
        logger.info(f"Ollama generation test successful. Response: {response[:50]}...")
        
        # Test if embedding model is working
        try:
            embedding = ollama.get_embeddings("This is a test embedding.")
            embedding_size = len(embedding)
            logger.info(f"Ollama embedding test successful. Embedding size: {embedding_size}")
            return True
        except Exception as e:
            logger.error(f"Ollama embedding test failed: {e}")
            logger.error("Make sure the embedding model is available. Try running: ollama pull nomic-embed-text")
            return False
    except Exception as e:
        logger.error(f"Ollama connection test failed: {e}")
        logger.error("Make sure Ollama is installed and running on http://localhost:11434")
        return False

def process_sample_email():
    """Process a sample email without using vector search."""
    try:
        # Load travel packages directly
        enriched_file = project_root / "data" / "synthetic" / "enriched_travel_packages.json"
        standard_file = project_root / "data" / "synthetic" / "travel_packages.json"
        
        # Try to load enriched packages first, fall back to standard packages
        if enriched_file.exists():
            with open(enriched_file, 'r') as f:
                data = json.load(f)
                packages = data.get('packages', [])
            logger.info(f"Loaded {len(packages)} enriched packages")
        else:
            with open(standard_file, 'r') as f:
                data = json.load(f)
                packages = data.get('packages', [])
            logger.info(f"Loaded {len(packages)} standard packages (enriched packages not found)")
        
        # Use a sample email
        sample_email = """
        Hi, I'm planning a family vacation to the Maldives next month. We are two adults and two children (ages 8 and 10). 
        We are looking for a beach resort with kids activities. Our budget is around $5000 for a week-long trip. 
        We enjoy snorkeling and water sports. Could you recommend some options?
        """
        
        # Extract information from the email
        extractor = EmailExtractor()
        extracted_info = extractor.extract_from_email(sample_email)
        
        # Print extracted information
        logger.info("Extracted information from email:")
        for key, value in extracted_info.items():
            logger.info(f"  {key}: {value}")
        
        # Manually select relevant packages (skipping vector search)
        relevant_packages = []
        for package in packages:
            # Simple keyword matching for beach-related packages
            if ("beach" in package.get('name', '').lower() or 
                "beach" in package.get('description', '').lower() or
                "maldives" in package.get('location', '').lower()):
                relevant_packages.append(package)
                
        # Use at least one package if none matched
        if not relevant_packages and packages:
            relevant_packages = [packages[0]]
            
        # Print selected packages
        logger.info("\nSelected packages:")
        for pkg in relevant_packages:
            logger.info(f"  {pkg.get('name')} - {pkg.get('location') or pkg.get('destination')} - ${pkg.get('price') if isinstance(pkg.get('price'), (int, float)) else pkg.get('price', {}).get('amount') if isinstance(pkg.get('price'), dict) else 'Unknown'}")
            
            # Show enriched data if available
            if pkg.get('country') and pkg.get('country') != 'Unknown':
                logger.info(f"    Country: {pkg.get('country')}, Continent: {pkg.get('continent')}")
            if pkg.get('weather_data'):
                logger.info(f"    Weather data available: Yes")
            if isinstance(pkg.get('activities'), list) and any(isinstance(act, dict) for act in pkg.get('activities', [])):
                activities = [act.get('name') for act in pkg.get('activities') if isinstance(act, dict) and 'name' in act]
                logger.info(f"    Enriched activities: {', '.join(activities[:3])}" + ("..." if len(activities) > 3 else ""))
        
        # Generate proposal
        proposal_generator = ProposalGenerator()
        proposal = proposal_generator.generate_proposal(extracted_info, relevant_packages)
        
        # Print proposal
        logger.info("\nGenerated proposal:")
        logger.info(proposal[:500] + "..." if len(proposal) > 500 else proposal)
        
        # Check if proposal contains enriched information
        enriched_indicators = [
            'weather', 'temperature', 'forecast',
            'country', 'local', 'currency',
            'attractions', 'activities'
        ]
        
        found_indicators = []
        for indicator in enriched_indicators:
            if indicator in proposal.lower():
                found_indicators.append(indicator)
        
        if found_indicators:
            logger.info(f"\nProposal contains enriched information: {', '.join(found_indicators)}")
        else:
            logger.warning("\nProposal does not contain any enriched information indicators")
        
        return True
    except Exception as e:
        logger.error(f"Error processing sample email: {e}")
        return False

def test_with_vector_search():
    """Test the full RAG pipeline with vector search."""
    try:
        # Initialize vector store
        vector_store = VectorStore()
        if not vector_store.load():
            logger.warning("Vector store could not be loaded. Test will run with reduced functionality.")
            return False
        
        # Initialize retriever
        retriever = Retriever(vector_store)
        
        # Sample email for mountain vacation
        sample_email = """
        Hello,
        I'm planning a mountain adventure in the Swiss Alps for next month. We're a couple interested in 
        hiking and outdoor activities. Our budget is around $3000 for a 7-day trip.
        We'd like to stay in a nice chalet with good views.
        Thank you!
        """
        
        # Extract information
        extractor = EmailExtractor()
        extracted_info = extractor.extract_from_email(sample_email)
        
        logger.info("Extracted information from mountain email:")
        for key, value in extracted_info.items():
            logger.info(f"  {key}: {value}")
        
        # Build query and retrieve packages
        query = retriever.build_query(extracted_info)
        logger.info(f"Generated query: {query}")
        
        packages = retriever.retrieve_relevant_packages(query, top_k=3)
        
        logger.info(f"Retrieved {len(packages)} packages from vector store")
        for i, pkg in enumerate(packages):
            logger.info(f"Package {i+1}: {pkg.get('name')}")
            logger.info(f"  Location: {pkg.get('location', pkg.get('destination', 'Unknown'))}")
            if pkg.get('country'):
                logger.info(f"  Country: {pkg.get('country')}")
            if pkg.get('weather_data'):
                logger.info(f"  Weather data: Available")
        
        # Generate proposal
        proposal_generator = ProposalGenerator()
        proposal = proposal_generator.generate_proposal(extracted_info, packages)
        
        logger.info("\nGenerated proposal with vector search:")
        logger.info(proposal[:500] + "..." if len(proposal) > 500 else proposal)
        
        return True
    except Exception as e:
        logger.error(f"Error testing vector search: {e}")
        return False

if __name__ == "__main__":
    logger.info("Testing Ollama connection...")
    if test_ollama_connection():
        logger.info("Ollama connection test passed!")
        
        logger.info("\nProcessing a sample email without vector search...")
        if process_sample_email():
            logger.info("Sample email processed successfully!")
        else:
            logger.error("Failed to process sample email.")
        
        logger.info("\nTesting the full RAG pipeline with vector search...")
        if test_with_vector_search():
            logger.info("Vector search test completed successfully!")
        else:
            logger.warning("Vector search test completed with issues.")
    else:
        logger.error("Ollama connection test failed. Please check if Ollama is running.")