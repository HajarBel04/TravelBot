#!/usr/bin/env python3

import os
import sys
import json
import logging
import time
import uuid
import random
from pathlib import Path
import argparse

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.utils.web_scraper import TravelDataScraper
from src.knowledge_base.enrichment import DataEnrichmentPipeline
from src.utils.api_clients import (
    get_weather_forecast, 
    get_coordinates, 
    get_country_info,
    get_local_attractions,
    get_wikivoyage_info,
    get_continent_from_country
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def collect_and_enrich_data(output_file: str = "data/synthetic/enriched_travel_packages.json", 
                           sources: list = ["unesco", "wikitravel"],
                           limit: int = 20):
    """
    Collect and enrich travel data from various sources.
    
    Args:
        output_file: Path to save the collected data
        sources: List of sources to collect from ("unesco", "wikitravel")
        limit: Maximum number of items to collect per source
    """
    logger.info(f"Collecting travel data from sources: {sources}")
    
    # Create scraper
    scraper = TravelDataScraper()
    
    all_packages = []
    
    # Collect from UNESCO
    if "unesco" in sources:
        logger.info("Collecting UNESCO World Heritage Sites...")
        unesco_sites = scraper.scrape_unesco_sites()
        logger.info(f"Collected {len(unesco_sites)} UNESCO sites")
        
        # Take only up to the limit
        all_packages.extend(unesco_sites[:limit])
    
    # Collect from Wikitravel
    if "wikitravel" in sources:
        logger.info("Collecting WikiTravel destinations...")
        wikitravel_dests = scraper.scrape_wikitravel_destinations(limit=limit)
        logger.info(f"Collected {len(wikitravel_dests)} WikiTravel destinations")
        
        all_packages.extend(wikitravel_dests)
    
    # If we didn't get any new data, check if we have existing data to enrich
    if not all_packages:
        logger.info("No new data collected, checking for existing data to enrich...")
        
        existing_path = project_root / "data" / "synthetic" / "travel_packages.json"
        if existing_path.exists():
            with open(existing_path, 'r') as f:
                data = json.load(f)
                if 'packages' in data:
                    all_packages = data['packages']
                    logger.info(f"Loaded {len(all_packages)} existing packages for enrichment")
                    
    # Enrich all collected data
    if all_packages:
        logger.info(f"Enriching {len(all_packages)} packages with additional data...")
        
        enrichment = DataEnrichmentPipeline()
        enriched_packages = []
        
        for package in all_packages:
            enriched = enrichment.enrich_package(package)
            enriched_packages.append(enriched)
            # Add a small delay to avoid rate limiting with APIs
            time.sleep(0.5)
            
        # Save the enriched data
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({"packages": enriched_packages}, f, indent=2)
            
        logger.info(f"Saved {len(enriched_packages)} enriched packages to {output_file}")
        return len(enriched_packages)
    else:
        logger.warning("No packages collected or found for enrichment")
        return 0

def get_popular_destinations(limit: int = 100) -> list:
    """Generate a list of popular travel destinations for manual collection."""
    popular_destinations = [
        # Europe
        "Paris, France", "Rome, Italy", "Barcelona, Spain", "London, UK", "Amsterdam, Netherlands",
        "Prague, Czech Republic", "Vienna, Austria", "Athens, Greece", "Venice, Italy", "Budapest, Hungary",
        "Santorini, Greece", "Florence, Italy", "Dublin, Ireland", "Zurich, Switzerland", "Berlin, Germany",
        
        # Asia
        "Tokyo, Japan", "Kyoto, Japan", "Bangkok, Thailand", "Bali, Indonesia", "Singapore",
        "Hong Kong", "Seoul, South Korea", "Phuket, Thailand", "Dubai, UAE", "Shanghai, China",
        "New Delhi, India", "Mumbai, India", "Kathmandu, Nepal", "Hanoi, Vietnam", "Istanbul, Turkey",
        
        # North America
        "New York City, USA", "Los Angeles, USA", "San Francisco, USA", "Las Vegas, USA", "Miami, USA",
        "New Orleans, USA", "Chicago, USA", "Toronto, Canada", "Vancouver, Canada", "Mexico City, Mexico",
        "Cancun, Mexico", "Montreal, Canada", "Hawaii, USA", "Seattle, USA", "Boston, USA",
        
        # South America
        "Rio de Janeiro, Brazil", "Buenos Aires, Argentina", "Machu Picchu, Peru", "Lima, Peru", "Santiago, Chile",
        "Bogota, Colombia", "Quito, Ecuador", "Cusco, Peru", "Cartagena, Colombia", "Galapagos Islands, Ecuador",
        
        # Africa
        "Cairo, Egypt", "Cape Town, South Africa", "Marrakech, Morocco", "Nairobi, Kenya", "Zanzibar, Tanzania",
        "Casablanca, Morocco", "Victoria Falls, Zimbabwe", "Luxor, Egypt", "Johannesburg, South Africa", "Mauritius",
        
        # Oceania
        "Sydney, Australia", "Melbourne, Australia", "Auckland, New Zealand", "Queenstown, New Zealand", "Fiji",
        "Gold Coast, Australia", "Perth, Australia", "Brisbane, Australia", "Wellington, New Zealand", "Tahiti"
    ]
    
    # Shuffle the list and return up to the limit
    random.shuffle(popular_destinations)
    return popular_destinations[:limit]

def manually_enrich_destinations(destinations: list, output_file: str):
    """Manually build travel packages for a list of destinations using APIs."""
    logger.info(f"Manually enriching {len(destinations)} destinations...")
    
    packages = []
    
    for dest in destinations:
        try:
            # Try to get coordinates
            coords = get_coordinates(dest)
            
            if not coords:
                logger.warning(f"Could not find coordinates for {dest}, skipping...")
                continue
                
            lat, lon = coords["lat"], coords["lon"]
            
            # Split destination into city and country if possible
            parts = dest.split(',')
            city = parts[0].strip()
            country = parts[1].strip() if len(parts) > 1 else "Unknown"
            
            # Create basic package
            package_id = str(uuid.uuid4())
            package = {
                "id": package_id,
                "name": f"Explore {city}",
                "location": dest,
                "destination": city,
                "country": country,
                "continent": get_continent_from_country(country),
                "coordinates": {
                    "latitude": lat,
                    "longitude": lon
                },
                "description": f"Experience the charm and beauty of {city}, one of the most fascinating destinations in {country}.",
                "duration": f"{random.randint(3, 10)} days",
                "price": random.randint(800, 3000),
                "activities": [],
                "highlights": []
            }
            
            # Get attractions to use as activities
            attractions = get_local_attractions(lat, lon, radius=2000)
            
            if attractions:
                # Add activities based on attractions
                for attraction in attractions[:5]:  # Limit to 5
                    activity = {
                        "name": attraction["name"],
                        "description": f"Visit {attraction['name']}, a popular {attraction['type']} in {city}.",
                        "duration": f"{random.randint(1, 4)} hours",
                        "price": {
                            "amount": random.randint(10, 50),
                            "currency": "USD"
                        }
                    }
                    package["activities"].append(activity)
                    package["highlights"].append(attraction["name"])
            
            # If no attractions found, add some generic activities
            if not package["activities"]:
                generic_activities = [
                    f"Guided tour of {city}",
                    f"Local cuisine experience in {city}",
                    f"Cultural show in {city}",
                    f"Shopping experience in {city}",
                    f"Historical sites visit in {city}"
                ]
                
                for activity_name in generic_activities:
                    activity = {
                        "name": activity_name,
                        "description": f"Enjoy {activity_name.lower()}.",
                        "duration": f"{random.randint(2, 5)} hours",
                        "price": {
                            "amount": random.randint(20, 60),
                            "currency": "USD"
                        }
                    }
                    package["activities"].append(activity)
                
                package["highlights"] = generic_activities[:3]
            
            # Get country information
            country_info = get_country_info(country)
            if country_info:
                package["local_info"] = {
                    "capital": country_info[0].get("capital", ["Unknown"])[0] if country_info[0].get("capital") else "Unknown",
                    "currencies": country_info[0].get("currencies", {}),
                    "languages": country_info[0].get("languages", {}),
                    "flag": country_info[0].get("flags", {}).get("png", "")
                }
            
            # Get weather data
            weather = get_weather_forecast(lat, lon)
            if weather:
                package["weather_data"] = weather
            
            # Get wikivoyage information
            wiki_info = get_wikivoyage_info(city)
            if wiki_info:
                package["destination_guide"] = wiki_info
                
                # If we have a guide, extract sections for better highlights
                if "extract" in wiki_info and wiki_info["extract"]:
                    extract = wiki_info["extract"]
                    
                    # Try to find "See" or "Do" sections in the extract
                    see_sections = []
                    lines = extract.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip() in ["See", "Do", "Attractions", "Sights"]:
                            # Get next line as potential highlight
                            if i + 1 < len(lines) and lines[i+1].strip():
                                see_sections.append(lines[i+1].strip())
                    
                    # If we found sections, use them as highlights
                    if see_sections:
                        package["highlights"] = see_sections[:5]
            
            packages.append(package)
            
            # Add a small delay to avoid API rate limits
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error enriching {dest}: {e}")
            continue
    
    # Save the packages
    if packages:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({"packages": packages}, f, indent=2)
            
        logger.info(f"Saved {len(packages)} manually created packages to {output_file}")
        return len(packages)
    else:
        logger.warning("No packages created")
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect and enrich travel data from various sources')
    parser.add_argument('--output', type=str, default="data/synthetic/enriched_travel_packages.json",
                        help='Output file to save collected data')
    parser.add_argument('--sources', type=str, nargs='+', default=["unesco", "wikitravel"],
                        choices=["unesco", "wikitravel", "manual"],
                        help='Sources to collect data from')
    parser.add_argument('--limit', type=int, default=20,
                        help='Maximum number of items to collect per source')
    
    args = parser.parse_args()
    
    if "manual" in args.sources:
        # Manual collection uses a different function
        destinations = get_popular_destinations(args.limit)
        manually_enrich_destinations(destinations, args.output)
    else:
        # Standard collection from web sources
        collect_and_enrich_data(args.output, args.sources, args.limit)