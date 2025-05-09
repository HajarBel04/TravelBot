from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
import uuid

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Price(BaseModel):
    amount: float
    currency: str = "USD"
    per_person: bool = True

class Activity(BaseModel):
    name: str
    description: Optional[str] = None
    duration: Optional[str] = None
    included_in_package: bool = True
    coordinates: Optional[Coordinates] = None
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Activity name cannot be empty')
        return v.strip()

class WeatherDaily(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: Optional[List[float]] = None

class WeatherData(BaseModel):
    daily: WeatherDaily

class LocalInfo(BaseModel):
    capital: Optional[str] = None
    currency: Optional[str] = None
    languages: Optional[str] = None
    flag: Optional[str] = None

class LocalAttraction(BaseModel):
    name: str
    description: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class DestinationGuide(BaseModel):
    title: Optional[str] = None
    extract: str

class TravelPackage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    location: str  # Primary location field
    destination: Optional[str] = None  # Kept for backward compatibility
    country: str = "Unknown"
    continent: str = "Unknown"
    price: Union[float, Dict[str, Any], Price]
    duration: str = "5 days"
    activities: List[Union[str, Dict[str, Any], Activity]] = []
    coordinates: Optional[Coordinates] = None
    weather_data: Optional[WeatherData] = None
    local_info: Optional[LocalInfo] = None
    local_attractions: Optional[List[LocalAttraction]] = None
    destination_guide: Optional[DestinationGuide] = None
    highlights: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('destination', always=True)
    def set_destination_from_location(cls, v, values):
        """If destination is not provided, use location value."""
        if not v and 'location' in values:
            return values['location']
        return v
    
    @validator('price')
    def validate_price(cls, v):
        """Convert price to standard Price model."""
        if isinstance(v, (int, float)):
            return Price(amount=float(v))
        elif isinstance(v, dict):
            if 'amount' in v:
                # Convert to Price model
                price_data = {
                    'amount': float(v['amount']),
                    'currency': v.get('currency', 'USD'),
                    'per_person': v.get('per_person', True)
                }
                return Price(**price_data)
            else:
                raise ValueError('Price dictionary must contain amount')
        elif isinstance(v, Price):
            return v
        else:
            raise ValueError('Price must be a number, dictionary, or Price model')
    
    @validator('activities')
    def validate_activities(cls, v):
        """Convert activities to standard Activity models."""
        result = []
        for activity in v:
            if isinstance(activity, str):
                result.append(Activity(
                    name=activity,
                    description=f"Enjoy {activity}",
                    duration="2 hours"
                ))
            elif isinstance(activity, dict):
                if 'name' not in activity:
                    raise ValueError('Activity dictionary must contain name')
                result.append(Activity(**activity))
            elif isinstance(activity, Activity):
                result.append(activity)
            else:
                raise ValueError('Activity must be a string, dictionary, or Activity model')
        return result

class ExtractedEmailInfo(BaseModel):
    destination: Optional[str] = None
    dates: Optional[str] = None
    travelers: Optional[str] = None
    budget: Optional[str] = None
    duration: Optional[str] = None
    interests: Optional[str] = None
    travel_type: Optional[str] = None
    travel_date: Optional[str] = None
    num_travelers: Optional[str] = None
    optional_details: Optional[str] = None
    hotel_pref: Optional[str] = None
    flight_pref: Optional[str] = None
    allergy: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields not defined in the model

class TravelProposal(BaseModel):
    extracted_info: ExtractedEmailInfo
    packages: List[TravelPackage]
    query: Optional[str] = None
    proposal: str
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True

# Function to convert legacy package to standardized package
def standardize_package(package_data: Dict) -> TravelPackage:
    """
    Convert a legacy package dictionary to a standardized TravelPackage model.
    """
    # Handle missing required fields
    if 'name' not in package_data:
        package_data['name'] = f"Travel Package {package_data.get('id', '')}"
    
    if 'location' not in package_data:
        if 'destination' in package_data:
            package_data['location'] = package_data['destination']
        else:
            package_data['location'] = 'Unknown Location'
    
    # Create standardized package
    try:
        return TravelPackage(**package_data)
    except Exception as e:
        # Handle validation errors by fixing data issues
        if 'price' in str(e) and 'price' in package_data:
            # Fix price issues
            if isinstance(package_data['price'], dict) and 'amount' not in package_data['price']:
                package_data['price'] = {'amount': 1000, 'currency': 'USD'}
            elif not isinstance(package_data['price'], (dict, int, float)):
                package_data['price'] = 1000
                
        # Try again with fixed data
        try:
            return TravelPackage(**package_data)
        except Exception as e:
            # Last resort: create minimal valid package
            print(f"Error standardizing package {package_data.get('id', 'unknown')}: {e}")
            return TravelPackage(
                id=package_data.get('id', str(uuid.uuid4())),
                name=package_data.get('name', 'Unknown Package'),
                location=package_data.get('location', package_data.get('destination', 'Unknown Location')),
                price=1000,
                description=package_data.get('description', 'No description available')
            )

# Function to standardize a collection of packages
def standardize_packages(packages_data: List[Dict]) -> List[TravelPackage]:
    """
    Convert a list of legacy package dictionaries to standardized TravelPackage models.
    
    Args:
        packages_data: List of package dictionaries
        
    Returns:
        List of standardized TravelPackage models
    """
    standardized_packages = []
    
    for package_data in packages_data:
        try:
            standardized_package = standardize_package(package_data)
            standardized_packages.append(standardized_package)
        except Exception as e:
            print(f"Failed to standardize package: {e}")
            # Skip invalid packages
            continue
    
    return standardized_packages

# Function to convert standardized package back to dictionary
def package_to_dict(package: TravelPackage) -> Dict:
    """
    Convert a TravelPackage model to a dictionary that can be used with existing code.
    
    Args:
        package: TravelPackage model
        
    Returns:
        Dictionary representation of the package
    """
    package_dict = package.dict()
    
    # Convert nested Price model to dictionary
    if isinstance(package.price, Price):
        package_dict['price'] = {
            'amount': package.price.amount,
            'currency': package.price.currency,
            'per_person': package.price.per_person
        }
    
    # Convert activities list
    activities = []
    for activity in package.activities:
        if isinstance(activity, Activity):
            activities.append({
                'name': activity.name,
                'description': activity.description,
                'duration': activity.duration,
                'included_in_package': activity.included_in_package
            })
        else:
            activities.append(activity)
    
    package_dict['activities'] = activities
    
    return package_dict