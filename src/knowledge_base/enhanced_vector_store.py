import os
import pickle
import numpy as np
import logging
import sqlite3
import json
import faiss
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any, Union

from src.config import Config
from src.generation.llm_wrapper import OllamaWrapper

logger = logging.getLogger(__name__)

class EnhancedVectorStore:
    """Enhanced vector store with improved storage and retrieval capabilities."""
    
    def __init__(self, 
                 db_path: str = "data/travel_data.db", 
                 index_path: str = "data/embeddings/faiss_index.pkl",
                 ollama_client = None):
        """Initialize the enhanced vector store."""
        self.db_path = Path(db_path)
        self.index_path = Path(index_path)
        self.embedder = ollama_client or OllamaWrapper()
        self.embedding_dimension = Config.EMBEDDING_DIMENSION
        self.index = None
        self.id_mapping = []  # Maps FAISS index positions to package IDs
        
        # Create database and tables if they don't exist
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for package storage."""
        try:
            # Create parent directories if they don't exist
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create packages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT,
                description TEXT,
                duration TEXT,
                price REAL,
                package_json TEXT NOT NULL,
                embedding_id INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # Create activities table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                package_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                duration TEXT,
                FOREIGN KEY (package_id) REFERENCES packages (id)
            )
            ''')
            
            # Create embeddings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id TEXT UNIQUE,
                created_at TEXT,
                FOREIGN KEY (package_id) REFERENCES packages (id)
            )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise e
        
        
    def add_package(self, package: Dict, text: Optional[str] = None) -> bool:
        """Add a package to the vector store and database."""
        try:
            # Generate text representation if not provided
            if text is None:
                text = self._generate_text_from_package(package)
            
            # Generate embedding
            embedding = self.embedder.get_embeddings(text)
            
            # Store package in database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Convert package to JSON
            package_json = json.dumps(package)
            
            # Current timestamp
            timestamp = datetime.now().isoformat()
            
            # Insert package
            cursor.execute('''
            INSERT OR REPLACE INTO packages
            (id, name, location, description, duration, price, package_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                package.get('id', str(hash(text))),
                package.get('name', 'Unknown'),
                package.get('location', package.get('destination', 'Unknown')),
                package.get('description', ''),
                package.get('duration', ''),
                package.get('price', 0) if isinstance(package.get('price'), (int, float)) else 0,
                package_json,
                timestamp,
                timestamp
            ))
            
            package_id = package.get('id', str(hash(text)))
            
            # Insert activities if present
            if 'activities' in package and isinstance(package['activities'], list):
                for activity in package['activities']:
                    if isinstance(activity, dict):
                        activity_id = activity.get('id', str(hash(activity.get('name', ''))))
                        cursor.execute('''
                        INSERT OR REPLACE INTO activities
                        (id, package_id, name, description, duration)
                        VALUES (?, ?, ?, ?, ?)
                        ''', (
                            activity_id,
                            package_id,
                            activity.get('name', 'Unknown Activity'),
                            activity.get('description', ''),
                            activity.get('duration', '')
                        ))
            
            # Add to embeddings table and get embedding_id
            cursor.execute('''
            INSERT OR REPLACE INTO embeddings
            (package_id, created_at)
            VALUES (?, ?)
            ''', (package_id, timestamp))
            
            embedding_id = cursor.lastrowid
            
            # Update package with embedding_id
            cursor.execute('''
            UPDATE packages 
            SET embedding_id = ? 
            WHERE id = ?
            ''', (embedding_id, package_id))
            
            conn.commit()
            conn.close()
            
            # Update FAISS index
            self._update_faiss_index()
            
            return True
        except Exception as e:
            logger.error(f"Error adding package: {e}")
            return False
    
    def add_packages(self, packages: List[Dict], texts: Optional[List[str]] = None) -> bool:
        """Add multiple packages to the vector store and database."""
        try:
            if not packages:
                return True
                
            # Generate texts if not provided
            if texts is None:
                texts = [self._generate_text_from_package(pkg) for pkg in packages]
                
            # Generate embeddings
            embeddings = self.embedder.get_embeddings(texts)
            
            # Store packages and embeddings in database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            for i, package in enumerate(packages):
                # Convert package to JSON
                package_json = json.dumps(package)
                
                # Current timestamp
                timestamp = datetime.now().isoformat()
                
                # Generate a unique ID if not present
                package_id = package.get('id', str(hash(texts[i])))
                
                # Insert package
                cursor.execute('''
                INSERT OR REPLACE INTO packages
                (id, name, location, description, duration, price, package_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    package_id,
                    package.get('name', 'Unknown'),
                    package.get('location', package.get('destination', 'Unknown')),
                    package.get('description', ''),
                    package.get('duration', ''),
                    package.get('price', 0) if isinstance(package.get('price'), (int, float)) else 0,
                    package_json,
                    timestamp,
                    timestamp
                ))
                
                # Insert activities if present
                if 'activities' in package and isinstance(package['activities'], list):
                    for activity in package['activities']:
                        if isinstance(activity, dict):
                            activity_id = activity.get('id', str(hash(activity.get('name', ''))))
                            cursor.execute('''
                            INSERT OR REPLACE INTO activities
                            (id, package_id, name, description, duration)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (
                                activity_id,
                                package_id,
                                activity.get('name', 'Unknown Activity'),
                                activity.get('description', ''),
                                activity.get('duration', '')
                            ))
                
                # Add to embeddings table and get embedding_id
                cursor.execute('''
                INSERT OR REPLACE INTO embeddings
                (package_id, created_at)
                VALUES (?, ?)
                ''', (package_id, timestamp))
                
                embedding_id = cursor.lastrowid
                
                # Update package with embedding_id
                cursor.execute('''
                UPDATE packages 
                SET embedding_id = ? 
                WHERE id = ?
                ''', (embedding_id, package_id))
            
            conn.commit()
            conn.close()
            
            # Update FAISS index
            self._update_faiss_index()
            
            return True
        except Exception as e:
            logger.error(f"Error adding packages: {e}")
            return False
    
    def _generate_text_from_package(self, package: Dict) -> str:
        """Generate a text representation of a package for embedding."""
        text = f"Travel package: {package.get('name', '')}\n"
        text += f"Destination: {package.get('location', package.get('destination', ''))}\n"
        text += f"Description: {package.get('description', '')}\n"
        
        # Add activities
        activities = []
        if 'activities' in package and isinstance(package['activities'], list):
            for activity in package['activities']:
                if isinstance(activity, dict) and 'name' in activity:
                    activities.append(activity['name'])
                elif isinstance(activity, str):
                    activities.append(activity)
            
            if activities:
                text += f"Activities: {', '.join(activities)}\n"
        
        # Add duration and price
        text += f"Duration: {package.get('duration', '')}\n"
        
        # Handle price which could be a number or a dict
        price = package.get('price', '')
        if isinstance(price, dict):
            text += f"Price: {price.get('amount', '')} {price.get('currency', '')}\n"
        else:
            text += f"Price: {price}\n"
        
        # Add other important attributes
        if 'country' in package:
            text += f"Country: {package['country']}\n"
            
        if 'continent' in package:
            text += f"Continent: {package['continent']}\n"
            
        if 'highlights' in package and isinstance(package['highlights'], list):
            text += f"Highlights: {', '.join(package['highlights'])}\n"
            
        return text
    
    def _update_faiss_index(self):
        """Update the FAISS index with all embeddings."""
        try:
            # Get all packages and their embeddings
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get all packages
            cursor.execute('''
            SELECT p.id, p.package_json, e.id
            FROM packages p
            JOIN embeddings e ON p.id = e.package_id
            ''')
            
            packages_data = cursor.fetchall()
            conn.close()
            
            if not packages_data:
                logger.warning("No packages found for indexing")
                return
            
            # Generate embeddings for all packages
            package_ids = []
            embedding_ids = []
            texts = []
            
            for package_id, package_json, embedding_id in packages_data:
                package = json.loads(package_json)
                text = self._generate_text_from_package(package)
                texts.append(text)
                package_ids.append(package_id)
                embedding_ids.append(embedding_id)
            
            # Get embeddings
            embeddings = self.embedder.get_embeddings(texts)
            
            # Create a FAISS index
            vector_dim = len(embeddings[0])
            self.index = faiss.IndexFlatL2(vector_dim)
            
            # Add vectors to the index
            vectors_np = np.array(embeddings).astype('float32')
            self.index.add(vectors_np)
            
            # Save mapping of FAISS indices to package IDs
            self.id_mapping = list(zip(embedding_ids, package_ids))
            
            # Save the index and mapping
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, 'wb') as f:
                pickle.dump((self.index, self.id_mapping), f)
                
            logger.info(f"FAISS index updated with {len(embeddings)} vectors")
        except Exception as e:
            logger.error(f"Error updating FAISS index: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar packages using FAISS."""
        try:
            # Load index if not already loaded
            if self.index is None:
                self._load_faiss_index()
                
            # If still not loaded, return empty results
            if self.index is None:
                logger.warning("FAISS index not available")
                return []
                
            # Generate query embedding
            query_embedding = self.embedder.get_embeddings(query)
            query_np = np.array([query_embedding]).astype('float32')
            
            # Search the index
            distances, indices = self.index.search(query_np, min(k, self.index.ntotal))
            
            # Get package IDs from index results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.id_mapping):
                    embedding_id, package_id = self.id_mapping[idx]
                    
                    # Get package from database
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.cursor()
                    cursor.execute('SELECT package_json FROM packages WHERE id = ?', (package_id,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        package = json.loads(result[0])
                        # Calculate similarity score (1 - normalized distance)
                        similarity = 1.0 - (distances[0][i] / max(distances[0]) if max(distances[0]) > 0 else 0)
                        results.append((package, similarity))
            
            # Sort by similarity (highest first)
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Return just the packages
            return [pkg for pkg, _ in results]
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def _load_faiss_index(self):
        """Load the FAISS index from disk if available."""
        try:
            if self.index_path.exists():
                with open(self.index_path, 'rb') as f:
                    self.index, self.id_mapping = pickle.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                logger.warning(f"FAISS index not found at {self.index_path}")
                self._update_faiss_index()
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
    
    def get_all_packages(self) -> List[Dict]:
        """Get all packages from the database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT package_json FROM packages')
            results = cursor.fetchall()
            conn.close()
            
            return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Error getting all packages: {e}")
            return []
    
    def get_package_by_id(self, package_id: str) -> Optional[Dict]:
        """Get a package by its ID."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('SELECT package_json FROM packages WHERE id = ?', (package_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Error getting package by ID: {e}")
            return None