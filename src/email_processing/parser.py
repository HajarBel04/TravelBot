class EmailParser:
    def parse_email(self, raw_email):
        structured_data = {}
        
        # Example parsing logic (to be expanded based on actual email format)
        lines = raw_email.split('\n')
        for line in lines:
            if line.startswith("Destination:"):
                structured_data['destination'] = line.split(":", 1)[1].strip()
            elif line.startswith("Dates:"):
                structured_data['dates'] = line.split(":", 1)[1].strip()
            elif line.startswith("Travelers:"):
                structured_data['travelers'] = line.split(":", 1)[1].strip()
            elif line.startswith("Budget:"):
                structured_data['budget'] = line.split(":", 1)[1].strip()
            elif line.startswith("Interests:"):
                structured_data['interests'] = line.split(":", 1)[1].strip()
        
        return structured_data