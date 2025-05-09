import requests
import logging
import random
import time
from pathlib import Path
import os
from typing import Dict, List, Optional, Union, Any

logger = logging.getLogger(__name__)

def get_weather_forecast(lat: float, lon: float) -> Dict:
    """Get weather forecast from Open-Meteo API."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to get weather forecast: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return {}

def get_coordinates(place_name: str) -> Optional[Dict[str, float]]:
    """Convert place name to coordinates using Nominatim API."""
    try:
        # Encode the place name for URL
        encoded_place = requests.utils.quote(place_name)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_place}&format=json"
        
        # Nominatim requires a user agent
        headers = {"User-Agent": "TravelRAGApp/1.0"}
        
        # Respect usage policy with a delay
        time.sleep(1)
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return {"lat": float(data[0]["lat"]), "lon": float(data[0]["lon"])}
        return None
    except Exception as e:
        logger.error(f"Error getting coordinates for {place_name}: {e}")
        return None

def get_country_info(country_code: str) -> List[Dict]:
    """Get country information from REST Countries API."""
    try:
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            # Try with country name if code fails
            url = f"https://restcountries.com/v3.1/name/{country_code}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            logger.warning(f"Failed to get country info: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting country info: {e}")
        return []

def get_exchange_rate(base: str = "USD", target: str = "EUR") -> Optional[float]:
    """Get currency exchange rate from open.er-api.com."""
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["rates"].get(target)
        else:
            logger.warning(f"Failed to get exchange rate: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error getting exchange rate: {e}")
        return None

def get_local_attractions(lat: float, lon: float, radius: int = 1000) -> List[Dict]:
    """Get local attractions from OpenStreetMap using Overpass API."""
    try:
        query = f"""
        [out:json];
        node["tourism"](around:{radius},{lat},{lon});
        out body;
        """
        response = requests.post(
            "https://overpass-api.de/api/interpreter", 
            data={"data": query}
        )
        if response.status_code == 200:
            data = response.json()
            attractions = []
            for element in data.get("elements", []):
                if "tags" in element:
                    attraction = {
                        "name": element["tags"].get("name", "Unnamed Attraction"),
                        "type": element["tags"].get("tourism", "attraction"),
                        "lat": element.get("lat"),
                        "lon": element.get("lon")
                    }
                    attractions.append(attraction)
            return attractions
        else:
            logger.warning(f"Failed to get local attractions: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting local attractions: {e}")
        return []

def get_wikivoyage_info(destination: str) -> Dict:
    """Extract travel guide content from Wikivoyage."""
    try:
        # Replace spaces with underscores and capitalize first letters
        formatted_dest = destination.replace(" ", "_").title()
        url = f"https://en.wikivoyage.org/w/api.php?action=query&prop=extracts&titles={formatted_dest}&format=json&explaintext=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if page_id != "-1":  # -1 means page not found
                    return {
                        "title": page_data.get("title", ""),
                        "extract": page_data.get("extract", "")
                    }
            return {}
        else:
            logger.warning(f"Failed to get Wikivoyage info: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Error getting Wikivoyage info: {e}")
        return {}

def get_continent_from_country(country: str) -> str:
    """Get continent based on country name (simplified version)."""
    # This is a simplified mapping - in production you'd use a complete database
    continent_mapping = {
        "United States": "North America",
        "Canada": "North America",
        "Mexico": "North America",
        "Brazil": "South America",
        "Argentina": "South America",
        "Colombia": "South America",
        "Peru": "South America",
        "United Kingdom": "Europe",
        "France": "Europe",
        "Germany": "Europe",
        "Italy": "Europe",
        "Spain": "Europe",
        "Greece": "Europe",
        "China": "Asia",
        "Japan": "Asia",
        "India": "Asia",
        "Thailand": "Asia",
        "Vietnam": "Asia",
        "Australia": "Oceania",
        "New Zealand": "Oceania",
        "Egypt": "Africa",
        "South Africa": "Africa",
        "Kenya": "Africa",
        "Morocco": "Africa"
    }
    
    # Try direct lookup
    if country in continent_mapping:
        return continent_mapping[country]
    
    # Try to find a partial match
    for known_country, continent in continent_mapping.items():
        if known_country in country or country in known_country:
            return continent
    
    # Default fallback
    return "Unknown"

def get_reverse_geocoding(lat: float, lon: float) -> Dict:
    """Get location information from coordinates using Nominatim reverse geocoding."""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "TravelRAGApp/1.0"}
        
        # Respect usage policy with a delay
        time.sleep(1)
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to get reverse geocoding: {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Error getting reverse geocoding: {e}")
        return {}