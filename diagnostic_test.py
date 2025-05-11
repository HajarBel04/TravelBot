# diagnostic_test.py
import requests
import json
import sys
from pathlib import Path

# Adjust these paths to match your project structure
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import components directly (adjust imports as needed)
from src.email_processing.extractor import EmailExtractor
from src.retrieval.retriever import Retriever
from src.generation.proposal_generator import ProposalGenerator
from src.knowledge_base.vector_store import VectorStore
from src.generation.llm_wrapper import OllamaWrapper

def test_api_endpoint():
    """Test the API endpoint directly."""
    print("\n=== Testing API Endpoint ===")
    
    test_email = """
    Hello Travel Assistant,
    
    I'm planning a trip to Paris, France for 5 days in July 2025. I'll be traveling with my partner, 
    and our budget is approximately $3,000 for the entire trip.
    
    We're interested in visiting the major attractions like the Eiffel Tower, Louvre Museum, and Notre Dame.
    
    Thank you!
    """
    
    url = "http://localhost:8000/api/process-email"
    headers = {"Content-Type": "application/json"}
    data = {"email": test_email}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("API Response SUCCESS!")
                print(f"Extracted Info: {json.dumps(result.get('extracted_info', {}), indent=2)}")
                print(f"Packages Count: {len(result.get('packages', []))}")
                proposal_preview = result.get('proposal', '')[:100] + "..." if result.get('proposal') else "No proposal"
                print(f"Proposal Preview: {proposal_preview}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(f"Raw Response: {response.text[:500]}...")
        else:
            print(f"Error Response: {response.text}")
    except Exception as e:
        print(f"Request Error: {e}")

def test_components():
    """Test each component individually."""
    print("\n=== Testing Individual Components ===")
    
    test_email = """
    Hello Travel Assistant,
    
    I'm planning a trip to Paris, France for 5 days in July 2025. I'll be traveling with my partner, 
    and our budget is approximately $3,000 for the entire trip.
    
    We're interested in visiting the major attractions like the Eiffel Tower, Louvre Museum, and Notre Dame.
    
    Thank you!
    """
    
    # 1. Test Email Extraction
    print("\n--- Testing Email Extraction ---")
    try:
        extractor = EmailExtractor()
        extracted_info = extractor.extract_from_email(test_email)
        print(f"Extracted Info: {json.dumps(extracted_info, indent=2)}")
        
        if not extracted_info or all(v is None for v in extracted_info.values()):
            print("⚠️ WARNING: No information extracted from email")
    except Exception as e:
        print(f"❌ ERROR in Email Extraction: {e}")
    
    # 2. Test Vector Store Loading
    print("\n--- Testing Vector Store ---")
    try:
        vector_store = VectorStore()
        vector_store.load()
        doc_count = len(vector_store.documents) if hasattr(vector_store, 'documents') else 0
        print(f"Vector Store Documents: {doc_count}")
        
        if doc_count == 0:
            print("⚠️ WARNING: No documents in vector store")
    except Exception as e:
        print(f"❌ ERROR in Vector Store: {e}")
    
    # 3. Test Retrieval
    print("\n--- Testing Retrieval ---")
    try:
        retriever = Retriever(vector_store)
        query = retriever.build_query(extracted_info)
        print(f"Generated Query: {query}")
        
        packages = retriever.retrieve_relevant_packages(query, top_k=3)
        print(f"Retrieved Packages: {len(packages)}")
        
        if packages:
            for i, pkg in enumerate(packages):
                print(f"  Package {i+1}: {pkg.get('name')} - {pkg.get('location', pkg.get('destination', 'Unknown'))}")
        else:
            print("⚠️ WARNING: No packages retrieved")
    except Exception as e:
        print(f"❌ ERROR in Retrieval: {e}")
    
    # 4. Test Proposal Generation
    print("\n--- Testing Proposal Generation ---")
    try:
        if packages:
            proposal_generator = ProposalGenerator()
            proposal = proposal_generator.generate_proposal(extracted_info, packages)
            print(f"Proposal Length: {len(proposal)} characters")
            print(f"Proposal Preview: {proposal[:200]}...")
            
            if len(proposal) < 100:
                print("⚠️ WARNING: Proposal is very short")
        else:
            print("⚠️ Skipping proposal generation due to missing packages")
    except Exception as e:
        print(f"❌ ERROR in Proposal Generation: {e}")

if __name__ == "__main__":
    print("Starting diagnostic tests...")
    
    # First test the API endpoint
    test_api_endpoint()
    
    # Then test individual components
    test_components()
    
    print("\nDiagnostic tests completed.")