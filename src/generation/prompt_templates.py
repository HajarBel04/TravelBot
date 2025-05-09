from typing import Dict, Optional

def get_proposal_template(customer_info, packages_text, itinerary=""):
    """
    Generate a prompt template for proposal generation.
    
    Args:
        customer_info: Dictionary with extracted customer information
        packages_text: Formatted text of relevant packages
        itinerary: Pre-generated itinerary to include in the proposal
        
    Returns:
        str: The prompt template
    """
    destination = customer_info.get('destination', 'the requested destination')
    dates = customer_info.get('dates', 'the requested dates')
    travelers = customer_info.get('travelers', 'the travelers')
    budget = customer_info.get('budget', 'the specified budget')
    interests = customer_info.get('interests', 'the client interests')
    hotel_pref = customer_info.get('hotel_pref', 'Not specified')
    flight_pref = customer_info.get('flight_pref', 'Not specified')
    
    template = f"""
    Create a detailed and personalized travel itinerary for a trip with the following parameters:
    
    Travel Information:
    - Destination: {destination}
    - Travel Dates: {dates}
    - Travelers: {travelers}
    - Budget: {budget}
    - Interests/Preferences: {interests}
    - Hotel Preferences: {hotel_pref}
    - Flight Preferences: {flight_pref}
    
    Your response should be a direct itinerary presentation with:
    1. A clear title and overview
    2. A day-by-day breakdown with specific activities, timings, and locations
    3. Practical information about accommodations and transportation
    
    Do not format this as an email or letter. Present it as a professional itinerary document.
    """
    
    return template

def get_itinerary_template(destination, travel_type="vacation", days=5, travelers=None, budget=None, interests=None):
    """
    Generate a prompt template for itinerary generation.
    
    Args:
        destination: The travel destination
        travel_type: Type of travel (vacation, business, etc.)
        days: Number of days for the itinerary
        travelers: Number of travelers (optional)
        budget: Budget for the trip (optional)
        interests: Special interests or activities (optional)
        
    Returns:
        str: The prompt template for generating an itinerary
    """
    # Handle None values with defaults
    destination = destination or "your destination"
    travel_type = travel_type or "vacation"
    
    budget_text = f"The total budget is approximately {budget}." if budget else ""
    travelers_text = f"This plan is for {travelers} traveler(s)." if travelers else ""
    interests_text = f"The travelers are interested in: {interests}." if interests else ""
    
    # Create base template
    template = f"""
    Create a DETAILED {days}-day travel itinerary for a {travel_type} to {destination}.
    
    Client Information:
    - Destination: {destination}
    - Trip Type: {travel_type}
    - Duration: {days} days
    - Number of Travelers: {travelers if travelers else "Not specified"}
    - Budget: {budget if budget else "Not specified"}
    - Special Interests: {interests if interests else "Not specified"}
    
    Format your response DIRECTLY as a professional itinerary with:
    
    # {days}-Day {travel_type.title()} Itinerary for {destination}
    
    ## Overview
    Begin with a brief overview of what makes this trip special. {budget_text} {travelers_text} {interests_text}
    """
    
    # Add explicit structure for each day
    for day in range(1, days + 1):
        template += f"""
    ## Day {day}
    
    ### Morning (8:00 AM - 12:00 PM)
    - Include SPECIFIC breakfast location recommendations with actual restaurant names
    - List SPECIFIC attractions, sites or activities (include actual names, not generic descriptions)
    - Include estimated duration for each activity and travel time between locations
    
    ### Afternoon (12:00 PM - 5:00 PM)
    - Recommend SPECIFIC lunch spots with actual restaurant names
    - List SPECIFIC afternoon activities with actual location names
    - Include estimated duration and any entrance fees or special notes
    
    ### Evening (5:00 PM - 10:00 PM)
    - Recommend SPECIFIC dinner restaurants with actual names
    - Include SPECIFIC evening activities or entertainment options
    - Add practical information (dress code, reservations needed, etc.)
    """
    
    # Add practical information section
    template += """
    ## Practical Information
    
    ### Recommended Accommodations
    - Provide 2-3 SPECIFIC hotel/accommodation recommendations with actual names in different price ranges
    
    ### Transportation Options
    - Include detailed information about getting around (public transport, rentals, etc.)
    
    ### Estimated Costs
    - Break down estimated costs for accommodations, meals, attractions, and transportation
    
    Make sure all recommendations are appropriate for the destination and match the client's travel style.
    Use ACTUAL names of attractions, restaurants, and hotels that exist in the destination.
    Be extremely specific and detailed, avoiding generic suggestions.
    Include insider tips that would make their experience more authentic and memorable.
    DO NOT format this as an email or letter. Present it as a professional travel document.
    """
    
    return template

def get_travel_package_template(package: Dict) -> str:
    """Formats a travel package into a readable string."""
    return (
        f"Package Name: {package['name']}\n"
        f"Destination: {package['destination']}\n"
        f"Dates: {package['dates']}\n"
        f"Budget: {package['budget']}\n"
        f"Highlights: {package['highlights']}\n"
        "-----------------------------------\n"
    )