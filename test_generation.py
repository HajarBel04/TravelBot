# Create a file called test_generation.py
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from enhanced_proposal_generator import ProposalGenerator
from src.generation.llm_wrapper import OllamaWrapper

print("Testing proposal generation...")

# Set up test data
extracted_info = {
    "destination": "beach",
    "dates": "summer",
    "travelers": "family",
    "budget": "$3000",
    "interests": "beach activities, kid-friendly"
}

packages = [
    {
        "name": "Beach Paradise",
        "location": "Maldives",
        "description": "Beautiful beaches and clear waters",
        "activities": ["swimming", "snorkeling", "beach relaxation"],
        "price": 2500
    }
]

# Initialize components with fewer tokens to speed up generation
ollama = OllamaWrapper()
ollama.max_tokens = 200  # Reduce tokens to get a faster response
proposal_generator = ProposalGenerator(ollama_client=ollama)

# Generate proposal with timeout
import time
import signal

def handler(signum, frame):
    raise TimeoutError("Generation timed out")

# Set 60-second timeout
signal.signal(signal.SIGALRM, handler)
signal.alarm(60)

try:
    start_time = time.time()
    proposal = proposal_generator.generate_proposal(extracted_info, packages)
    end_time = time.time()
    
    print(f"Generation completed in {end_time - start_time:.2f} seconds")
    print("First 100 chars of proposal:")
    print(proposal[:100] + "...")
    print("Test completed successfully!")
except TimeoutError:
    print("Generation timed out after 60 seconds")
    print("There might be an issue with Ollama's response time")
except Exception as e:
    print(f"Error during generation: {e}")
finally:
    signal.alarm(0)  # Disable the alarm
