import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add the project directory to the path to make imports work
project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

from src.email_processing.extractor import EmailExtractor
from src.knowledge_base.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from enhanced_proposal_generator import ProposalGenerator
from src.generation.llm_wrapper import OllamaWrapper
from src.utils.data_cleanup import clean_country_data
from standardized_data_schema import standardize_packages, package_to_dict
from optimized_vector_store import OptimizedVectorStore
from response_caching_system import ResponseCache, DestinationCache
from rag_evaluation_metrics import RAGEvaluator
import time  # Make sure you have this import

# Initialize enhanced components
response_cache = ResponseCache(cache_dir="cache/responses")
destination_cache = DestinationCache(cache_dir="cache/destinations")
evaluator = RAGEvaluator(metrics_dir="metrics")


def load_travel_packages(file_path, fallback_path=None):
    """
    Load travel packages from a JSON file with fallback option.
    Tries enriched packages first if available.
    """
    try:
        # Try to load the primary file
        with open(file_path, 'r') as f:
            data = json.load(f)
            packages = data.get('packages', [])
            
        if packages:
            logger.info(f"Loaded {len(packages)} packages from {file_path}")
            return packages
            
        # If no packages, try the fallback path
        if fallback_path and Path(fallback_path).exists():
            logger.info(f"No packages found in {file_path}, trying fallback: {fallback_path}")
            with open(fallback_path, 'r') as f:
                data = json.load(f)
                packages = data.get('packages', [])
                
            if packages:
                logger.info(f"Loaded {len(packages)} packages from fallback {fallback_path}")
                return packages
                
        # If we get here, either no fallback was provided or it also had no packages
        if not packages:
            logger.error("No packages found in any provided paths.")
                
        return packages
    except Exception as e:
        logger.error(f"Error loading travel packages from {file_path}: {e}")
        # Try fallback if available
        if fallback_path and Path(fallback_path).exists():
            try:
                with open(fallback_path, 'r') as f:
                    data = json.load(f)
                    packages = data.get('packages', [])
                logger.info(f"Loaded {len(packages)} packages from fallback {fallback_path}")
                return packages
            except Exception as e2:
                logger.error(f"Error loading fallback packages from {fallback_path}: {e2}")
        return []

def load_example_emails(file_path):
    """Load example emails from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading example emails: {e}")
        return []

def load_llama_multitask_data(file_path):
    """Load training data from llama_multitask_val.json file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Process the data into usable formats
        extraction_examples = []
        itinerary_examples = []
        
        for item in data:
            # Extract items with task field
            if isinstance(item, dict) and item.get('task') == 'extraction':
                extraction_examples.append({
                    'input': item.get('input', ''),
                    'output': item.get('output', '')
                })
            elif isinstance(item, dict) and item.get('task') == 'generation':
                itinerary_examples.append({
                    'input': item.get('input', ''),
                    'output': item.get('output', '')
                })
            # Also process items without explicit task field but with expected output format
            elif isinstance(item, dict) and 'output' in item:
                output = item.get('output', '')
                if output.startswith('travel_date:'):
                    extraction_examples.append({
                        'input': '',  # No input in this format
                        'output': output
                    })
                elif output.startswith('# '):
                    itinerary_examples.append({
                        'input': '',  # No input in this format
                        'output': output
                    })
                
        logger.info(f"Loaded {len(extraction_examples)} extraction examples and {len(itinerary_examples)} itinerary examples from llama_multitask_val.json")
        return {
            'extraction_examples': extraction_examples,
            'itinerary_examples': itinerary_examples
        }
    except Exception as e:
        logger.error(f"Error loading llama_multitask data: {e}")
        return {'extraction_examples': [], 'itinerary_examples': []}

def initialize_vector_store(packages):
    """Initialize and populate the vector store with travel packages."""
    try:
        # Create optimized vector store
        vector_store = OptimizedVectorStore(
            store_path="data/embeddings/optimized_vector_store.pkl",
            ollama_client=OllamaWrapper()
        )
        
        # Check if vector store has documents
        if vector_store.get_documents():
            logger.info("Loaded existing vector store.")
            return vector_store
            
        # If not, create a new one
        logger.info("Creating new vector store...")
        
        # Add to vector store
        vector_store.add_documents(packages)
        logger.info(f"Created vector store with {len(packages)} packages.")
        
        return vector_store
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        return OptimizedVectorStore()  # Return empty vector store as fallback

def process_email(email_text, retriever, proposal_generator, top_k=3):
    """Process a single email and generate a proposal."""
    try:
        # Try to use cache first
        cached_result = response_cache.get(email_text)
        if cached_result:
            logger.info("Using cached response")
            return cached_result
        
        start_time = time.time()
        
        # Extract information from email
        extracted_info, packages = retriever.get_packages_from_email(email_text, top_k=top_k)
        extraction_time = time.time() - start_time
        
        # Evaluate extraction
        extraction_eval = evaluator.evaluate_extraction(email_text, extracted_info)
        
        # If no packages found and we have interests, try a more direct approach
        if not packages and extracted_info.get('interests'):
            interests = extracted_info.get('interests', '').lower()
            query = ""
            
            # Try to match specific interests with package types
            if 'beach' in interests:
                query = "beach vacation seaside ocean tropical"
            elif 'mountain' in interests or 'hiking' in interests:
                query = "mountain vacation hiking nature outdoor"
            elif 'city' in interests or 'museum' in interests:
                query = "city vacation urban sightseeing cultural"
            
            if query:
                logger.info(f"No packages found initially. Retrying with interest-based query: {query}")
                packages = retriever.retrieve_relevant_packages(query, top_k)
        
        # Fix any missing country/continent data
        if packages:
            packages = clean_country_data(packages)
        
        # Evaluate retrieval
        query = retriever.build_query(extracted_info)
        retrieval_eval = evaluator.evaluate_retrieval(query, packages)
        
        # Generate proposal
        generation_start_time = time.time()
        proposal = proposal_generator.generate_proposal(extracted_info, packages)
        generation_time = time.time() - generation_start_time
        
        # Evaluate generation
        generation_eval = evaluator.evaluate_generation(extracted_info, packages, proposal)
        
        # Evaluate end-to-end performance
        total_time = time.time() - start_time
        end_to_end_eval = evaluator.evaluate_end_to_end(email_text, proposal, total_time)
        
        # Prepare result
        result = {
            'extracted_info': extracted_info,
            'recommended_packages': packages,
            'proposal': proposal,
            'timings': {
                'extraction_ms': extraction_time * 1000,
                'generation_ms': generation_time * 1000,
                'total_ms': total_time * 1000
            }
        }
        
        # Cache the result
        response_cache.put(email_text, result)
        
        # Cache destination data
        if extracted_info.get('destination'):
            destination = extracted_info.get('destination')
            destination_data = {
                'name': destination,
                'country': next((p.get('country') for p in packages if p.get('country') != 'Unknown'), 'Unknown'),
                'continent': next((p.get('continent') for p in packages if p.get('continent') != 'Unknown'), 'Unknown'),
                'packages': [p for p in packages if p.get('location') == destination or destination in p.get('location', '')],
                'query': query
            }
            destination_cache.cache_destination_data(destination, destination_data)
        
        return result
    except Exception as e:
        logger.error(f"Error processing email: {e}")
        return {
            'error': str(e),
            'proposal': "Error generating proposal."
        }

def main():
    """Main entry point for the travel RAG system."""
    # Set paths
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data" / "synthetic"
    
    # Try to use enriched packages first, fall back to standard packages
    enriched_packages_path = data_dir / "enriched_travel_packages.json"
    standard_packages_path = data_dir / "travel_packages.json"
    
    emails_path = data_dir / "emails.json"
    
    # Path to the llama_multitask_val.json file in the project root
    llama_data_path = base_dir.parent / "llama_multitask_val.json"
    
    logger.info("Starting Travel RAG System...")
    
    # Check if Ollama is running
    try:
        ollama = OllamaWrapper()
        # Test connection with a simple query
        ollama.generate("Hello", "Test connection")
        logger.info("Successfully connected to Ollama")
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {e}")
        logger.error("Make sure Ollama is installed and running on http://localhost:11434")
        sys.exit(1)
    
    # Load data - try enriched packages first, fall back to standard
    packages = load_travel_packages(
        enriched_packages_path, 
        fallback_path=standard_packages_path
    )
    
    if not packages:
        logger.error("No travel packages found. Cannot continue.")
        sys.exit(1)
    logger.info(f"Loaded {len(packages)} travel packages.")
    
    emails = load_example_emails(emails_path)
    if not emails:
        logger.warning("No example emails found.")
    else:
        logger.info(f"Loaded {len(emails)} example emails.")
    
    # Load the llama_multitask_val.json data if available
    llama_data = None
    if llama_data_path.exists():
        llama_data = load_llama_multitask_data(llama_data_path)
        logger.info("Loaded llama_multitask_val.json data.")
    else:
        logger.warning(f"Llama multitask data not found at {llama_data_path}. Continuing without it.")
    
    # Initialize vector store
    vector_store = initialize_vector_store(packages)
    
    # Create retriever and proposal generator
    retriever = Retriever(vector_store)
    proposal_generator = ProposalGenerator()
    
    # Update example email to be more specific about beach
    if emails and emails[0].get('subject') == "Looking for a family vacation":
        # The original email asks for beach destinations but doesn't emphasize it enough
        # Let's make it clearer for testing
        enhanced_email = """
        Hi, I'm planning a family beach vacation for next summer. We want to enjoy sun, sand, and
        beautiful beaches. We are interested in beach destinations that include activities for kids.
        Our budget is around $3000. Please send me some beach vacation options.
        """
        
        logger.info("Using enhanced beach vacation email for testing")
        example_email = enhanced_email
    else:
        # Use the original email
        example_email = emails[0].get('body', 'This is a test email.') if emails else "This is a test email."
        logger.info(f"Processing example email with subject: {emails[0].get('subject', 'Unknown') if emails else 'No subject'}")
    
    # Process the email
    result = process_email(example_email, retriever, proposal_generator)
    
    # Print extracted info
    logger.info("\n=== Extracted Information ===")
    for key, value in result['extracted_info'].items():
        logger.info(f"{key}: {value}")
        
    # Print packages
    logger.info("\n=== Retrieved Packages ===")
    for i, pkg in enumerate(result['recommended_packages']):
        logger.info(f"Package {i+1}: {pkg.get('name')} - {pkg.get('location') or pkg.get('destination')} - " + 
                   (f"${pkg.get('price')}" if isinstance(pkg.get('price'), (int, float)) else
                    f"${pkg['price'].get('amount')}" if isinstance(pkg.get('price'), dict) else "No price"))
            
    # Print proposal
    logger.info("\n=== Generated Proposal ===")
    logger.info(result['proposal'])
    
    # If we have llama data, test with an example from it
    if llama_data and llama_data['extraction_examples']:
        logger.info("\n\n=== Testing with Llama Multitask Data ===")
        example = llama_data['extraction_examples'][0]
        if example.get('input'):
            logger.info(f"Processing example email from llama dataset")
            result = process_email(example['input'], retriever, proposal_generator)
            
            # Print extracted info
            logger.info("\n=== Extracted Information from Llama Data ===")
            for key, value in result['extracted_info'].items():
                logger.info(f"{key}: {value}")
                
            # Print proposal
            logger.info("\n=== Generated Proposal from Llama Data ===")
            logger.info(result['proposal'])
    
    # Set baseline metrics for future comparison
    evaluator.set_as_baseline()
    logger.info("Set current performance as baseline for future comparisons")
    
    # Show cache statistics
    logger.info("\n=== Cache Statistics ===")
    logger.info(f"Response cache entries: {len(response_cache.cache)}")
    logger.info(f"Destination cache entries: {len(destination_cache.destinations)}")
    
    
    logger.info("Travel RAG System initialized successfully.")
    logger.info("You can now process emails and generate proposals.")

if __name__ == "__main__":
    main()