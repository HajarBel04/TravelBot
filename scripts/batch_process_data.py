#!/usr/bin/env python3

import os
import sys
import json
import logging
import argparse
from pathlib import Path
import time

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.data_io import (
    load_json_packages,
    save_json_packages,
    import_csv_packages,
    convert_open_travel_data,
    merge_package_sources
)
from src.utils.data_cleanup import (
    process_package_file,
    deduplicate_packages
)
from src.knowledge_base.enrichment import DataEnrichmentPipeline
from scripts.collect_travel_data import (
    collect_and_enrich_data,
    manually_enrich_destinations,
    get_popular_destinations
)
from src.knowledge_base.enhanced_vector_store import EnhancedVectorStore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def batch_process_all_data(sources_dir: str, output_dir: str, vector_db_path: str):
    """
    Process all data sources in the specified directory and update the vector store.
    
    Args:
        sources_dir: Directory containing source files
        output_dir: Directory to save processed files
        vector_db_path: Path to vector database
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all data files in sources directory
    sources_path = Path(sources_dir)
    json_files = list(sources_path.glob('**/*.json'))
    csv_files = list(sources_path.glob('**/*.csv'))
    
    all_files = json_files + csv_files
    logger.info(f"Found {len(all_files)} data files to process")
    
    # Process each file
    processed_files = []
    
    for file_path in all_files:
        try:
            # Get relative path for output
            rel_path = file_path.relative_to(sources_path)
            output_file = output_path / f"{rel_path.stem}_processed.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Processing {file_path}...")
            
            # Process based on file type
            if file_path.suffix.lower() == '.json':
                process_package_file(str(file_path), str(output_file))
            elif file_path.suffix.lower() == '.csv':
                # Import CSV and save as JSON
                packages = import_csv_packages(str(file_path))
                save_json_packages(packages, str(output_file))
            
            processed_files.append(str(output_file))
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
    
    # Merge all processed files
    if processed_files:
        merged_file = output_path / "all_packages.json"
        merge_package_sources(processed_files, str(merged_file))
        
        # Load merged packages for deduplication
        all_packages = load_json_packages(str(merged_file))
        
        # Deduplicate
        unique_packages = deduplicate_packages(all_packages)
        
        # Save deduplicated packages
        deduplicated_file = output_path / "deduplicated_packages.json"
        save_json_packages(unique_packages, str(deduplicated_file))
        
        # Enrich the unique packages
        enrichment = DataEnrichmentPipeline()
        enriched_packages = []
        
        logger.info(f"Enriching {len(unique_packages)} packages...")
        for package in unique_packages:
            try:
                enriched = enrichment.enrich_package(package)
                enriched_packages.append(enriched)
                # Small delay to avoid API rate limits
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error enriching package {package.get('id')}: {e}")
        
        # Save enriched packages
        enriched_file = output_path / "enriched_packages.json"
        save_json_packages(enriched_packages, str(enriched_file))
        
        # Update vector store
        logger.info("Updating vector store...")
        vector_store = EnhancedVectorStore(db_path=vector_db_path)
        
        # Add packages to vector store
        texts = []
        for package in enriched_packages:
            # Create text representation for embedding
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
            
            # Add other fields
            text += f"Duration: {package.get('duration', '')}\n"
            if isinstance(package.get('price'), dict):
                text += f"Price: {package['price'].get('amount', '')} {package['price'].get('currency', '')}\n"
            else:
                text += f"Price: {package.get('price', '')}\n"
            
            texts.append(text)
        
        # Add packages to vector store
        vector_store.add_packages(enriched_packages, texts)
        
        logger.info(f"Successfully processed and added {len(enriched_packages)} packages to vector store")
        return len(enriched_packages)
    else:
        logger.warning("No files were successfully processed")
        return 0

def process_and_add_new_sources(args):
    """
    Process new data sources and add to the system.
    
    Args:
        args: Command line arguments
    """
    # Process based on command
    if args.command == 'collect':
        # Collect from web sources
        collect_and_enrich_data(
            output_file=args.output,
            sources=args.sources,
            limit=args.limit
        )
    elif args.command == 'manual':
        # Manually build packages for popular destinations
        destinations = get_popular_destinations(args.limit)
        manually_enrich_destinations(destinations, args.output)
    elif args.command == 'process':
        # Process existing files
        process_package_file(args.input, args.output)
    elif args.command == 'batch':
        # Batch process all data
        batch_process_all_data(
            args.sources_dir,
            args.output_dir,
            args.vector_db
        )
    elif args.command == 'merge':
        # Merge multiple sources
        merge_package_sources(args.inputs, args.output)
    elif args.command == 'convert':
        # Convert from other formats
        convert_open_travel_data(args.input, args.output)
    elif args.command == 'import':
        # Import to vector store directly
        packages = load_json_packages(args.input)
        vector_store = EnhancedVectorStore(db_path=args.vector_db)
        vector_store.add_packages(packages)
        logger.info(f"Imported {len(packages)} packages to vector store")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process travel data sources')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect data from web sources')
    collect_parser.add_argument('--output', type=str, default="data/synthetic/collected_packages.json",
                              help='Output file to save collected data')
    collect_parser.add_argument('--sources', type=str, nargs='+', default=["unesco", "wikitravel"],
                              choices=["unesco", "wikitravel"],
                              help='Sources to collect data from')
    collect_parser.add_argument('--limit', type=int, default=20,
                              help='Maximum number of items to collect per source')
    
    # Manual command
    manual_parser = subparsers.add_parser('manual', help='Manually build packages for popular destinations')
    manual_parser.add_argument('--output', type=str, default="data/synthetic/manual_packages.json",
                             help='Output file to save generated packages')
    manual_parser.add_argument('--limit', type=int, default=20,
                             help='Number of destinations to process')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a single data file')
    process_parser.add_argument('--input', type=str, required=True,
                              help='Input file to process')
    process_parser.add_argument('--output', type=str, required=True,
                              help='Output file to save processed data')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Batch process all data in a directory')
    batch_parser.add_argument('--sources-dir', type=str, default="data/sources",
                            help='Directory containing source files')
    batch_parser.add_argument('--output-dir', type=str, default="data/processed",
                            help='Directory to save processed files')
    batch_parser.add_argument('--vector-db', type=str, default="data/travel_data.db",
                            help='Path to vector database')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple sources')
    merge_parser.add_argument('--inputs', type=str, nargs='+', required=True,
                            help='Input files to merge')
    merge_parser.add_argument('--output', type=str, required=True,
                            help='Output file to save merged data')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert from other formats')
    convert_parser.add_argument('--input', type=str, required=True,
                              help='Input file to convert')
    convert_parser.add_argument('--output', type=str, required=True,
                              help='Output file to save converted data')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import to vector store')
    import_parser.add_argument('--input', type=str, required=True,
                             help='Input file to import')
    import_parser.add_argument('--vector-db', type=str, default="data/travel_data.db",
                             help='Path to vector database')
    
    args = parser.parse_args()
    
    if args.command:
        process_and_add_new_sources(args)
    else:
        parser.print_help()