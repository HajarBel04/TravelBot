#!/usr/bin/env python3

import os
import sys
import logging
import argparse
from pathlib import Path
from src.utils.data_cleanup import clean_country_data


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Enhance Travel RAG System Data Sources')
    parser.add_argument('--mode', choices=['all', 'collect', 'process', 'enrich', 'import'], default='all',
                      help='Mode of operation')
    parser.add_argument('--limit', type=int, default=20,
                      help='Limit for number of items to collect')
    parser.add_argument('--input', type=str,
                      help='Input file for processing or importing')
    parser.add_argument('--output', type=str,
                      help='Output file for saving results')
    
    args = parser.parse_args()
    
    # Add the project root to Python path
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))
    
    # Import project modules
    from src.config import Config
    from scripts.collect_travel_data import collect_and_enrich_data, manually_enrich_destinations, get_popular_destinations
    from scripts.batch_process_data import batch_process_all_data, process_package_file
    from src.knowledge_base.enrichment import DataEnrichmentPipeline
    from src.knowledge_base.enhanced_vector_store import EnhancedVectorStore
    from src.utils.data_io import load_json_packages, save_json_packages
    
    # Initialize paths
    Config.initialize_paths()
    
    # Default file paths
    input_file = args.input or os.path.join(Config.DATA_SOURCES["synthetic_dir"], "travel_packages.json")
    output_file = args.output or Config.DATA_SOURCES["enriched_file"]
    
    # Execute based on mode
    if args.mode == 'all' or args.mode == 'collect':
        logger.info("Collecting data from web sources...")
        
        # Collect from both UNESCO and WikiTravel
        collect_and_enrich_data(
            output_file=os.path.join(Config.DATA_SOURCES["sources_dir"], "collected_packages.json"),
            sources=["unesco", "wikitravel"],
            limit=args.limit
        )
        
        # Collect from manual destinations
        destinations = get_popular_destinations(args.limit)
        manually_enrich_destinations(
            destinations,
            os.path.join(Config.DATA_SOURCES["sources_dir"], "manual_packages.json")
        )
    
    if args.mode == 'all' or args.mode == 'process':
        logger.info("Processing data files...")
        
        # Process all data in the sources directory
        batch_process_all_data(
            Config.DATA_SOURCES["sources_dir"],
            Config.DATA_SOURCES["processed_dir"],
            Config.DB_PATH
        )
    
    if args.mode == 'all' or args.mode == 'enrich':
        logger.info("Enriching existing data...")
        
        # Enrich the existing travel_packages.json file
        if os.path.exists(input_file):
            # Load packages
            packages = load_json_packages(input_file)
            
            if packages:
                # Enrich packages
                enrichment = DataEnrichmentPipeline()
                enriched_packages = []
                
                for package in packages:
                    try:
                        enriched = enrichment.enrich_package(package)
                        enriched_packages.append(enriched)
                    except Exception as e:
                        logger.error(f"Error enriching package {package.get('name', 'unknown')}: {e}")
                
                # Save enriched packages
                save_json_packages(enriched_packages, output_file)
                cleaned_packages = clean_country_data(enriched_packages)
                if cleaned_packages:
                    logger.info(f"Saving cleaned packages with fixed country/continent data")
                    save_json_packages(cleaned_packages, output_file)
                logger.info(f"Enriched {len(enriched_packages)} packages from {input_file}")
            else:
                logger.warning(f"No packages found in {input_file}")
        else:
            logger.warning(f"Input file {input_file} not found")
    
    if args.mode == 'all' or args.mode == 'import':
        logger.info("Importing data to vector store...")
        
        # Import the enriched data to the vector store
        enriched_file = Config.DATA_SOURCES["enriched_file"]
        if os.path.exists(enriched_file):
            # Load enriched packages
            packages = load_json_packages(enriched_file)
            
            if packages:
                # Create vector store
                vector_store = EnhancedVectorStore(db_path=Config.DB_PATH)
                
                # Add packages to vector store
                texts = []
                for package in packages:
                    # Create text for embedding
                    text = f"Travel package: {package.get('name', '')}\n"
                    text += f"Destination: {package.get('location', package.get('destination', ''))}\n"
                    text += f"Description: {package.get('description', '')}\n"
                    
                    # Add activities
                    activities = []
                    if 'activities' in package and isinstance(package['activities'], list):
                        for activity in package['activities']:
                            if isinstance(activity, dict) and 'name' in activity:
                                activities.append(activity['name'])
                            elif isinstance(activity, str):
                                activities.append(activity)
                    
                    if activities:
                        text += f"Activities: {', '.join(activities)}\n"
                    
                    # Add duration and price
                    text += f"Duration: {package.get('duration', '')}\n"
                    
                    if isinstance(package.get('price'), dict):
                        text += f"Price: {package['price'].get('amount', '')} {package['price'].get('currency', '')}\n"
                    else:
                        text += f"Price: {package.get('price', '')}\n"
                    
                    texts.append(text)
                
                # Add packages to vector store
                vector_store.add_packages(packages, texts)
                logger.info(f"Imported {len(packages)} packages to vector store")
            else:
                logger.warning(f"No packages found in {enriched_file}")
        else:
            logger.warning(f"Enriched file {enriched_file} not found")
    
    logger.info("Data enhancement completed!")

if __name__ == "__main__":
    main()
    
# Add this code at the end of the enhanced_data_sources.py file to rebuild the vector store
from src.knowledge_base.vector_store import VectorStore
import os

# Remove existing vector store
vector_store_path = "data/embeddings/vector_store.pkl"
if os.path.exists(vector_store_path):
    os.remove(vector_store_path)
    print(f"Removed existing vector store: {vector_store_path}")

# Rebuild it
from src.main import initialize_vector_store, load_travel_packages

packages = load_travel_packages("data/synthetic/enriched_travel_packages.json",
                               fallback_path="data/synthetic/travel_packages.json")
vector_store = initialize_vector_store(packages)
print(f"Rebuilt vector store with {len(packages)} packages using enhanced text embeddings")