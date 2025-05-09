from flask import Flask, request, jsonify
from src.email_processing.extractor import EmailExtractor
from src.email_processing.parser import EmailParser
from src.retrieval.query_builder import QueryBuilder
from src.retrieval.retriever import PackageRetriever
from src.generation.proposal_generator import ProposalGenerator

app = Flask(__name__)

@app.route('/generate-proposal', methods=['POST'])
def generate_proposal():
    email_content = request.json.get('email_content')
    
    # Extract information from the email
    extractor = EmailExtractor()
    parser = EmailParser()
    parsed_data = parser.parse_email(email_content)
    
    destination = extractor.extract_destination(parsed_data)
    dates = extractor.extract_dates(parsed_data)
    travelers = extractor.extract_travelers(parsed_data)
    budget = extractor.extract_budget(parsed_data)
    interests = extractor.extract_interests(parsed_data)
    
    # Build query and retrieve packages
    query_builder = QueryBuilder()
    query = query_builder.build_query(destination, dates, travelers, budget, interests)
    
    retriever = PackageRetriever()
    relevant_packages = retriever.retrieve_packages(query)
    
    # Generate proposal
    proposal_generator = ProposalGenerator()
    proposal = proposal_generator.generate_proposal(relevant_packages)
    
    return jsonify({'proposal': proposal})

if __name__ == '__main__':
    app.run(debug=True)