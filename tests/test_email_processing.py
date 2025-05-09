#travel-rag-system/tests/test_email_processing.py
from src.email_processing.extractor import EmailExtractor
from src.email_processing.parser import EmailParser

def test_email_extraction():
    raw_email = """
    Subject: Vacation Plans
    Hi there,
    I'm planning a trip to Paris from 2023-06-01 to 2023-06-10. 
    I will be traveling with my family, which includes my wife and two kids. 
    Our budget is around $5000, and we are interested in sightseeing and local cuisine.
    Thanks!
    """
    
    extractor = EmailExtractor()
    parser = EmailParser()
    
    structured_data = parser.parse_email(raw_email)
    
    destination = extractor.extract_destination(structured_data)
    dates = extractor.extract_dates(structured_data)
    travelers = extractor.extract_travelers(structured_data)
    budget = extractor.extract_budget(structured_data)
    interests = extractor.extract_interests(structured_data)
    
    assert destination == "Paris"
    assert dates == ("2023-06-01", "2023-06-10")
    assert travelers == ["wife", "two kids"]
    assert budget == 5000
    assert interests == ["sightseeing", "local cuisine"]

def test_email_parsing():
    raw_email = """
    Subject: Business Trip
    Hello,
    I need to travel to New York from 2023-07-15 to 2023-07-20 for a conference. 
    I will be going alone and my budget is $3000. 
    I'm interested in hotels and transportation.
    Regards,
    """
    
    parser = EmailParser()
    structured_data = parser.parse_email(raw_email)
    
    assert structured_data['destination'] == "New York"
    assert structured_data['dates'] == ("2023-07-15", "2023-07-20")
    assert structured_data['travelers'] == ["alone"]
    assert structured_data['budget'] == 3000
    assert structured_data['interests'] == ["hotels", "transportation"]