import logging
from src.generation.llm_wrapper import OllamaWrapper
from src.generation.prompt_templates import get_proposal_template, get_itinerary_template

logger = logging.getLogger(__name__)

class ProposalGenerator:
    """Generates travel proposals based on customer information and relevant packages."""
    
    def __init__(self, ollama_client=None):
        """Initialize the proposal generator."""
        self.ollama = ollama_client or OllamaWrapper()
    
    def generate_proposal(self, customer_info, packages):
        """
        Generate a detailed travel proposal based on customer information.
        
        Args:
            customer_info: Dictionary with extracted customer information
            packages: List of relevant travel packages (used for inspiration but not directly mentioned)
            
        Returns:
            str: Generated detailed proposal text with day-by-day itinerary
        """
        try:
            # Extract useful information from packages to inspire the proposal
            activities = []
            possible_destinations = []
            price_range = None
            weather_data = None
            country_info = None
            local_attractions = []
            destination_guide = None
            
            for package in packages:
                # Collect regular information
                if package.get('activities'):
                    if isinstance(package['activities'], list):
                        for activity in package['activities']:
                            if isinstance(activity, dict) and 'name' in activity:
                                activities.append(activity['name'])
                            elif isinstance(activity, str):
                                activities.append(activity)
                    else:
                        activities.extend(package.get('activities', []))
                        
                if package.get('location'):
                    possible_destinations.append(package.get('location'))
                elif package.get('destination'):
                    possible_destinations.append(package.get('destination'))
                    
                if package.get('price'):
                    if isinstance(package['price'], dict) and 'amount' in package['price']:
                        package_price = package['price']['amount']
                    else:
                        package_price = package.get('price')
                        
                    if not price_range or package_price < price_range:
                        price_range = package_price
                
                # Collect enriched data
                if package.get('weather_data') and not weather_data:
                    weather_data = package.get('weather_data')
                    
                if package.get('country') and package.get('country') != "Unknown" and not country_info:
                    country_info = {
                        'name': package.get('country'),
                        'continent': package.get('continent', 'Unknown')
                    }
                    
                if package.get('local_info') and not country_info:
                    local_info = package.get('local_info')
                    country_info = {
                        'name': local_info.get('capital', 'Unknown'),
                        'currency': local_info.get('currency', 'Unknown'),
                        'languages': local_info.get('languages', 'Unknown')
                    }
                    
                # Get local attractions beyond standard activities
                if isinstance(package.get('activities'), list):
                    for activity in package.get('activities', []):
                        if isinstance(activity, dict) and activity.get('name') and not activity.get('included_in_package', True):
                            local_attractions.append(activity)
                            
                # Get destination guide information
                if package.get('destination_guide') and not destination_guide:
                    destination_guide = package.get('destination_guide')
            
            # Remove duplicates
            activities = list(set(activities))
            possible_destinations = list(set(possible_destinations))
            
            # Use destination from customer info or from packages
            destination = customer_info.get('destination')
            if not destination and possible_destinations:
                destination = possible_destinations[0]
            
            # If no destination is specified, use a generic one
            if not destination:
                destination = "your chosen destination"
            
            # Generate detailed itinerary
            duration_days = 5  # Default to 5 days if not specified
            if customer_info.get('duration') and customer_info['duration'] not in [None, 'None']:
                try:
                    duration_str = customer_info['duration'].split()[0]  # Extract just the number
                    duration_days = int(duration_str)
                except (ValueError, IndexError):
                    pass
            
            travel_type = customer_info.get('travel_type') or "vacation"
            travelers = customer_info.get('travelers') or "2"
            budget = customer_info.get('budget')
            
            # Activities and interests for the itinerary
            interests = []
            if customer_info.get('interests'):
                interests.append(customer_info.get('interests'))
            if activities:
                interests.extend(activities[:5])  # Add up to 5 activities
                
            interests_text = ", ".join(interests) if interests else ""
            
            # Generate the itinerary prompt with additional details
            itinerary_prompt = get_itinerary_template(
                destination=destination,
                travel_type=travel_type,
                days=duration_days,
                travelers=travelers,
                budget=budget,
                interests=interests_text
            )
            
            # Add enriched information to the prompt
            if country_info:
                if isinstance(country_info, dict) and 'name' in country_info:
                    country_name = country_info['name']
                    continent = country_info.get('continent', 'Unknown')
                    itinerary_prompt += f"\n\nDestination Information: {destination} is located in {country_name}, which is in {continent}."
                    
                    if 'currency' in country_info:
                        itinerary_prompt += f" The local currency is {country_info['currency']}."
                    if 'languages' in country_info:
                        itinerary_prompt += f" The local language(s) include {country_info['languages']}."
            
            # Add weather information if available
            if weather_data and isinstance(weather_data, dict) and 'daily' in weather_data:
                try:
                    daily = weather_data['daily']
                    if 'temperature_2m_max' in daily and 'temperature_2m_min' in daily and len(daily['temperature_2m_max']) > 0:
                        avg_max = sum(daily['temperature_2m_max'][:7]) / min(7, len(daily['temperature_2m_max']))
                        avg_min = sum(daily['temperature_2m_min'][:7]) / min(7, len(daily['temperature_2m_min']))
                        
                        itinerary_prompt += f"\n\nWeather Information: The current weather forecast shows temperatures ranging from {avg_min:.1f}°C to {avg_max:.1f}°C."
                        
                        if 'precipitation_sum' in daily and len(daily['precipitation_sum']) > 0:
                            total_precip = sum(daily['precipitation_sum'][:7])
                            if total_precip > 10:
                                itinerary_prompt += f" There may be some rainfall during your visit, so pack accordingly."
                            else:
                                itinerary_prompt += f" The forecast shows minimal precipitation, so expect mostly dry conditions."
                except Exception as e:
                    logger.warning(f"Error processing weather data: {e}")
            
            # Add local attractions if available
            if local_attractions:
                itinerary_prompt += "\n\nLocal Attractions to Consider:"
                for i, attraction in enumerate(local_attractions[:5], 1):
                    name = attraction.get('name', 'Local attraction')
                    desc = attraction.get('description', '')
                    itinerary_prompt += f"\n{i}. {name}: {desc}"
            
            # Add destination guide excerpt if available
            if destination_guide and isinstance(destination_guide, dict) and 'extract' in destination_guide:
                # Use just a brief excerpt to avoid overwhelming the LLM
                excerpt = destination_guide['extract'][:500] + "..." if len(destination_guide['extract']) > 500 else destination_guide['extract']
                itinerary_prompt += f"\n\nDestination Guide: {excerpt}"
            
            # Generate the detailed itinerary - skip email formatting, just focus on the core itinerary
            system_prompt_itinerary = """You are an expert travel planner creating personalized travel itineraries.
            Write a VERY detailed and specific day-by-day itinerary with specific locations, attractions, restaurants, 
            and activities for each part of the day. Include actual names of places, not generic descriptions.
            Be professional, specific, and informative. Make realistic time allocations and consider travel time between activities.
            Do NOT use an email format - just present the itinerary directly in a clean, professional format.
            No introduction or conclusion paragraphs - focus on the itinerary itself."""
            
            # Add weather and cultural awareness to system prompt
            if weather_data:
                system_prompt_itinerary += "\nConsider the weather conditions mentioned when planning outdoor activities."
            
            if country_info:
                system_prompt_itinerary += "\nIncorporate cultural context and local customs of the destination when appropriate."
            
            itinerary = self.ollama.generate(itinerary_prompt, system_prompt_itinerary)
            
            # Clean up the itinerary to remove any email-like formatting that might have been added
            itinerary = self._clean_itinerary_format(itinerary)
            
            # Add additional information sections after the main itinerary
            enriched_info = ""
            
            if country_info and isinstance(country_info, dict) and 'name' in country_info:
                enriched_info += f"\n\n## Destination Information\n"
                enriched_info += f"Country: {country_info['name']}\n"
                if 'continent' in country_info:
                    enriched_info += f"Continent: {country_info['continent']}\n"
                if 'currency' in country_info:
                    enriched_info += f"Currency: {country_info['currency']}\n"
                if 'languages' in country_info:
                    enriched_info += f"Languages: {country_info['languages']}\n"
            
            if weather_data and isinstance(weather_data, dict) and 'daily' in weather_data:
                try:
                    daily = weather_data['daily']
                    if 'time' in daily and 'temperature_2m_max' in daily and 'temperature_2m_min' in daily:
                        enriched_info += f"\n\n## Weather Forecast\n"
                        days = min(5, len(daily['time']))
                        for i in range(days):
                            date = daily['time'][i] if i < len(daily['time']) else "Unknown"
                            max_temp = daily['temperature_2m_max'][i] if i < len(daily['temperature_2m_max']) else "N/A"
                            min_temp = daily['temperature_2m_min'][i] if i < len(daily['temperature_2m_min']) else "N/A"
                            precip = daily['precipitation_sum'][i] if 'precipitation_sum' in daily and i < len(daily['precipitation_sum']) else "N/A"
                            
                            enriched_info += f"- {date}: {min_temp}°C to {max_temp}°C, Precipitation: {precip}mm\n"
                except Exception as e:
                    logger.warning(f"Error formatting weather forecast: {e}")
            
            # Add the enriched info to the itinerary if available
            if enriched_info:
                itinerary += "\n" + enriched_info
            
            return itinerary
            
        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            return self._generate_fallback_proposal(customer_info)
    
    def _clean_itinerary_format(self, itinerary):
        """
        Remove email-like formatting from the itinerary.
        
        Args:
            itinerary: The generated itinerary text
            
        Returns:
            str: Cleaned itinerary text
        """
        # Remove email-like greetings
        lines = itinerary.split('\n')
        cleaned_lines = []
        skip_line = False
        
        for line in lines:
            # Skip common email greeting patterns
            if any(greeting in line.lower() for greeting in ['dear', 'hello', 'hi ', 'greetings', 'thank you', 'regards', 'sincerely']):
                skip_line = True
                continue
                
            # If we were skipping lines and found a meaningful header, start including again
            if skip_line and (line.startswith('#') or line.startswith('## ')):
                skip_line = False
                
            if not skip_line:
                cleaned_lines.append(line)
                
        return '\n'.join(cleaned_lines)
    
    def _generate_fallback_proposal(self, customer_info):
        """
        Generate a simple fallback proposal if the main generation fails.
        
        Args:
            customer_info: Dictionary with extracted customer information
            
        Returns:
            str: A simple proposal
        """
        destination = customer_info.get('destination', 'your chosen destination')
        return f"""
        # Detailed Travel Itinerary for {destination}
        
        We're currently preparing your detailed itinerary. Our travel experts will create a 
        comprehensive day-by-day plan based on your preferences and interests.
        
        ## Your Destination: {destination}
        
        We'll include:
        - Specific accommodation recommendations
        - Day-by-day activities with timing
        - Local restaurant suggestions
        - Transportation options
        - Estimated costs
        - Weather forecast and local conditions
        - Cultural information and travel tips
        
        Your complete itinerary will be ready shortly.
        """