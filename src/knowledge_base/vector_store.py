import os
import pickle
import numpy as np
import logging
from src.config import Config
from src.generation.llm_wrapper import OllamaWrapper
import faiss

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for document embeddings and similarity search using FAISS."""
    
    def __init__(self, ollama_client=None):
        """Initialize the vector store."""
        self.vectors = []
        self.documents = []
        self.embedder = ollama_client or OllamaWrapper()
        self.store_path = Config.VECTOR_STORE_PATH
        self.index = None
        self.embedding_dimension = Config.EMBEDDING_DIMENSION
        
    def add_documents(self, documents, texts=None):
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document objects to store
            texts: List of text representations to embed. If None, will try to use documents directly.
        """
        if texts is None:
            texts = [str(doc) for doc in documents]
        
        try:
            embeddings = self.embedder.get_embeddings(texts)
            
            # Add to our store
            self.vectors.extend(embeddings)
            self.documents.extend(documents)
            
            # Update the FAISS index
            self._update_index()
            
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise e
    
    def _update_index(self):
        """Update or create the FAISS index with current vectors."""
        try:
            # Convert list of vectors to numpy array
            if not self.vectors:
                logger.warning("No vectors to index")
                return
                
            vectors_np = np.array(self.vectors).astype('float32')
            
            # Create a new index
            self.index = faiss.IndexFlatL2(vectors_np.shape[1])
            
            # Add vectors to the index
            self.index.add(vectors_np)
            logger.info(f"Updated FAISS index with {len(self.vectors)} vectors")
        except Exception as e:
            logger.error(f"Error updating FAISS index: {e}")
            # Fall back to non-FAISS similarity search if index creation fails
            self.index = None
    
    def similarity_search(self, query, k=5):
        """
        Search for similar documents using FAISS for efficient vector similarity.
        
        Args:
            query: The query text
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        if not self.vectors:
            logger.warning("Vector store is empty. No results to return.")
            return []
        
        try:
            # Get query embedding
            query_embedding = self.embedder.get_embeddings(query)
            
            # Handle dimension mismatch if needed
            if isinstance(query_embedding, list) and len(query_embedding) != self.embedding_dimension:
                logger.warning(f"Query embedding dimension ({len(query_embedding)}) doesn't match expected dimension ({self.embedding_dimension})")
                query_embedding_np = np.array(query_embedding)
                
                if len(query_embedding) > self.embedding_dimension:
                    # Truncate
                    query_embedding_np = query_embedding_np[:self.embedding_dimension]
                else:
                    # Pad with zeros
                    padding = np.zeros(self.embedding_dimension - len(query_embedding))
                    query_embedding_np = np.concatenate([query_embedding_np, padding])
                
                # Renormalize
                norm = np.linalg.norm(query_embedding_np)
                if norm > 0:
                    query_embedding_np = query_embedding_np / norm
                    
                query_embedding = query_embedding_np.tolist()
            
            # Convert to numpy array
            query_np = np.array([query_embedding]).astype('float32')
            
            # If FAISS index exists, use it for fast search
            if self.index is not None:
                # Search using FAISS
                distances, indices = self.index.search(query_np, min(k, len(self.vectors)))
                
                # Convert distances to similarity scores (1 - normalized distance)
                # FAISS uses L2 distance by default, so we convert to a similarity score
                max_dist = np.max(distances) if distances.size > 0 else 1.0
                if max_dist == 0:
                    max_dist = 1.0
                    
                results = []
                for i, idx in enumerate(indices[0]):
                    if idx < len(self.documents):  # Ensure index is valid
                        # Convert distance to similarity score (1 = identical, 0 = completely different)
                        similarity = 1.0 - (distances[0][i] / max_dist)
                        results.append((self.documents[idx], similarity))
                
                return results
            else:
                # Fall back to standard cosine similarity if FAISS is not available
                logger.warning("FAISS index not available, using fallback cosine similarity")
                similarities = []
                for i, doc_embedding in enumerate(self.vectors):
                    # Handle potential dimension mismatch
                    doc_array = np.array(doc_embedding)
                    query_array = np.array(query_embedding)
                    
                    # Check and adjust dimensions if needed
                    if len(doc_array) != len(query_array):
                        logger.warning(f"Document embedding dimension ({len(doc_array)}) doesn't match query dimension ({len(query_array)})")
                        
                        # Adjust the smaller one to match the larger one
                        if len(doc_array) < len(query_array):
                            # Pad document embedding
                            padding = np.zeros(len(query_array) - len(doc_array))
                            doc_array = np.concatenate([doc_array, padding])
                        else:
                            # Truncate document embedding
                            doc_array = doc_array[:len(query_array)]
                    
                    # Cosine similarity
                    similarity = self._cosine_similarity(query_array, doc_array)
                    similarities.append((self.documents[i], similarity))
                
                # Sort by similarity (descending)
                sorted_results = sorted(similarities, key=lambda x: x[1], reverse=True)
                
                return sorted_results[:k]
        except Exception as e:
            logger.error(f"Error during similarity search: {e}")
            # Try fallback method using cosine similarity
            return self._fallback_similarity_search(query_embedding, k)
    
    def _fallback_similarity_search(self, query_embedding, k=5):
        """A simple fallback similarity search when FAISS fails."""
        try:
            similarities = []
            
            # Ensure query_embedding has the right dimension
            if isinstance(query_embedding, list):
                query_embedding = np.array(query_embedding)
                
            # Check and adjust the query embedding dimension if needed
            if len(query_embedding) != self.embedding_dimension:
                logger.warning(f"Query embedding dimension ({len(query_embedding)}) doesn't match expected dimension ({self.embedding_dimension})")
                if len(query_embedding) > self.embedding_dimension:
                    # Truncate
                    query_embedding = query_embedding[:self.embedding_dimension]
                else:
                    # Pad with zeros
                    padding = np.zeros(self.embedding_dimension - len(query_embedding))
                    query_embedding = np.concatenate([query_embedding, padding])
                    
                # Renormalize
                norm = np.linalg.norm(query_embedding)
                if norm > 0:
                    query_embedding = query_embedding / norm
            
            for i, doc_embedding in enumerate(self.vectors):
                # Ensure document embedding has right dimension (shouldn't be needed but added for safety)
                doc_array = np.array(doc_embedding)
                if len(doc_array) != self.embedding_dimension:
                    logger.warning(f"Document embedding dimension ({len(doc_array)}) doesn't match expected dimension ({self.embedding_dimension})")
                    continue
                    
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, doc_array)
                similarities.append((self.documents[i], similarity))
            
            # Sort by similarity (descending)
            sorted_results = sorted(similarities, key=lambda x: x[1], reverse=True)
            
            return sorted_results[:k]
        except Exception as e:
            logger.error(f"Error during fallback similarity search: {e}")
            return []
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    def save(self):
        """Save the vector store to disk."""
        try:
            os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
            with open(self.store_path, 'wb') as f:
                pickle.dump((self.vectors, self.documents), f)
            logger.info(f"Vector store saved to {self.store_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load(self):
        """Load the vector store from disk and initialize FAISS index."""
        try:
            if os.path.exists(self.store_path):
                with open(self.store_path, 'rb') as f:
                    self.vectors, self.documents = pickle.load(f)
                logger.info(f"Vector store loaded from {self.store_path} with {len(self.documents)} documents")
                
                # Initialize FAISS index after loading vectors
                if self.vectors:
                    self._update_index()
                
                return True
            else:
                logger.warning(f"Vector store file not found at {self.store_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False