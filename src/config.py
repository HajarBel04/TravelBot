import os
from pathlib import Path

class Config:
    # Keep your existing configuration
    DATABASE_URI = "sqlite:///travel_packages.db"
    API_KEY = "your_api_key_here"
    EMAIL_SERVICE = {
        "provider": "smtp",
        "host": "smtp.example.com",
        "port": 587,
        "username": "your_email@example.com",
        "password": "your_email_password"
    }
    LOGGING_LEVEL = "DEBUG"
    MAX_EMAILS_TO_PROCESS = 100
    EMBEDDING_DIMENSION = 768
    VECTOR_STORE_PATH = "data/embeddings/vector_store.pkl"
    
    # Keep your Ollama Configuration
    OLLAMA = {
        "base_url": "http://localhost:11434",
        "embedding_model": "nomic-embed-text",
        "generation_model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # ADD THESE NEW CONFIGURATIONS:
    
    # Database path for enhanced vector store
    DB_PATH = "data/travel_data.db"
    FAISS_INDEX_PATH = "data/embeddings/faiss_index.pkl"
    
    # API configuration for free data sources
    API_CONFIG = {
        # Weather API
        "weather_api": {
            "url": "https://api.open-meteo.com/v1/forecast",
            "params": {
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "auto"
            }
        },
        
        # Geocoding API
        "geocoding_api": {
            "url": "https://nominatim.openstreetmap.org/search",
            "user_agent": "TravelRAGApp/1.0",
            "delay": 1  # seconds between requests
        },
        
        # Countries API
        "countries_api": {
            "url": "https://restcountries.com/v3.1"
        },
        
        # Exchange Rate API
        "exchange_rate_api": {
            "url": "https://open.er-api.com/v6/latest/"
        }
    }
    
    # Data sources configuration
    DATA_SOURCES = {
        "base_dir": "data",
        "sources_dir": "data/sources",
        "processed_dir": "data/processed",
        "synthetic_dir": "data/synthetic",
        "enriched_file": "data/synthetic/enriched_travel_packages.json"
    }
    
    # Initialize paths
    @classmethod
    def initialize_paths(cls):
        """Create necessary directories for data storage."""
        # Create directories
        for dir_key in ["base_dir", "sources_dir", "processed_dir", "synthetic_dir"]:
            Path(cls.DATA_SOURCES[dir_key]).mkdir(parents=True, exist_ok=True)
            
        # Create embeddings directory
        Path(cls.VECTOR_STORE_PATH).parent.mkdir(parents=True, exist_ok=True)