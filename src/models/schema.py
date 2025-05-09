from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class PriceInfo(BaseModel):
    amount: float
    currency: str = "USD"
    per_person: bool = True
    includes_taxes: bool = True

class Accommodation(BaseModel):
    name: str
    type: str  # hotel, hostel, resort, etc.
    star_rating: Optional[float] = None
    address: str
    coordinates: Optional[Coordinates] = None
    amenities: List[str] = []
    room_types: List[str] = []
    images: List[str] = []
    booking_link: Optional[str] = None

class Activity(BaseModel):
    name: str
    description: str
    duration: str  # e.g. "2 hours"
    price: Optional[PriceInfo] = None
    included_in_package: bool = True
    suitable_for: List[str] = []  # families, couples, etc.
    coordinates: Optional[Coordinates] = None
    availability: List[str] = []  # days of week or "daily"
    booking_required: bool = False
    image: Optional[str] = None

class DailyItinerary(BaseModel):
    day: int
    title: str
    description: str
    meals_included: List[str] = []  # breakfast, lunch, dinner
    activities: List[Activity] = []
    accommodation: Optional[Accommodation] = None
    transportation: Optional[str] = None

class TravelPackage(BaseModel):
    id: str
    name: str
    description: str
    destination: str
    country: str
    continent: str
    coordinates: Coordinates
    price: PriceInfo
    duration: str
    activities: List[Activity] = []
    accommodations: List[Accommodation] = []
    itinerary: List[DailyItinerary] = []
    highlights: List[str] = []
    included_services: List[str] = []
    excluded_services: List[str] = []
    best_season: List[str] = []
    languages: List[str] = ["English"]
    min_travelers: int = 1
    max_travelers: Optional[int] = None
    suitable_for: List[str] = []
    sustainability_rating: Optional[int] = None
    featured_image: Optional[str] = None
    gallery_images: List[str] = []
    tags: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.now)
    reviews: List[Dict] = []
    weather_data: Optional[Dict] = None
    local_info: Optional[Dict] = None