#!/usr/bin/env python3
import json
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def fix_beach_package():
    """Fix the country and weather data for the Beach Getaway package."""
    print("Fixing Beach Getaway package data...")
    
    # Try to load from enriched_travel_packages.json first
    packages_path = Path("data/synthetic/enriched_travel_packages.json")
    if not packages_path.exists():
        packages_path = Path("data/synthetic/travel_packages.json")
        
    if not packages_path.exists():
        print(f"Error: Cannot find packages file at {packages_path}")
        return False
        
    try:
        with open(packages_path, 'r') as f:
            data = json.load(f)
            packages = data.get('packages', [])
            
        # Update the Beach Getaway package
        beach_package_found = False
        for package in packages:
            if package.get('name') == 'Beach Getaway':
                beach_package_found = True
                # Set correct country and continent
                package['country'] = 'Maldives'
                package['continent'] = 'Asia'
                
                # Make sure location matches
                package['location'] = 'Maldives'
                package['destination'] = 'Maldives'
                
                # Add appropriate weather data for tropical location
                package['weather_data'] = {
                    'daily': {
                        'time': ['2025-05-08', '2025-05-09', '2025-05-10', '2025-05-11', '2025-05-12'],
                        'temperature_2m_max': [32.1, 31.8, 32.3, 31.9, 32.5],
                        'temperature_2m_min': [26.5, 26.3, 26.7, 26.4, 26.8],
                        'precipitation_sum': [0.0, 2.3, 0.0, 0.5, 1.2]
                    }
                }
                
                # Make sure activities are in the right format and beach-focused
                if isinstance(package.get('activities'), list):
                    # Check if activities are already in dict format
                    if all(isinstance(act, dict) for act in package['activities']):
                        # They're already dict format, just make sure beach keywords are prominent
                        for act in package['activities']:
                            if 'beach' not in act['name'].lower():
                                act['description'] = f"Enjoy {act['name']} on the beautiful beaches of Maldives"
                    else:
                        # Convert string activities to dict format with beach emphasis
                        activities = []
                        for act_str in package['activities']:
                            activities.append({
                                'name': act_str,
                                'description': f"Enjoy {act_str} on the beautiful beaches of Maldives",
                                'duration': '3 hours',
                                'included_in_package': True
                            })
                        package['activities'] = activities
                
                print(f"Updated Beach Getaway package with correct country, continent, and weather data")
                
                # Also add some local attractions
                package['local_attractions'] = [
                    {
                        'name': 'Coral Reef Snorkeling',
                        'description': 'Explore vibrant coral reefs with tropical fish',
                        'included_in_package': False
                    },
                    {
                        'name': 'Island Hopping Tour',
                        'description': 'Visit multiple beautiful islands in one day',
                        'included_in_package': False
                    },
                    {
                        'name': 'Traditional Fishing Trip',
                        'description': 'Learn traditional Maldivian fishing techniques',
                        'included_in_package': False
                    }
                ]
                
                # Add currency and language info
                package['local_info'] = {
                    'capital': 'Malé',
                    'currency': 'Maldivian Rufiyaa (MVR)',
                    'languages': 'Dhivehi, English'
                }
        
        if not beach_package_found:
            print("Warning: Beach Getaway package not found in packages")
            return False
            
        # Save the updated packages
        with open(packages_path, 'w') as f:
            json.dump({"packages": packages}, f, indent=2)
            
        print(f"Saved updated packages to {packages_path}")
        return True
    except Exception as e:
        print(f"Error fixing Beach Getaway package: {e}")
        return False

if __name__ == "__main__":
    fix_beach_package()