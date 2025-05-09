# test_custom_email.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from src.email_processing.extractor import EmailExtractor
from src.knowledge_base.vector_store import VectorStore
from src.retrieval.retriever import Retriever
from src.generation.proposal_generator import ProposalGenerator

def test_email(email_text):
    """Test the system with a custom email."""
    # Initialize components
    vector_store = VectorStore()
    vector_store.load()
    retriever = Retriever(vector_store)
    proposal_generator = ProposalGenerator()
    
    # Process the email
    extracted_info, packages = retriever.get_packages_from_email(email_text)
    
    # Print extracted info
    print("\n=== Extracted Information ===")
    for key, value in extracted_info.items():
        if key != "Here's the extracted information" and value is not None:
            print(f"{key}: {value}")
    
    # Print retrieved packages
    print("\n=== Retrieved Packages ===")
    for i, pkg in enumerate(packages):
        print(f"{i+1}. {pkg.get('name')} - {pkg.get('location') or pkg.get('destination')}")
    
    # Generate and print proposal
    proposal = proposal_generator.generate_proposal(extracted_info, packages)
    print("\n=== Generated Proposal (first 500 chars) ===")
    print(proposal[:500] + "..." if len(proposal) > 500 else proposal)
    
    return proposal

# Test with different emails
emails = [
    # Beach vacation
    """
    Hi, I'm looking for a beach vacation for my family. We want to relax on beautiful beaches
    with clear water. Our budget is around $3000 and we'd like to go for 5-7 days. 
    What beach destinations can you recommend?
    """,
    
    # Mountain adventure
    """
    Hello, my partner and I are planning a hiking trip in the mountains next month.
    We're looking for scenic trails and outdoor activities. Our budget is flexible,
    around $2500-3000. Any mountain destinations you'd suggest?
    """,
    
    # City break
    """
    I need a quick city break for the weekend. I'm interested in museums, dining,
    and shopping. Budget is about $1000 for 3 days. What city would you recommend?
    """
]

if __name__ == "__main__":
    choice = input("""Choose an email to test:
1. Beach vacation
2. Mountain adventure
3. City break
Enter choice (1-3): """)
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(emails):
            print(f"\nProcessing email type: {['Beach vacation', 'Mountain adventure', 'City break'][idx]}")
            test_email(emails[idx])
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    except ValueError:
        print("Invalid input. Please enter a number.")