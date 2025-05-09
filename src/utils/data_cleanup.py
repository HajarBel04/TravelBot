import logging
from pathlib import Path
import json
import uuid
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def validate_package(package: Dict) -> bool:
    """
    Validate a travel package for required fields and data integrity.
    
    Args:
        package: The package to validate
        
    Returns:
        bool: True if package is valid, False otherwise
    """
    # Check required fields
    required_fields = ['id', 'name', 'location']
    for field in required_fields:
        if field not in package or not package[field]:
            logger.warning(f"Package missing required field: {field}")
            return False
    
    # Validate types
    if 'price' in package and not isinstance(package['price'], (int, float, dict)):
        logger.warning(f"Invalid price format in package {package.get('id')}")
        return False
        
    if 'activities' in package and not isinstance(package['activities'], list):
        logger.warning(f"Invalid activities format in package {package.get('id')}")
        return False
    
    # Check activities format
    if 'activities' in package:
        for activity in package['activities']:
            if isinstance(activity, dict) and ('name' not in activity or not activity['name']):
                logger.warning(f"Activity missing name in package {package.get('id')}")
                return False
    
    # Package is valid
    return True

def clean_package(package: Dict) -> Dict:
    """
    Clean and normalize a travel package.
    
    Args:
        package: The package to clean
        
    Returns:
        Dict: The cleaned package
    """
    cleaned = package.copy()
    
    # Ensure ID exists
    if 'id' not in cleaned or not cleaned['id']:
        cleaned['id'] = str(uuid.uuid4())
    
    # Normalize location/destination
    if 'location' in cleaned and 'destination' not in cleaned:
        cleaned['destination'] = cleaned['location']
    elif 'destination' in cleaned and 'location' not in cleaned:
        cleaned['location'] = cleaned['destination']
    
    # Normalize price
    if 'price' in cleaned:
        if isinstance(cleaned['price'], (int, float)):
            cleaned['price'] = {
                'amount': float(cleaned['price']),
                'currency': 'USD'
            }
        elif isinstance(cleaned['price'], dict):
            # Ensure amount is a float
            if 'amount' in cleaned['price']:
                cleaned['price']['amount'] = float(cleaned['price']['amount'])
            
            # Ensure currency exists
            if 'currency' not in cleaned['price']:
                cleaned['price']['currency'] = 'USD'
    else:
        # Add default price
        cleaned['price'] = {
            'amount': 1000.0,
            'currency': 'USD'
        }
    
    # Normalize activities
    if 'activities' in cleaned:
        normalized_activities = []
        
        for activity in cleaned['activities']:
            if isinstance(activity, str):
                # Convert string to activity object
                normalized_activities.append({
                    'name': activity,
                    'description': activity,
                    'duration': '2 hours'
                })
            elif isinstance(activity, dict):
                # Ensure activity has required fields
                if 'name' not in activity:
                    continue
                    
                normalized_activity = activity.copy()
                
                if 'description' not in normalized_activity:
                    normalized_activity['description'] = normalized_activity['name']
                    
                if 'duration' not in normalized_activity:
                    normalized_activity['duration'] = '2 hours'
                    
                normalized_activities.append(normalized_activity)
        
        cleaned['activities'] = normalized_activities
    else:
        # Add empty activities list
        cleaned['activities'] = []
    
    # Add coordinates if missing
    if 'coordinates' not in cleaned:
        cleaned['coordinates'] = None
    
    # Add country if missing
    if 'country' not in cleaned:
        # Try to extract from location
        if 'location' in cleaned and ',' in cleaned['location']:
            parts = cleaned['location'].split(',')
            if len(parts) >= 2:
                cleaned['country'] = parts[-1].strip()
            else:
                cleaned['country'] = 'Unknown'
        else:
            cleaned['country'] = 'Unknown'
    
    # Add duration if missing
    if 'duration' not in cleaned or not cleaned['duration']:
        cleaned['duration'] = '5 days'
    
    # Add description if missing
    if 'description' not in cleaned or not cleaned['description']:
        cleaned['description'] = f"Explore {cleaned.get('destination', cleaned.get('location', 'this destination'))} and discover its unique attractions."
    
    return cleaned

def process_package_file(input_path: str, output_path: str) -> bool:
    """
    Validate, clean, and save a package file.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load packages
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and 'packages' in data:
            packages = data['packages']
        elif isinstance(data, list):
            packages = data
        else:
            logger.error(f"Invalid file format: {input_path}")
            return False
        
        # Process packages
        valid_packages = []
        for package in packages:
            if validate_package(package):
                cleaned = clean_package(package)
                valid_packages.append(cleaned)
        
        # Save processed packages
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"packages": valid_packages}, f, indent=2)
        
        logger.info(f"Processed {len(valid_packages)} valid packages out of {len(packages)}")
        return True
    except Exception as e:
        logger.error(f"Error processing package file: {e}")
        return False

def deduplicate_packages(packages: List[Dict]) -> List[Dict]:
    """
    Remove duplicate packages based on location and name similarity.
    
    Args:
        packages: List of packages to deduplicate
        
    Returns:
        List[Dict]: Deduplicated packages
    """
    try:
        deduplicated = []
        seen_locations = set()
        seen_names = set()
        
        for package in packages:
            # Get normalized location and name
            location = package.get('location', '').lower().strip()
            name = package.get('name', '').lower().strip()
            
            # Skip if we've seen very similar location and name
            if location in seen_locations and any(name in seen for seen in seen_names):
                continue
                
            seen_locations.add(location)
            seen_names.add(name)
            deduplicated.append(package)
        
        logger.info(f"Deduplicated packages: {len(packages)} -> {len(deduplicated)}")
        return deduplicated
    except Exception as e:
        logger.error(f"Error deduplicating packages: {e}")
        return packages
    

def clean_country_data(packages: List[Dict]) -> List[Dict]:
    """
    Add missing country and continent data to packages.
    
    Args:
        packages: List of travel packages
        
    Returns:
        List of packages with corrected country and continent info
    """
    # This mapping covers common travel destinations
    location_to_country = {
        "Swiss Alps": "Switzerland",
        "Maldives": "Maldives",
        "Rome": "Italy",
        "Venice": "Italy",
        "Florence": "Italy",
        "Kenya": "Kenya",
        "New York": "United States",
        "Paris": "France",
        "London": "United Kingdom",
        "Bangkok": "Thailand",
        "Tokyo": "Japan",
        "Sydney": "Australia",
        "Cape Town": "South Africa"
    }
    
    country_to_continent = {
        "Switzerland": "Europe",
        "Maldives": "Asia",
        "Italy": "Europe",
        "Kenya": "Africa",
        "United States": "North America",
        "France": "Europe",
        "United Kingdom": "Europe",
        "Thailand": "Asia",
        "Japan": "Asia",
        "Australia": "Oceania",
        "South Africa": "Africa"
    }
    
    fixed_count = 0
    
    for package in packages:
        location = package.get("destination", "") or package.get("location", "")
        
        # Skip if already has valid country and continent
        if (package.get("country") and package.get("country") != "Unknown" and
            package.get("continent") and package.get("continent") != "Unknown"):
            continue
            
        # If country is unknown, try to determine it
        if package.get("country") == "Unknown" or not package.get("country"):
            for key, value in location_to_country.items():
                if key.lower() in location.lower():
                    package["country"] = value
                    fixed_count += 1
                    break
        
        # If continent is unknown, try to determine it from country
        if package.get("continent") == "Unknown" or not package.get("continent"):
            country = package.get("country", "")
            if country in country_to_continent:
                package["continent"] = country_to_continent[country]
                fixed_count += 1
    
    logger.info(f"Fixed country/continent data for {fixed_count} packages")
    return packages