import json
import logging
from pathlib import Path
import random
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

from src.utils.api_clients import (
    get_weather_forecast, 
    get_coordinates, 
    get_country_info,
    get_local_attractions,
    get_wikivoyage_info,
    get_continent_from_country,
    get_reverse_geocoding  

)

logger = logging.getLogger(__name__)

class DataEnrichmentPipeline:
    def __init__(self):
        self.packages = []
        
    def load_base_packages(self, source_file: str):
        """Load initial package data from a JSON file."""
        try:
            with open(source_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'packages' in data:
                    self.packages = data['packages']
                elif isinstance(data, list):
                    self.packages = data
                else:
                    self.packages = []
                    
            logger.info(f"Loaded {len(self.packages)} base packages from {source_file}")
        except Exception as e:
            logger.error(f"Error loading base packages: {e}")
            self.packages = []
            
    def enrich_all_packages(self) -> List[Dict]:
        """Enrich all loaded packages with additional data."""
        enriched_packages = []
        
        for package in self.packages:
            try:
                # Convert to standard format if needed
                if isinstance(package, dict):
                    enriched = self.enrich_package(package)
                    enriched_packages.append(enriched)
            except Exception as e:
                logger.error(f"Error enriching package {package.get('name', 'unknown')}: {e}")
                
        logger.info(f"Enriched {len(enriched_packages)} packages")
        return enriched_packages
            
    def enrich_package(self, package: Dict) -> Dict:
        """Enrich a single package with additional data."""
        # Step 1: Standardize basic package fields
        enriched = {
            "id": package.get("id") or str(uuid.uuid4()),
            "name": package.get("name", "Unknown Package"),
            "description": package.get("description", ""),
            "destination": package.get("location", "Unknown"),
            "country": "Unknown",  # Will try to determine from location
            "continent": "Unknown",  # Will try to determine from country
            "price": {
                "amount": float(package.get("price", 0)) if isinstance(package.get("price"), (int, float)) else 0,
                "currency": "USD",
                "per_person": True
            },
            "duration": package.get("duration", "5 days"),
            "activities": [],
            "last_updated": datetime.now().isoformat()
        }
        
        # Step 2: Get coordinates
        location = package.get("location", "")
        coords = get_coordinates(location)
        
        if coords:
            enriched["coordinates"] = {
                "latitude": coords["lat"],
                "longitude": coords["lon"]
            }
            
            # Step 3: Add weather data
            try:
                weather = get_weather_forecast(coords["lat"], coords["lon"])
                if weather:
                    enriched["weather_data"] = weather
            except Exception as e:
                logger.error(f"Error getting weather for {location}: {e}")
        
        
        # Step 4: Try to determine country and continent
        if "," in location:
            # If location has format "City, Country"
            parts = location.split(",")
            if len(parts) >= 2:
                potential_country = parts[-1].strip()
                # Get country info
                country_info = get_country_info(potential_country)
                if country_info:
                    enriched["country"] = potential_country
                    # Get continent
                    enriched["continent"] = get_continent_from_country(potential_country)
        else:
            # Try to extract country from location name based on known locations
            location_lower = location.lower()
            if "swiss" in location_lower or "switzerland" in location_lower:
                enriched["country"] = "Switzerland"
                enriched["continent"] = "Europe"
            elif "alps" in location_lower and enriched["country"] == "Unknown":
                enriched["country"] = "Multiple (France, Italy, Switzerland, Austria)"
                enriched["continent"] = "Europe"
            elif "rome" in location_lower or "venice" in location_lower or "florence" in location_lower or "italy" in location_lower:
                enriched["country"] = "Italy"
                enriched["continent"] = "Europe"
            elif "paris" in location_lower or "france" in location_lower:
                enriched["country"] = "France"
                enriched["continent"] = "Europe"
            elif "london" in location_lower or "uk" in location_lower or "united kingdom" in location_lower:
                enriched["country"] = "United Kingdom" 
                enriched["continent"] = "Europe"
            elif "new york" in location_lower or "nyc" in location_lower or "usa" in location_lower or "united states" in location_lower:
                enriched["country"] = "United States"
                enriched["continent"] = "North America"
            elif "maldives" in location_lower:
                enriched["country"] = "Maldives"
                enriched["continent"] = "Asia"
            elif "kenya" in location_lower:
                enriched["country"] = "Kenya"
                enriched["continent"] = "Africa"
            # Try using reverse geocoding if coordinates are available
            elif coords:
                try:
                    reverse_data = get_reverse_geocoding(coords["lat"], coords["lon"])
                    if reverse_data and "address" in reverse_data and "country" in reverse_data["address"]:
                        enriched["country"] = reverse_data["address"]["country"]
                        # Get continent based on country
                        enriched["continent"] = get_continent_from_country(enriched["country"])
                except Exception as e:
                    logger.error(f"Error with reverse geocoding: {e}")

        # Step 5: Add activities
        if "activities" in package and isinstance(package["activities"], list):
            for activity in package["activities"]:
                if isinstance(activity, dict) and 'name' in activity:
                    activity_name = activity['name']
                else:
                    activity_name = activity
                
                activity_obj = {
                    "name": activity_name,
                    "description": f"Enjoy {activity_name} in {location}",
                    "duration": f"{random.randint(1, 4)} hours",
                    "included_in_package": True
                }
                enriched["activities"].append(activity_obj)
        
        # Step 6: Add local attractions if coordinates are available
        if coords:
            try:
                attractions = get_local_attractions(coords["lat"], coords["lon"])
                if attractions:
                    # Add as additional activities
                    for attraction in attractions[:5]:  # Limit to 5
                        activity = {
                            "name": attraction["name"],
                            "description": f"Visit {attraction['name']}, a local {attraction['type']}",
                            "duration": "2 hours",
                            "included_in_package": False,
                            "coordinates": {
                                "latitude": attraction["lat"],
                                "longitude": attraction["lon"]
                            }
                        }
                        enriched["activities"].append(activity)
            except Exception as e:
                logger.error(f"Error getting attractions for {location}: {e}")
        
        # Step 7: Add destination guide
        try:
            wiki_info = get_wikivoyage_info(location)
            if wiki_info and "extract" in wiki_info:
                enriched["destination_guide"] = wiki_info
        except Exception as e:
            logger.error(f"Error getting wiki info for {location}: {e}")
        
        return enriched
        
    def save_enriched_packages(self, output_file: str):
        """Save enriched packages to a JSON file."""
        try:
            enriched = self.enrich_all_packages()
            
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump({"packages": enriched}, f, indent=2)
                
            logger.info(f"Saved {len(enriched)} enriched packages to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving enriched packages: {e}")
            return False
        
    