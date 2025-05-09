import os
import pickle
import numpy as np
import logging
import time
from pathlib import Path
import faiss
from typing import List, Dict, Tuple, Optional, Any, Union
import hashlib
import json

from src.config import Config
from src.generation.llm_wrapper import OllamaWrapper

logger = logging.getLogger(__name__)

class OptimizedVectorStore:
    """Vector store with incremental updates and performance optimizations."""
    
    def __init__(self, store_path=None, embedding_dimension=None, ollama_client=None):
        """Initialize the vector store."""
        self.store_path = store_path or Config.VECTOR_STORE_PATH
        self.embedder = ollama_client or OllamaWrapper()
        self.embedding_dimension = embedding_dimension or Config.EMBEDDING_DIMENSION
        
        # Core data structures
        self.index = None
        self.documents = []
        self.document_hashes = {}  # Track document hashes to detect changes
        self.document_ids = {}     # Map document IDs to their positions in the vectors list
        self.vectors = []
        
        # Metadata
        self.last_updated = None
        self.last_rebuild = None
        self.update_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Embedding cache to avoid redundant embeddings
        self.embedding_cache = {}
        self.cache_max_size = 1000  # Maximum number of items in cache
        
        # Load if store exists
        self.load()
        
    def text_to_hash(self, text: str) -> str:
        """Generate a deterministic hash from text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def document_to_hash(self, document: Dict) -> str:
        """Generate a hash for a document based on its content."""
        # Extract relevant fields for hashing
        hash_fields = {
            'id': document.get('id', ''),
            'name': document.get('name', ''),
            'description': document.get('description', ''),
            'location': document.get('location', document.get('destination', '')),
            'activities': str(document.get('activities', [])),
            'price': str(document.get('price', ''))
        }
        # Create a consistent string representation and hash it
        hash_str = json.dumps(hash_fields, sort_keys=True)
        return self.text_to_hash(hash_str)
    
    def get_document_embedding(self, document: Dict, text: Optional[str] = None) -> Tuple[np.ndarray, str]:
        """
        Get embedding for a document, using cache when possible.
        
        Args:
            document: Document to embed
            text: Optional pre-generated text representation
            
        Returns:
            Tuple of (embedding vector, text representation)
        """
        # Generate text if not provided
        if text is None:
            text = self.generate_text_representation(document)
        
        # Create hash for the text
        text_hash = self.text_to_hash(text)
        
        # Check cache
        if text_hash in self.embedding_cache:
            self.cache_hits += 1
            return self.embedding_cache[text_hash], text
        
        # Generate embedding
        self.cache_misses += 1
        embedding = self.embedder.get_embeddings(text)
        
        # Convert to numpy array if it's a list
        if isinstance(embedding, list):
            embedding = np.array(embedding)
        
        # Ensure correct dimension
        if embedding.shape[0] != self.embedding_dimension:
            if embedding.shape[0] > self.embedding_dimension:
                embedding = embedding[:self.embedding_dimension]
            else:
                padding = np.zeros(self.embedding_dimension - embedding.shape[0])
                embedding = np.concatenate([embedding, padding])
            
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
        
        # Store in cache (manage cache size)
        if len(self.embedding_cache) >= self.cache_max_size:
            # Remove a random item when cache is full
            try:
                random_key = next(iter(self.embedding_cache))
                del self.embedding_cache[random_key]
            except:
                # If iteration fails, just clear a portion of the cache
                keys = list(self.embedding_cache.keys())[:100]
                for key in keys:
                    del self.embedding_cache[key]
        
        self.embedding_cache[text_hash] = embedding
        return embedding, text
    
    def generate_text_representation(self, document: Dict) -> str:
        """Generate a text representation of a document for embedding."""
        text = f"Package Name: {document.get('name', '')}\n"
        
        # Handle both location and destination fields
        location = document.get('location', '')
        destination = document.get('destination', '')
        text += f"Destination: {location or destination}\n"
        
        text += f"Duration: {document.get('duration', '')}\n"
        
        # Handle different price formats
        if isinstance(document.get('price'), dict):
            text += f"Price: ${document['price'].get('amount', 0)}\n"
        else:
            text += f"Price: ${document.get('price', 0)}\n"
        
        # Handle different activities formats
        activities = []
        if isinstance(document.get('activities'), list):
            for activity in document.get('activities'):
                if isinstance(activity, dict) and 'name' in activity:
                    activities.append(activity['name'])
                elif isinstance(activity, str):
                    activities.append(activity)
        
        if activities:
            text += f"Activities: {', '.join(activities)}\n"
        
        # Add enriched data if available
        if document.get('country') and document.get('country') != 'Unknown':
            text += f"Country: {document.get('country')}\n"
            
        if document.get('continent') and document.get('continent') != 'Unknown':
            text += f"Continent: {document.get('continent')}\n"
        
        # Add description - make this more prominent for better topic matching
        description = document.get('description', '')
        if description:
            text += f"Description: {description}\n"
            # Also add the description again with keywords to enhance retrieval
            text += f"Keywords: {description}\n"
        
        # Explicitly add key words for better matching
        if "beach" in description.lower() or any("beach" in act.lower() for act in activities):
            text += "Type: Beach vacation, seaside, ocean, tropical\n"
            
        if "mountain" in description.lower() or any("hik" in act.lower() for act in activities):
            text += "Type: Mountain vacation, hiking, nature, outdoor\n"
            
        if "city" in description.lower() or any("museum" in act.lower() for act in activities):
            text += "Type: City vacation, urban, sightseeing, cultural\n"
        
        return text
    
    def add_documents(self, documents: List[Dict], texts: Optional[List[str]] = None) -> bool:
        """
        Add documents to the vector store with incremental updates.
        
        Args:
            documents: List of documents to add
            texts: Optional pre-generated text representations
            
        Returns:
            bool: Success status
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return True
                
            # Track new and updated documents
            new_vectors = []
            new_documents = []
            updated_indices = []
            
            # Process each document
            for i, document in enumerate(documents):
                # Get document ID
                doc_id = document.get('id', None)
                if not doc_id:
                    # Generate a stable ID if not present
                    doc_id = str(hash(document.get('name', '') + document.get('location', '')))
                    document['id'] = doc_id
                
                # Get document hash to detect changes
                doc_hash = self.document_to_hash(document)
                
                # Get text representation
                text = None
                if texts and i < len(texts):
                    text = texts[i]
                
                # Check if document exists and has changed
                if doc_id in self.document_ids:
                    index_position = self.document_ids[doc_id]
                    
                    # Check if document has changed
                    if self.document_hashes.get(doc_id) != doc_hash:
                        # Document has changed, update it
                        embedding, text = self.get_document_embedding(document, text)
                        
                        # Track for FAISS index update
                        updated_indices.append((index_position, embedding))
                        
                        # Update documents and vectors
                        self.documents[index_position] = document
                        self.vectors[index_position] = embedding
                        self.document_hashes[doc_id] = doc_hash
                    # If unchanged, do nothing
                else:
                    # New document, add it
                    embedding, text = self.get_document_embedding(document, text)
                    
                    # Track for batch addition
                    new_vectors.append(embedding)
                    new_documents.append(document)
                    
                    # Add to mappings
                    new_position = len(self.vectors) + len(new_vectors) - 1
                    self.document_ids[doc_id] = new_position
                    self.document_hashes[doc_id] = doc_hash
            
            # Apply updates
            if new_documents or updated_indices:
                self._apply_updates(new_documents, new_vectors, updated_indices)
                
                # Track update metadata
                self.last_updated = time.time()
                self.update_count += 1
                
                # Save the updated store
                self.save()
                
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def _apply_updates(self, new_documents, new_vectors, updated_indices):
        """Apply incremental updates to the vector store."""
        # 1. Extend documents and vectors with new items
        self.documents.extend(new_documents)
        self.vectors.extend(new_vectors)
        
        # 2. Create or update the FAISS index
        if self.index is None or self.update_count % 10 == 0 or len(updated_indices) > 10:
            # Complete rebuild (more efficient with many changes)
            self._rebuild_index()
            self.last_rebuild = time.time()
        else:
            # Incremental update
            try:
                # Add new vectors to the index
                if new_vectors:
                    vectors_np = np.array(new_vectors).astype('float32')
                    self.index.add(vectors_np)
                
                # Update changed vectors in the index
                for idx, embedding in updated_indices:
                    # FAISS doesn't support direct updates, we need to remove and re-add
                    # But we can't remove individual vectors, so we just update in our vectors list
                    # and will periodically rebuild the whole index
                    self.vectors[idx] = embedding
            except Exception as e:
                logger.error(f"Error in incremental update, falling back to rebuild: {e}")
                self._rebuild_index()
                self.last_rebuild = time.time()
        
        # Log update stats
        logger.info(f"Updated vector store: {len(new_documents)} new documents, {len(updated_indices)} updated documents")
        
    def _rebuild_index(self):
        """Rebuild the FAISS index from all vectors."""
        if not self.vectors:
            logger.warning("No vectors available for index rebuild")
            return
            
        try:
            # Convert all vectors to numpy array
            vectors_np = np.array(self.vectors).astype('float32')
            
            # Create a new FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            
            # Add all vectors
            self.index.add(vectors_np)
            
            logger.info(f"Rebuilt FAISS index with {len(self.vectors)} vectors")
        except Exception as e:
            logger.error(f"Error rebuilding FAISS index: {e}")
            self.index = None
    
    def similarity_search(self, query: str, k: int = 5, filter_fn=None) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents with optional filtering.
        
        Args:
            query: The query text
            k: Number of results to return
            filter_fn: Optional function to filter results
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vectors or not self.index:
            logger.warning("Vector store is empty or index not built")
            return []
        
        try:
            # Get query embedding
            query_embedding = self.embedder.get_embeddings(query)
            query_np = np.array([query_embedding]).astype('float32')
            
            # Search the index
            distances, indices = self.index.search(query_np, min(len(self.vectors), k*2))  # Get more for filtering
            
            # Process results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    
                    # Apply filter if provided
                    if filter_fn and not filter_fn(doc):
                        continue
                    
                    # Calculate similarity score (1 - normalized distance)
                    similarity = 1.0 - min(1.0, distances[0][i] / max(distances[0]) if max(distances[0]) > 0 else 0)
                    results.append((doc, similarity))
            
            # Sort by similarity (highest first)
            results.sort(key=lambda x: x[1], reverse=True)
            
            # Return only requested number after filtering
            return results[:k]
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def save(self):
        """Save the vector store to disk."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            
            # Prepare data for saving
            store_data = {
                'vectors': self.vectors,
                'documents': self.documents,
                'document_hashes': self.document_hashes,
                'document_ids': self.document_ids,
                'metadata': {
                    'last_updated': self.last_updated,
                    'last_rebuild': self.last_rebuild,
                    'update_count': self.update_count,
                    'vector_dim': self.embedding_dimension,
                    'doc_count': len(self.documents)
                }
            }
            
            # Save data
            with open(self.store_path, 'wb') as f:
                pickle.dump(store_data, f)
                
            logger.info(f"Saved vector store to {self.store_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load(self):
        """Load the vector store from disk."""
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path, 'rb') as f:
                    store_data = pickle.load(f)
                
                # Load data
                self.vectors = store_data.get('vectors', [])
                self.documents = store_data.get('documents', [])
                self.document_hashes = store_data.get('document_hashes', {})
                self.document_ids = store_data.get('document_ids', {})
                
                # Load metadata
                metadata = store_data.get('metadata', {})
                self.last_updated = metadata.get('last_updated')
                self.last_rebuild = metadata.get('last_rebuild')
                self.update_count = metadata.get('update_count', 0)
                
                # Rebuild index
                if self.vectors:
                    self._rebuild_index()
                
                logger.info(f"Loaded vector store from {self.store_path} with {len(self.documents)} documents")
                return True
            else:
                logger.info(f"Vector store file not found at {self.store_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
            
    def get_statistics(self):
        """Get statistics about the vector store."""
        return {
            'document_count': len(self.documents),
            'vector_count': len(self.vectors),
            'index_size': self.index.ntotal if self.index else 0,
            'last_updated': self.last_updated,
            'last_rebuilt': self.last_rebuild,
            'update_count': self.update_count,
            'cache_size': len(self.embedding_cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'cache_hit_ratio': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Cleared embedding cache")
    
    def get_documents(self):
        """Get all documents in the vector store."""
        return self.documents
    
    def get_document_by_id(self, doc_id):
        """Get a document by its ID."""
        if doc_id in self.document_ids:
            index = self.document_ids[doc_id]
            return self.documents[index]
        return None
    
    def remove_document(self, doc_id):
        """
        Remove a document from the vector store.
        Note: This marks the document for removal but requires a rebuild for FAISS.
        """
        if doc_id in self.document_ids:
            index = self.document_ids[doc_id]
            
            # Mark for removal (but don't actually remove until rebuild)
            # This is a workaround since FAISS doesn't support removing vectors
            self.documents[index] = None
            
            # Clean up mappings
            del self.document_ids[doc_id]
            if doc_id in self.document_hashes:
                del self.document_hashes[doc_id]
                
            # Schedule rebuild on next save
            self.update_count += 1
            logger.info(f"Marked document {doc_id} for removal")
            return True
        return False