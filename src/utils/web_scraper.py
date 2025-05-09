import requests
from bs4 import BeautifulSoup
import logging
import time
import random
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class TravelDataScraper:
    def __init__(self):
        self.user_agent = "TravelRAGResearchBot/1.0 (educational project)"
        self.delay_range = (1, 3)  # Ethical scraping delay in seconds
        
    def scrape_with_delay(self, url: str) -> Optional[BeautifulSoup]:
        """Make a request with ethical delay and return BeautifulSoup object."""
        try:
            # Add random delay for ethical scraping
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                logger.warning(f"Failed to scrape {url}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_unesco_sites(self) -> List[Dict]:
        """Scrape UNESCO World Heritage Sites."""
        sites = []
        url = "https://whc.unesco.org/en/list/"
        
        soup = self.scrape_with_delay(url)
        if not soup:
            return sites
        
        # Find all site listings
        for item in soup.select(".list_item"):
            try:
                name = item.select_one(".list_site").text.strip()
                country = item.select_one(".list_country").text.strip()
                category = item.select_one(".list_category").text.strip()
                
                # Get description if available
                description = ""
                descr_elem = item.select_one(".list_descr")
                if descr_elem:
                    description = descr_elem.text.strip()
                
                site = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "location": f"{name}, {country}",
                    "description": description,
                    "country": country,
                    "type": "UNESCO World Heritage Site",
                    "category": category,
                    "activities": ["Sightseeing", "Cultural Exploration", "Photography"],
                    "duration": "3 days",
                    "price": random.randint(500, 1500)
                }
                
                sites.append(site)
            except Exception as e:
                logger.error(f"Error processing UNESCO site: {e}")
                continue
        
        logger.info(f"Scraped {len(sites)} UNESCO sites")
        return sites
    
    def scrape_wikitravel_destinations(self, limit: int = 20) -> List[Dict]:
        """Scrape popular destinations from Wikitravel."""
        destinations = []
        url = "https://wikitravel.org/en/Main_Page"
        
        soup = self.scrape_with_delay(url)
        if not soup:
            return destinations
        
        # Find featured destinations and links to continent pages
        featured = soup.select(".featuredbox")
        continent_links = []
        
        for nav_item in soup.select("#quickbar a"):
            href = nav_item.get('href', '')
            if any(continent in href for continent in ['Europe', 'Asia', 'Africa', 'North_America', 'South_America', 'Oceania']):
                continent_links.append('https://wikitravel.org' + href)
        
        # Process featured destinations
        for item in featured:
            try:
                title_elem = item.select_one("h2, h3")
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                description = ""
                descr_elem = item.select_one("p")
                if descr_elem:
                    description = descr_elem.text.strip()
                
                # Find link
                link_elem = item.select_one("a")
                if not link_elem:
                    continue
                    
                link = link_elem['href']
                
                # Get more details from the destination page
                dest_url = f"https://wikitravel.org{link}"
                dest_soup = self.scrape_with_delay(dest_url)
                
                if not dest_soup:
                    continue
                
                # Build destination data
                activities = []
                highlights = []
                
                # Extract highlights (See section)
                see_section = dest_soup.find(id="See")
                if see_section:
                    section = see_section.parent.find_next("ul")
                    if section:
                        for li in section.find_all("li")[:5]:  # Limit to 5
                            highlights.append(li.text.strip())
                
                # Extract activities (Do section)
                do_section = dest_soup.find(id="Do")
                if do_section:
                    section = do_section.parent.find_next("ul")
                    if section:
                        for li in section.find_all("li")[:5]:  # Limit to 5
                            activities.append(li.text.strip())
                
                # Create destination dictionary
                destination = {
                    "id": str(uuid.uuid4()),
                    "name": f"Explore {title}",
                    "location": title,
                    "description": description,
                    "highlights": highlights,
                    "activities": activities or ["Sightseeing", "Local Cuisine", "Cultural Experience"],
                    "duration": f"{random.randint(3, 10)} days",
                    "price": random.randint(800, 3000)
                }
                
                destinations.append(destination)
                
                # Respect rate limits
                time.sleep(random.uniform(1, 2))
                
                # Check if we've reached the limit
                if len(destinations) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error processing Wikitravel destination: {e}")
                continue
        
        # If we need more destinations, explore continent pages
        if len(destinations) < limit:
            for continent_url in continent_links:
                if len(destinations) >= limit:
                    break
                    
                continent_soup = self.scrape_with_delay(continent_url)
                if not continent_soup:
                    continue
                
                # Find country links
                country_links = []
                
                for link in continent_soup.select("#bodyContent a"):
                    href = link.get('href', '')
                    if '/en/' in href and not any(x in href for x in [':', 'Main_Page', 'wikitravel']):
                        country_links.append('https://wikitravel.org' + href)
                
                # Process some random countries
                random.shuffle(country_links)
                for country_url in country_links[:3]:  # Limit to 3 countries per continent
                    if len(destinations) >= limit:
                        break
                        
                    country_soup = self.scrape_with_delay(country_url)
                    if not country_soup:
                        continue
                    
                    # Get country name
                    country_name = country_url.split('/')[-1].replace('_', ' ')
                    
                    # Extract country description
                    description = ""
                    first_p = country_soup.select_one("#bodyContent p")
                    if first_p:
                        description = first_p.text.strip()
                    
                    # Find cities or regions
                    cities = []
                    cities_section = country_soup.find(id="Cities")
                    if cities_section:
                        section = cities_section.parent.find_next("ul")
                        if section:
                            for li in section.find_all("li")[:5]:
                                city_text = li.text.strip()
                                cities.append(city_text)
                    
                    # If no cities found, try regions
                    if not cities:
                        regions_section = country_soup.find(id="Regions")
                        if regions_section:
                            section = regions_section.parent.find_next("ul")
                            if section:
                                for li in section.find_all("li")[:5]:
                                    region_text = li.text.strip()
                                    cities.append(region_text)
                    
                    # Create destination for country
                    if description:
                        destination = {
                            "id": str(uuid.uuid4()),
                            "name": f"Discover {country_name}",
                            "location": country_name,
                            "description": description,
                            "highlights": cities,
                            "activities": ["Sightseeing", "Local Cuisine", "Cultural Experience"],
                            "duration": f"{random.randint(7, 14)} days",
                            "price": random.randint(1200, 4000)
                        }
                        
                        destinations.append(destination)
                    
                    # Respect rate limits
                    time.sleep(random.uniform(1, 2))
        
        logger.info(f"Scraped {len(destinations)} Wikitravel destinations")
        return destinations
    
    def save_scraped_data(self, data: List[Dict], output_file: str):
        """Save scraped data to a JSON file."""
        try:
            # Create output directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and merge with existing data
            existing_data = []
            if output_path.exists():
                try:
                    with open(output_path, 'r') as f:
                        existing = json.load(f)
                        if isinstance(existing, dict) and 'packages' in existing:
                            existing_data = existing['packages']
                        elif isinstance(existing, list):
                            existing_data = existing
                except:
                    pass
            
            # Merge data (avoid duplicates by destination name)
            existing_names = {pkg.get('location', '') for pkg in existing_data}
            new_packages = [pkg for pkg in data if pkg.get('location', '') not in existing_names]
            
            all_packages = existing_data + new_packages
            
            with open(output_file, 'w') as f:
                json.dump({"packages": all_packages}, f, indent=2)
                
            logger.info(f"Saved {len(all_packages)} packages to {output_file} ({len(new_packages)} new)")
            return True
        except Exception as e:
            logger.error(f"Error saving scraped data: {e}")
            return False