# test_enriched_data.py
import sys
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.generation.proposal_generator import ProposalGenerator

def test_enriched_data_usage():
    """Test if the proposal generator effectively uses the enriched data."""
    # Load the Beach Getaway package
    packages_path = Path("data/synthetic/enriched_travel_packages.json")
    if not packages_path.exists():
        packages_path = Path("data/synthetic/travel_packages.json")
        
    with open(packages_path, 'r') as f:
        data = json.load(f)
        packages = data.get('packages', [])
    
    # Find the Beach Getaway package
    beach_package = None
    for package in packages:
        if package.get('name') == 'Beach Getaway':
            beach_package = package
            break
    
    if not beach_package:
        print("Beach Getaway package not found!")
        return
    
    # Check enriched data fields
    print("\nEnriched Data Fields in Beach Getaway Package:")
    print(f"Country: {beach_package.get('country')}")
    print(f"Continent: {beach_package.get('continent')}")
    
    if beach_package.get('weather_data'):
        print("Weather data: Available")
    else:
        print("Weather data: Not available")
        
    if beach_package.get('local_info'):
        print(f"Local info: {', '.join(beach_package.get('local_info', {}).keys())}")
    else:
        print("Local info: Not available")
        
    if beach_package.get('local_attractions'):
        print(f"Local attractions: {len(beach_package.get('local_attractions', []))} available")
    else:
        print("Local attractions: Not available")
    
    # Create a test customer request
    customer_info = {
        'destination': 'Maldives',
        'travel_type': 'beach vacation',
        'budget': '$3000',
        'travelers': '2 adults, 2 children',
        'interests': 'beach activities, snorkeling, relaxation'
    }
    
    # Generate a proposal
    proposal_generator = ProposalGenerator()
    proposal = proposal_generator.generate_proposal(customer_info, [beach_package])
    
    # Check if enriched data appears in the proposal
    enriched_data_keywords = [
        'maldives', 'asia', 'weather', 'temperature', 'tropical',
        'currency', 'language', 'activities', 'snorkeling', 'beach'
    ]
    
    print("\nEnriched Data Usage in Proposal:")
    proposal_lower = proposal.lower()
    
    for keyword in enriched_data_keywords:
        if keyword in proposal_lower:
            print(f"✅ '{keyword}' found in proposal")
        else:
            print(f"❌ '{keyword}' NOT found in proposal")
    
    # Return the generated proposal
    print("\nGenerated Proposal (first 500 chars):")
    print(proposal[:500] + "..." if len(proposal) > 500 else proposal)
    
    return proposal

if __name__ == "__main__":
    test_enriched_data_usage()