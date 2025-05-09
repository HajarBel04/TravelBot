#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def fix_extractor():
    """Fix the email extractor to avoid duplicate fields with different values."""
    
    extractor_path = Path("src/email_processing/extractor.py")
    if not extractor_path.exists():
        print(f"Error: Cannot find extractor file at {extractor_path}")
        return False
    
    # Read the current file
    with open(extractor_path, 'r') as f:
        content = f.read()
    
    # Make a backup
    backup_path = extractor_path.with_suffix('.py.bak')
    with open(backup_path, 'w') as f:
        f.write(content)
    
    # Find and replace the _parse_structured_output method
    if '_parse_structured_output' in content:
        # Replace the method with an improved version
        start_marker = 'def _parse_structured_output(self, response):'
        end_marker = 'return result'
        
        # Find the method boundaries
        start_idx = content.find(start_marker)
        if start_idx == -1:
            print("Could not find _parse_structured_output method")
            return False
            
        # Find the end of the method (looking for "return result")
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            print("Could not find end of _parse_structured_output method")
            return False
            
        # Get end of the line containing "return result"
        end_idx = content.find('\n', end_idx)
        if end_idx == -1:
            end_idx = len(content)
        
        # Replace the method with improved version
        improved_method = '''def _parse_structured_output(self, response):
        """
        Parse the structured output from the LLM.
        
        Args:
            response: The LLM response string
            
        Returns:
            dict: Parsed structured data
        """
        result = {}
        
        # Parse line by line
        lines = response.strip().split('\\n')
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
            
        return result'''
        
        # Replace the method
        new_content = content[:start_idx] + improved_method + content[end_idx:]
        
        # Write the updated file
        with open(extractor_path, 'w') as f:
            f.write(new_content)
            
        print(f"Updated _parse_structured_output method in {extractor_path}")
        print(f"Backup saved to {backup_path}")
        return True
    else:
        print("Could not find _parse_structured_output method in extractor file")
        return False

if __name__ == "__main__":
    fix_extractor()