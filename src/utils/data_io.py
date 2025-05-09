import json
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def import_csv_packages(file_path: str) -> List[Dict]:
    """Import travel packages from a CSV file."""
    try:
        import csv
        
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
            
        packages = []
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Create a package from CSV row
                package = {
                    "id": row.get("id") or str(uuid.uuid4()),
                    "name": row.get("name", "Unknown"),
                    "location": row.get("location", ""),
                    "destination": row.get("destination") or row.get("location", ""),
                    "description": row.get("description", ""),
                    "duration": row.get("duration", ""),
                    "price": float(row.get("price", 0)) if row.get("price") else 0
                }
                
                # Handle activities if present (assume comma-separated)
                if "activities" in row and row["activities"]:
                    package["activities"] = [act.strip() for act in row["activities"].split(",")]
                
                # Handle other columns as additional attributes
                for key, value in row.items():
                    if key not in package and value:
                        package[key] = value
                
                packages.append(package)
                
        logger.info(f"Imported {len(packages)} packages from {file_path}")
        return packages
    except Exception as e:
        logger.error(f"Error importing packages from CSV {file_path}: {e}")
        return []

def load_json_packages(file_path: str) -> List[Dict]:
    """Load travel packages from a JSON file."""
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different JSON formats
        if isinstance(data, dict) and 'packages' in data:
            return data['packages']
        elif isinstance(data, list):
            return data
        else:
            logger.warning(f"Unexpected JSON format in {file_path}")
            return []
    except Exception as e:
        logger.error(f"Error loading packages from {file_path}: {e}")
        return []

def save_json_packages(packages: List[Dict], file_path: str) -> bool:
    """Save travel packages to a JSON file."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"packages": packages}, f, indent=2)
            
        logger.info(f"Saved {len(packages)} packages to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving packages to {file_path}: {e}")
        return False
    
def convert_open_travel_data(file_path: str, output_path: str) -> bool:
    """
    Convert data from Open Travel datasets to our format.
    This function can handle various open travel data formats.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            return False
            
        # Determine file type
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif path.suffix.lower() == '.csv':
            packages = import_csv_packages(file_path)
            return save_json_packages(packages, output_path)
        else:
            logger.warning(f"Unsupported file format: {path.suffix}")
            return False
            
        # Process different JSON formats based on structure
        packages = []
        
        # Check for common open travel data formats
        if isinstance(data, list):
            # Format 1: List of destinations/attractions
            for item in data:
                if isinstance(item, dict):
                    package = _convert_open_data_item(item)
                    if package:
                        packages.append(package)
        elif isinstance(data, dict):
            # Format 2: Dictionary with data under specific keys
            if 'destinations' in data:
                for item in data['destinations']:
                    package = _convert_open_data_item(item)
                    if package:
                        packages.append(package)
            elif 'attractions' in data:
                for item in data['attractions']:
                    package = _convert_open_data_item(item)
                    if package:
                        packages.append(package)
            elif 'features' in data:
                # Format 3: GeoJSON format
                for feature in data['features']:
                    if 'properties' in feature:
                        package = _convert_open_data_item(feature['properties'])
                        
                        # Add coordinates if available
                        if 'geometry' in feature and 'coordinates' in feature['geometry']:
                            coords = feature['geometry']['coordinates']
                            if len(coords) >= 2:
                                # GeoJSON uses [longitude, latitude]
                                package['coordinates'] = {
                                    'longitude': coords[0],
                                    'latitude': coords[1]
                                }
                                
                        if package:
                            packages.append(package)
            elif 'packages' in data:
                # Format 4: Our own format
                packages = data['packages']
        
        # Save the converted packages
        if packages:
            return save_json_packages(packages, output_path)
        else:
            logger.warning(f"No valid packages found in {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"Error converting travel data {file_path}: {e}")
        return False

def _convert_open_data_item(item: Dict) -> Optional[Dict]:
    """Convert a single item from open travel data to our package format."""
    try:
        # Check if item has minimum required fields
        if not item:
            return None
            
        # Look for name/title field
        name = None
        for field in ['name', 'title', 'place_name', 'destination_name']:
            if field in item and item[field]:
                name = item[field]
                break
                
        if not name:
            return None
            
        # Create basic package
        package = {
            "id": item.get('id', str(uuid.uuid4())),
            "name": f"Visit {name}",
            "location": name,
            "destination": name
        }
        
        # Add description
        for field in ['description', 'summary', 'details', 'about']:
            if field in item and item[field]:
                package['description'] = item[field]
                break
        
        # Add country
        for field in ['country', 'country_name', 'nation']:
            if field in item and item[field]:
                package['country'] = item[field]
                break
                
        # Add coordinates if available
        if 'latitude' in item and 'longitude' in item:
            package['coordinates'] = {
                'latitude': float(item['latitude']),
                'longitude': float(item['longitude'])
            }
        elif 'lat' in item and 'lng' in item:
            package['coordinates'] = {
                'latitude': float(item['lat']),
                'longitude': float(item['lng'])
            }
        elif 'lat' in item and 'lon' in item:
            package['coordinates'] = {
                'latitude': float(item['lat']),
                'longitude': float(item['lon'])
            }
            
        # Add price information
        price = None
        for field in ['price', 'cost', 'price_from', 'min_price']:
            if field in item and item[field]:
                try:
                    price = float(item[field])
                    break
                except:
                    continue
                    
        if price:
            package['price'] = price
        else:
            # Add a placeholder price
            package['price'] = 1000
            
        # Add duration
        duration = None
        for field in ['duration', 'length', 'days']:
            if field in item and item[field]:
                duration = item[field]
                break
                
        if duration:
            # Try to normalize to "<number> days" format
            try:
                if isinstance(duration, (int, float)):
                    package['duration'] = f"{int(duration)} days"
                elif isinstance(duration, str):
                    if 'day' not in duration.lower():
                        package['duration'] = f"{duration} days"
                    else:
                        package['duration'] = duration
            except:
                package['duration'] = duration
        else:
            # Add a placeholder duration
            package['duration'] = "5 days"
            
        # Add activities
        activities = []
        
        for field in ['activities', 'things_to_do', 'attractions', 'features']:
            if field in item and item[field]:
                acts = item[field]
                if isinstance(acts, list):
                    for act in acts:
                        if isinstance(act, str):
                            activities.append(act)
                        elif isinstance(act, dict) and 'name' in act:
                            activities.append(act['name'])
                elif isinstance(acts, str):
                    # Split comma-separated activities
                    acts_list = [a.strip() for a in acts.split(',')]
                    activities.extend(acts_list)
        
        if activities:
            package['activities'] = activities
        
        return package
    except Exception as e:
        logger.error(f"Error converting item: {e}")
        return None
    
def merge_package_sources(sources: List[str], output_path: str) -> bool:
    """
    Merge multiple package sources into a single file.
    
    Args:
        sources: List of source file paths
        output_path: Output file path
    """
    try:
        all_packages = []
        
        # Track IDs to avoid duplicates
        seen_ids = set()
        
        for source in sources:
            packages = load_json_packages(source)
            
            # Add packages, avoiding duplicates
            for package in packages:
                pkg_id = package.get('id') or str(uuid.uuid4())
                
                # Use a new ID if duplicate found
                if pkg_id in seen_ids:
                    pkg_id = str(uuid.uuid4())
                    package['id'] = pkg_id
                
                seen_ids.add(pkg_id)
                all_packages.append(package)
        
        # Save merged packages
        if all_packages:
            return save_json_packages(all_packages, output_path)
        else:
            logger.warning("No packages found to merge")
            return False
    except Exception as e:
        logger.error(f"Error merging package sources: {e}")
        return False