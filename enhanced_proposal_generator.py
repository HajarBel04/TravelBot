import logging
from src.generation.llm_wrapper import OllamaWrapper
from src.generation.prompt_templates import get_proposal_template, get_itinerary_template

logger = logging.getLogger(__name__)

class ProposalGenerator:
    """Generates travel proposals based on customer information and relevant packages with enhanced data utilization."""
    
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
            enriched_data = self._extract_enriched_data(packages)
            
            # Use destination from customer info or from packages
            destination = customer_info.get('destination')
            if not destination and enriched_data['possible_destinations']:
                destination = enriched_data['possible_destinations'][0]
            
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
            if enriched_data['activities']:
                interests.extend(enriched_data['activities'][:5])  # Add up to 5 activities
                
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
            
            # Add enriched information to the prompt in a structured way
            itinerary_prompt += self._format_enriched_data_for_prompt(destination, enriched_data)
            
            # Generate the detailed itinerary
            system_prompt_itinerary = self._get_enhanced_system_prompt(enriched_data)
            
            itinerary = self.ollama.generate(itinerary_prompt, system_prompt_itinerary)
            
            # Clean up the itinerary to remove any email-like formatting
            itinerary = self._clean_itinerary_format(itinerary)
            
            # Add additional information sections after the main itinerary
            enriched_info = self._format_enriched_data_for_appendix(enriched_data)
            
            # Add the enriched info to the itinerary if available
            if enriched_info:
                itinerary += "\n" + enriched_info
            
            return itinerary
            
        except Exception as e:
            logger.error(f"Error generating proposal: {e}")
            return self._generate_fallback_proposal(customer_info)
    
    def _extract_enriched_data(self, packages):
        """Extract all enriched data from packages into a structured format."""
        result = {
            'activities': [],
            'possible_destinations': [],
            'price_range': None,
            'weather_data': None,
            'country_info': None,
            'local_attractions': [],
            'destination_guide': None,
            'has_beach': False,
            'has_mountain': False,
            'has_city': False,
            'highlights': []
        }
        
        for package in packages:
            # Collect regular information
            if package.get('activities'):
                if isinstance(package['activities'], list):
                    for activity in package['activities']:
                        if isinstance(activity, dict) and 'name' in activity:
                            activity_name = activity['name']
                            if activity_name not in result['activities']:
                                result['activities'].append(activity_name)
                        elif isinstance(activity, str) and activity not in result['activities']:
                            result['activities'].append(activity)
                            
            if package.get('location'):
                if package.get('location') not in result['possible_destinations']:
                    result['possible_destinations'].append(package.get('location'))
            elif package.get('destination'):
                if package.get('destination') not in result['possible_destinations']:
                    result['possible_destinations'].append(package.get('destination'))
                    
            if package.get('price'):
                if isinstance(package['price'], dict) and 'amount' in package['price']:
                    package_price = package['price']['amount']
                else:
                    package_price = package.get('price')
                    
                if not result['price_range'] or package_price < result['price_range']:
                    result['price_range'] = package_price
            
            # Collect enriched data
            if package.get('weather_data') and not result['weather_data']:
                result['weather_data'] = package.get('weather_data')
                
            if package.get('country') and package.get('country') != "Unknown" and not result['country_info']:
                result['country_info'] = {
                    'name': package.get('country'),
                    'continent': package.get('continent', 'Unknown')
                }
                    
            if package.get('local_info') and not result['country_info']:
                local_info = package.get('local_info')
                result['country_info'] = {
                    'capital': local_info.get('capital', 'Unknown'),
                    'currency': local_info.get('currency', 'Unknown'),
                    'languages': local_info.get('languages', 'Unknown')
                }
                    
            # Get local attractions beyond standard activities
            if isinstance(package.get('activities'), list):
                for activity in package.get('activities', []):
                    if isinstance(activity, dict) and activity.get('name') and not activity.get('included_in_package', True):
                        if activity not in result['local_attractions']:
                            result['local_attractions'].append(activity)
            
            # Check for specific features in package description and activities
            description = package.get('description', '').lower()
            if 'beach' in description or any('beach' in act.lower() for act in result['activities']):
                result['has_beach'] = True
            if 'mountain' in description or any('hik' in act.lower() for act in result['activities']):
                result['has_mountain'] = True
            if 'city' in description or any('museum' in act.lower() for act in result['activities']):
                result['has_city'] = True
                            
            # Get destination guide information
            if package.get('destination_guide') and not result['destination_guide']:
                result['destination_guide'] = package.get('destination_guide')
                
            # Get highlights
            if package.get('highlights') and isinstance(package.get('highlights'), list):
                for highlight in package.get('highlights'):
                    if highlight not in result['highlights']:
                        result['highlights'].append(highlight)
        
        return result
    
    def _format_enriched_data_for_prompt(self, destination, enriched_data):
        """Format enriched data as additional sections for the itinerary prompt."""
        prompt_additions = "\n\n# Additional Information for Planning\n"
        
        # Add destination and country information
        if enriched_data['country_info']:
            prompt_additions += "\n## Destination Information\n"
            
            if isinstance(enriched_data['country_info'], dict):
                if 'name' in enriched_data['country_info']:
                    country_name = enriched_data['country_info']['name']
                    continent = enriched_data['country_info'].get('continent', 'Unknown')
                    prompt_additions += f"{destination} is located in {country_name}, which is in {continent}.\n"
                    
                if 'currency' in enriched_data['country_info']:
                    prompt_additions += f"The local currency is {enriched_data['country_info']['currency']}. "
                    
                if 'languages' in enriched_data['country_info']:
                    prompt_additions += f"The local language(s) include {enriched_data['country_info']['languages']}.\n"
                    
                if 'capital' in enriched_data['country_info']:
                    prompt_additions += f"The capital city is {enriched_data['country_info']['capital']}.\n"
        
        # Add weather information
        if enriched_data['weather_data'] and isinstance(enriched_data['weather_data'], dict) and 'daily' in enriched_data['weather_data']:
            try:
                daily = enriched_data['weather_data']['daily']
                if 'temperature_2m_max' in daily and 'temperature_2m_min' in daily and len(daily['temperature_2m_max']) > 0:
                    avg_max = sum(daily['temperature_2m_max'][:7]) / min(7, len(daily['temperature_2m_max']))
                    avg_min = sum(daily['temperature_2m_min'][:7]) / min(7, len(daily['temperature_2m_min']))
                    
                    prompt_additions += f"\n## Weather Information\n"
                    prompt_additions += f"Current weather forecast shows temperatures ranging from {avg_min:.1f}°C to {avg_max:.1f}°C.\n"
                    
                    if 'precipitation_sum' in daily and len(daily['precipitation_sum']) > 0:
                        total_precip = sum(daily['precipitation_sum'][:7])
                        if total_precip > 10:
                            prompt_additions += f"There may be some rainfall during your visit, so pack accordingly.\n"
                        else:
                            prompt_additions += f"The forecast shows minimal precipitation, so expect mostly dry conditions.\n"
                            
                    # Add seasonal appropriate activities based on weather
                    if avg_max > 25:
                        prompt_additions += "This warm weather is perfect for beach activities, swimming, and outdoor dining.\n"
                    elif avg_max > 15:
                        prompt_additions += "This mild weather is ideal for sightseeing, hiking, and outdoor exploration.\n"
                    else:
                        prompt_additions += "The cool temperatures are suited for museums, indoor activities, and warm clothing.\n"
            except Exception as e:
                logger.warning(f"Error processing weather data: {e}")
        
        # Add destination type specific information
        if enriched_data['has_beach']:
            prompt_additions += "\n## Beach Information\n"
            prompt_additions += f"{destination} is known for its beautiful beaches and ocean activities. "
            prompt_additions += "Popular beach activities include swimming, sunbathing, snorkeling, and water sports. "
            prompt_additions += "Many resorts offer beach equipment rentals and ocean excursions.\n"
            
        if enriched_data['has_mountain']:
            prompt_additions += "\n## Mountain Information\n"
            prompt_additions += f"{destination} features stunning mountain landscapes and hiking opportunities. "
            prompt_additions += "Trails range from easy walks to challenging hikes with experienced guides available. "
            prompt_additions += "Mountain activities often include hiking, photography, cable car rides, and nature observation.\n"
            
        if enriched_data['has_city']:
            prompt_additions += "\n## Urban Information\n"
            prompt_additions += f"{destination} offers vibrant city life with cultural attractions and urban experiences. "
            prompt_additions += "City activities typically include museums, galleries, shopping, fine dining, and historical tours. "
            prompt_additions += "Public transportation is recommended for navigating the city areas.\n"
            
        # Add local attractions
        if enriched_data['local_attractions']:
            prompt_additions += "\n## Local Attractions\n"
            for i, attraction in enumerate(enriched_data['local_attractions'][:5], 1):
                if isinstance(attraction, dict):
                    name = attraction.get('name', 'Local attraction')
                    desc = attraction.get('description', '')
                    prompt_additions += f"{i}. {name}: {desc}\n"
                else:
                    prompt_additions += f"{i}. {attraction}\n"
        
        # Add destination highlights
        if enriched_data['highlights']:
            prompt_additions += "\n## Destination Highlights\n"
            for i, highlight in enumerate(enriched_data['highlights'][:5], 1):
                prompt_additions += f"{i}. {highlight}\n"
                
        # Add destination guide excerpt if available
        if enriched_data['destination_guide'] and isinstance(enriched_data['destination_guide'], dict) and 'extract' in enriched_data['destination_guide']:
            # Use just a brief excerpt to avoid overwhelming the LLM
            excerpt = enriched_data['destination_guide']['extract'][:500] + "..." if len(enriched_data['destination_guide']['extract']) > 500 else enriched_data['destination_guide']['extract']
            prompt_additions += f"\n## Travel Guide Information\n{excerpt}\n"
            
        return prompt_additions
    
    def _get_enhanced_system_prompt(self, enriched_data):
        """Generate a comprehensive system prompt based on available enriched data."""
        system_prompt = """You are an expert travel planner creating personalized travel itineraries.
        Write a VERY detailed and specific day-by-day itinerary with specific locations, attractions, restaurants, 
        and activities for each part of the day. Include actual names of places, not generic descriptions.
        Be professional, specific, and informative. Make realistic time allocations and consider travel time between activities.
        Do NOT use an email format - present the itinerary directly in a clean, professional format.
        No introduction or conclusion paragraphs - focus on the itinerary itself.
        """
        
        # Add weather awareness
        if enriched_data['weather_data']:
            system_prompt += "\nConsider the weather conditions mentioned when planning outdoor activities. "
            system_prompt += "Suggest appropriate clothing and gear based on the temperature and precipitation forecast."
        
        # Add cultural context
        if enriched_data['country_info']:
            system_prompt += "\nIncorporate cultural context and local customs of the destination when appropriate. "
            if isinstance(enriched_data['country_info'], dict) and 'languages' in enriched_data['country_info']:
                system_prompt += f"Include a few key phrases in the local language ({enriched_data['country_info'].get('languages')}). "
            if isinstance(enriched_data['country_info'], dict) and 'currency' in enriched_data['country_info']:
                system_prompt += f"Mention currency ({enriched_data['country_info'].get('currency')}) when discussing costs."
                
        # Add destination-specific guidance
        if enriched_data['has_beach']:
            system_prompt += "\nFor this beach destination, recommend specific beaches for different activities (swimming, snorkeling, surfing, etc). "
            system_prompt += "Include water temperature, tide information, and best times to visit each beach. "
            system_prompt += "Suggest water activities and beach-appropriate dining options."
            
        if enriched_data['has_mountain']:
            system_prompt += "\nFor this mountain destination, incorporate hiking trail difficulties, elevation gains, and estimated times. "
            system_prompt += "Suggest appropriate gear and clothing for mountain activities. "
            system_prompt += "Include information about altitude and acclimatization if relevant."
            
        if enriched_data['has_city']:
            system_prompt += "\nFor this urban destination, include information about public transportation, walking distances, and city districts. "
            system_prompt += "Recommend specific cultural institutions with their opening hours and ticket prices. "
            system_prompt += "Include urban dining experiences and shopping opportunities."
        
        return system_prompt
    
    def _format_enriched_data_for_appendix(self, enriched_data):
        """Format enriched data as appendix sections to add after the main itinerary."""
        appendix = ""
        
        # Add country and destination information
        if enriched_data['country_info'] and isinstance(enriched_data['country_info'], dict):
            appendix += f"\n\n## Destination Information\n"
            if 'name' in enriched_data['country_info']:
                appendix += f"Country: {enriched_data['country_info']['name']}\n"
            if 'continent' in enriched_data['country_info']:
                appendix += f"Continent: {enriched_data['country_info']['continent']}\n"
            if 'currency' in enriched_data['country_info']:
                appendix += f"Currency: {enriched_data['country_info']['currency']}\n"
            if 'languages' in enriched_data['country_info']:
                appendix += f"Languages: {enriched_data['country_info']['languages']}\n"
            if 'capital' in enriched_data['country_info']:
                appendix += f"Capital: {enriched_data['country_info']['capital']}\n"
        
        # Add weather forecast
        if enriched_data['weather_data'] and isinstance(enriched_data['weather_data'], dict) and 'daily' in enriched_data['weather_data']:
            try:
                daily = enriched_data['weather_data']['daily']
                if 'time' in daily and 'temperature_2m_max' in daily and 'temperature_2m_min' in daily:
                    appendix += f"\n\n## Weather Forecast\n"
                    days = min(5, len(daily['time']))
                    for i in range(days):
                        date = daily['time'][i] if i < len(daily['time']) else "Unknown"
                        max_temp = daily['temperature_2m_max'][i] if i < len(daily['temperature_2m_max']) else "N/A"
                        min_temp = daily['temperature_2m_min'][i] if i < len(daily['temperature_2m_min']) else "N/A"
                        precip = daily['precipitation_sum'][i] if 'precipitation_sum' in daily and i < len(daily['precipitation_sum']) else "N/A"
                        
                        appendix += f"- {date}: {min_temp}°C to {max_temp}°C, Precipitation: {precip}mm\n"
                        
                    # Add packing suggestions based on weather
                    appendix += "\n### Packing Suggestions Based on Weather\n"
                    avg_max = sum(daily['temperature_2m_max'][:days]) / days
                    avg_min = sum(daily['temperature_2m_min'][:days]) / days
                    
                    if avg_max > 28:
                        appendix += "- Light, breathable clothing\n- Sun hat and sunglasses\n- Strong sunscreen (SPF 30+)\n- Swimming attire\n- Light rain jacket\n"
                    elif avg_max > 20:
                        appendix += "- Light layers for daytime\n- Light jacket for evenings\n- Sun protection\n- Comfortable walking shoes\n- Light rain jacket\n"
                    elif avg_max > 10:
                        appendix += "- Sweaters and light jackets\n- Long pants\n- Comfortable walking shoes\n- Rain jacket\n- Light scarf\n"
                    else:
                        appendix += "- Warm coat or jacket\n- Layers for warmth\n- Hat, gloves, and scarf\n- Waterproof boots\n- Thermal undergarments if very cold\n"
            except Exception as e:
                logger.warning(f"Error formatting weather forecast: {e}")
        
        # Add local attractions
        if enriched_data['local_attractions']:
            appendix += "\n\n## Local Attractions\n"
            for i, attraction in enumerate(enriched_data['local_attractions'], 1):
                if isinstance(attraction, dict):
                    name = attraction.get('name', 'Local attraction')
                    desc = attraction.get('description', '')
                    duration = attraction.get('duration', '')
                    included = "Included in package" if attraction.get('included_in_package', False) else "Additional cost"
                    
                    appendix += f"### {i}. {name}\n"
                    appendix += f"Description: {desc}\n"
                    if duration:
                        appendix += f"Duration: {duration}\n"
                    appendix += f"Note: {included}\n\n"
                else:
                    appendix += f"### {i}. {attraction}\n\n"
        
        # Add travel tips based on destination type
        appendix += "\n\n## Travel Tips\n"
        
        if enriched_data['has_beach']:
            appendix += "\n### Beach Destination Tips\n"
            appendix += "- Apply sunscreen regularly, even on cloudy days\n"
            appendix += "- Stay hydrated with bottled or filtered water\n"
            appendix += "- Check tide schedules for water activities\n"
            appendix += "- Inquire about water safety and any dangerous marine life\n"
            appendix += "- Respect marine environments and wildlife\n"
            
        if enriched_data['has_mountain']:
            appendix += "\n### Mountain Destination Tips\n"
            appendix += "- Check weather forecasts before hiking\n"
            appendix += "- Bring layers even in warm weather as temperatures vary with altitude\n"
            appendix += "- Stay on marked trails\n"
            appendix += "- Bring sufficient water and snacks\n"
            appendix += "- Inform someone of your hiking plans\n"
            
        if enriched_data['has_city']:
            appendix += "\n### City Destination Tips\n"
            appendix += "- Use public transportation for efficiency\n"
            appendix += "- Be aware of pickpocketing in tourist areas\n"
            appendix += "- Check museum and attraction hours in advance\n"
            appendix += "- Look for city passes that bundle attractions\n"
            appendix += "- Try local specialties at authentic restaurants\n"
        
        # Add cultural tips if country info available
        if enriched_data['country_info']:
            appendix += "\n### Cultural Tips\n"
            appendix += "- Learn a few basic phrases in the local language\n"
            appendix += "- Research and respect local customs and etiquette\n"
            appendix += "- Dress appropriately for religious or cultural sites\n"
            appendix += "- Ask permission before photographing people\n"
            appendix += "- Respect local traditions and practices\n"
        
        return appendix
    
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