import re
import json
import logging
from src.generation.llm_wrapper import OllamaWrapper

logger = logging.getLogger(__name__)

class EmailExtractor:
    """Extract structured information from customer emails."""
    
    def __init__(self, ollama_client=None):
        """Initialize the email extractor."""
        self.ollama = ollama_client or OllamaWrapper()
    
    def extract_from_email(self, email_text):
        """
        Extract key travel information from customer email.
        
        Args:
            email_text: The raw email text
            
        Returns:
            dict: Extracted information (destination, dates, travelers, budget, interests)
        """
        # Using LLM to extract structured information in a consistent format
        prompt = f"""
        Extract the following information from this customer email for a travel agency.
        
        Format the output in this exact format:
        travel_date: [extract dates or NONE if not mentioned]
        destination: [extract destination or NONE if not mentioned]
        travel_type: [extract type of travel (vacation, business, honeymoon, etc.) or NONE if not mentioned]
        duration: [extract duration in days or NONE if not mentioned]
        budget: $[extract budget amount or NONE if not mentioned]
        num_travelers: [extract number of travelers or NONE if not mentioned]
        optional_details: [extract any other relevant details like preferences, requirements, etc.]
        hotel_pref: [extract hotel preferences or NONE if not mentioned]
        flight_pref: [extract flight preferences or NONE if not mentioned]
        allergy: [extract any allergies or NONE if not mentioned]

        Email:
        {email_text}
        """
        
        try:
            # LLM extraction
            response = self.ollama.generate(prompt)
            
            # Parse the structured output
            extracted_data = self._parse_structured_output(response)
                
            # Add 'interests' key for compatibility with existing code
            if 'optional_details' in extracted_data and extracted_data['optional_details'] != 'NONE':
                extracted_data['interests'] = extracted_data['optional_details']
            else:
                extracted_data['interests'] = None
                
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting information from email: {e}")
            return {
                'destination': None,
                'travel_date': None,
                'travelers': None,
                'budget': None,
                'interests': None,
                'duration': None,
                'travel_type': None
            }
    
    def _parse_structured_output(self, response):
        """
        Parse the structured output from the LLM.
        
        Args:
            response: The LLM response string
            
        Returns:
            dict: Parsed structured data
        """
        result = {}
        
        # Parse line by line
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Skip empty values or placeholders
                if value.lower() == 'none' or not value:
                    value = None
                
                # Map to our expected keys
                if key == 'travel_date':
                    result['dates'] = value
                    result['travel_date'] = value  # Keep original too
                elif key == 'num_travelers':
                    result['travelers'] = value
                    result['num_travelers'] = value  # Keep original too
                else:
                    # Add all other keys directly
                    result[key] = value
        
        # Ensure all required fields exist for compatibility
        required_fields = ['destination', 'dates', 'travelers', 'budget', 'duration', 'travel_type']
        for field in required_fields:
            if field not in result:
                result[field] = None
                
        # Also ensure interest field exists (map from optional_details if needed)
        if 'interests' not in result and 'optional_details' in result:
            result['interests'] = result['optional_details']
        elif 'interests' not in result:
            result['interests'] = None
            
        return result