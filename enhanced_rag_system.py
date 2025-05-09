#!/usr/bin/env python3
import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add the project directory to the path to make imports work
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

# Import standard components
from src.email_processing.extractor import EmailExtractor
from src.generation.llm_wrapper import OllamaWrapper

# Import enhanced components
from optimized_vector_store import OptimizedVectorStore
from standardized_data_schema import TravelPackage, standardize_packages, package_to_dict
from enhanced_proposal_generator import ProposalGenerator
from response_caching_system import ResponseCache, DestinationCache, process_with_cache
from rag_evaluation_metrics import RAGEvaluator

class EnhancedTravelRAG:
    """Enhanced Travel RAG system with improved performance and metrics."""
    
    def __init__(self):
        """Initialize the enhanced RAG system."""
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all components of the RAG system."""
        logger.info("Initializing enhanced RAG components...")
        
        # Initialize paths
        self.data_dir = project_dir / "data"
        self.cache_dir = project_dir / "cache"
        self.metrics_dir = project_dir / "metrics"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Ollama client
        self.ollama = OllamaWrapper()
        self._test_ollama_connection()
        
        # Initialize enhanced vector store
        self.vector_store = OptimizedVectorStore(
            store_path=str(self.data_dir / "embeddings" / "optimized_vector_store.pkl"),
            ollama_client=self.ollama
        )
        
        # Initialize email extractor
        self.extractor = EmailExtractor(ollama_client=self.ollama)
        
        # Initialize enhanced proposal generator
        self.proposal_generator = ProposalGenerator(ollama_client=self.ollama)
        
        # Initialize caching
        self.response_cache = ResponseCache(
            cache_dir=str(self.cache_dir / "responses"),
            max_size=1000,
            ttl_seconds=86400 * 7  # 7 days
        )
        
        self.destination_cache = DestinationCache(
            cache_dir=str(self.cache_dir / "destinations"),
            ttl_days=30  # 30 days
        )
        
        # Initialize evaluator
        self.evaluator = RAGEvaluator(metrics_dir=str(self.metrics_dir))
        
        # Load travel packages
        self.load_travel_packages()
        
        logger.info("Enhanced RAG system initialized successfully")
        
    def _test_ollama_connection(self):
        """Test the connection to Ollama."""
        try:
            response = self.ollama.generate("Test connection", "This is a test")
            logger.info("Successfully connected to Ollama")
        except Exception as e:
            logger.error(f"Error connecting to Ollama: {e}")
            logger.error("Make sure Ollama is installed and running on http://localhost:11434")
            sys.exit(1)
    
    def load_travel_packages(self):
        """Load travel packages from files and prepare the vector store."""
        # Try to load enriched packages first, fall back to standard packages
        enriched_path = self.data_dir / "synthetic" / "enriched_travel_packages.json"
        standard_path = self.data_dir / "synthetic" / "travel_packages.json"
        
        packages_path = enriched_path if enriched_path.exists() else standard_path
        
        try:
            with open(packages_path, 'r') as f:
                data = json.load(f)
                raw_packages = data.get('packages', [])
                
            logger.info(f"Loaded {len(raw_packages)} packages from {packages_path}")
            
            # Standardize packages
            self.packages = standardize_packages(raw_packages)
            logger.info(f"Standardized {len(self.packages)} packages")
            
            # Check if vector store has data
            if not self.vector_store.get_documents():
                logger.info("Vector store is empty, adding packages...")
                
                # Convert standardized packages back to dictionaries for vector store
                package_dicts = [package_to_dict(package) for package in self.packages]
                
                # Add to vector store
                self.vector_store.add_documents(package_dicts)
                logger.info(f"Added {len(package_dicts)} packages to vector store")
            else:
                logger.info(f"Vector store already contains {len(self.vector_store.get_documents())} documents")
                
        except Exception as e:
            logger.error(f"Error loading packages: {e}")
            self.packages = []
            logger.warning("Continuing with empty package list")
    
    def build_query(self, extracted_info):
        """
        Build a search query from extracted email information.
        
        Args:
            extracted_info: Dictionary with extracted information
            
        Returns:
            str: A query string
        """
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
    
    def retrieve_packages(self, query, top_k=3):
        """
        Retrieve relevant packages based on the query.
        
        Args:
            query: The search query
            top_k: Number of packages to retrieve
            
        Returns:
            List of relevant packages
        """
        # Use optimized vector store for retrieval
        results = self.vector_store.similarity_search(query, k=top_k*2)  # Get more results to rerank
        
        # Extract documents
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
                    for activity in doc.get('activities'):
                        if isinstance(activity, dict) and 'name' in activity:
                            activities.append(activity['name'].lower())
                        elif isinstance(activity, str):
                            activities.append(activity.lower())
                
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
    
    def process_email(self, email_text, force_refresh=False, evaluate=True):
        """
        Process an email and generate a proposal with caching and evaluation.
        
        Args:
            email_text: The email text to process
            force_refresh: Force processing even if cached
            evaluate: Whether to evaluate performance
            
        Returns:
            Dict with extracted info, recommended packages, and proposal
        """
        # Try to use cache first
        if not force_refresh:
            cached_result = self.response_cache.get(email_text)
            if cached_result:
                logger.info("Using cached response")
                return cached_result
        
        start_time = time.time()
        
        # Extract information from email and evaluate
        extracted_info = self.extractor.extract_from_email(email_text)
        extraction_time = time.time() - start_time
        
        if evaluate:
            extraction_eval = self.evaluator.evaluate_extraction(email_text, extracted_info)
            logger.info(f"Extraction completeness: {extraction_eval['metrics']['extraction_completeness']:.2f}")
        
        # Build query
        query = self.build_query(extracted_info)
        
        # Retrieve packages and evaluate
        query_start_time = time.time()
        packages = self.retrieve_packages(query, top_k=3)
        retrieval_time = time.time() - query_start_time
        
        if evaluate:
            retrieval_eval = self.evaluator.evaluate_retrieval(query, packages)
            logger.info(f"Retrieved {len(packages)} packages with diversity: {retrieval_eval['metrics']['location_diversity']:.2f}")
        
        # Fix any missing country/continent data
        for package in packages:
            if package.get('country') == 'Unknown' and package.get('location'):
                # Try to determine country from destination cache
                cached_dest = self.destination_cache.get_destination_data(package.get('location'))
                if cached_dest and 'country' in cached_dest.data:
                    package['country'] = cached_dest.data['country']
                    package['continent'] = cached_dest.data.get('continent', 'Unknown')
        
        # Generate proposal and evaluate
        generation_start_time = time.time()
        proposal = self.proposal_generator.generate_proposal(extracted_info, packages)
        generation_time = time.time() - generation_start_time
        
        total_time = time.time() - start_time
        
        if evaluate:
            generation_eval = self.evaluator.evaluate_generation(extracted_info, packages, proposal)
            end_to_end_eval = self.evaluator.evaluate_end_to_end(email_text, proposal, total_time)
            
            logger.info(f"Generation quality: {generation_eval['metrics']['quality_score']:.2f}")
            logger.info(f"Total processing time: {total_time:.2f}s")
        
        # Prepare response
        result = {
            'extracted_info': extracted_info,
            'recommended_packages': packages,
            'proposal': proposal,
            'timings': {
                'extraction_ms': extraction_time * 1000,
                'retrieval_ms': retrieval_time * 1000,
                'generation_ms': generation_time * 1000,
                'total_ms': total_time * 1000
            }
        }
        
        # Cache the result
        self.response_cache.put(email_text, result)
        
        # Cache destination data
        if extracted_info.get('destination'):
            destination = extracted_info.get('destination')
            destination_data = {
                'name': destination,
                'country': next((p.get('country') for p in packages if p.get('country') != 'Unknown'), 'Unknown'),
                'continent': next((p.get('continent') for p in packages if p.get('continent') != 'Unknown'), 'Unknown'),
                'packages': packages,
                'query': query
            }
            self.destination_cache.cache_destination_data(destination, destination_data)
        
        return result
    
    def get_system_stats(self):
        """Get statistics about the system."""
        return {
            'vector_store': self.vector_store.get_statistics(),
            'response_cache': self.response_cache.get_statistics(),
            'destination_cache': {
                'destinations': self.destination_cache.get_all_destinations(),
                'count': len(self.destination_cache.destinations)
            },
            'packages': {
                'total': len(self.packages),
                'beach_packages': sum(1 for p in self.packages if 'beach' in p.name.lower()),
                'mountain_packages': sum(1 for p in self.packages if 'mountain' in p.name.lower()),
                'city_packages': sum(1 for p in self.packages if 'city' in p.name.lower())
            }
        }
    
    def get_performance_report(self):
        """Get a performance report of the system."""
        return self.evaluator.get_summary_report()


# Runnable script for testing
if __name__ == "__main__":
    # Initialize the enhanced RAG system
    enhanced_rag = EnhancedTravelRAG()
    
    # Test email
    test_email = """
    Hi, I'm planning a family beach vacation for next summer. We want to enjoy sun, sand, and
    beautiful beaches. We are interested in beach destinations that include activities for kids.
    Our budget is around $3000. Please send me some beach vacation options.
    """
    
    print("\n--- Testing Enhanced RAG System ---\n")
    
    # Process the email
    result = enhanced_rag.process_email(test_email)
    
    # Print extracted info
    print("\n=== Extracted Information ===")
    for key, value in result['extracted_info'].items():
        if key not in ['timestamp', 'text'] and value:
            print(f"{key}: {value}")
        
    # Print packages
    print("\n=== Retrieved Packages ===")
    for i, pkg in enumerate(result['recommended_packages']):
        print(f"Package {i+1}: {pkg.get('name')} - {pkg.get('location') or pkg.get('destination')}")
            
    # Print proposal (first 500 chars)
    print("\n=== Generated Proposal ===")
    print(result['proposal'][:500] + "...")
    
    # Print performance stats
    print("\n=== Performance Statistics ===")
    for component, timing in result['timings'].items():
        print(f"{component}: {timing:.2f} ms")
    
    # Process the same email again (should use cache)
    print("\n--- Processing same email again (testing cache) ---")
    cache_start = time.time()
    cached_result = enhanced_rag.process_email(test_email)
    cache_time = time.time() - cache_start
    print(f"Cache retrieval time: {cache_time*1000:.2f} ms")
    
    # Get system stats
    print("\n=== System Statistics ===")
    stats = enhanced_rag.get_system_stats()
    print(f"Vector store documents: {stats['vector_store']['document_count']}")
    print(f"Response cache entries: {stats['response_cache']['total_entries']}")
    print(f"Cached destinations: {stats['destination_cache']['count']}")
    
    # Add this as the baseline for future comparisons
    enhanced_rag.evaluator.set_as_baseline()
    print("\nSet current performance as baseline for future comparisons")
    
    print("\nEnhanced RAG system test completed!")