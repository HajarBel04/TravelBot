import requests
import json
import numpy as np
import logging
from src.config import Config

logger = logging.getLogger(__name__)

class LLMWrapper:
    def __init__(self):
        self.model = None

    def set_model(self, model):
        self.model = model

    def generate_response(self, prompt):
        if self.model is None:
            raise ValueError("Model is not set. Please set a model before generating a response.")
        # Here you would typically call the model's generate method
        # For the purpose of this proof-of-concept, we will return a synthetic response
        return f"Generated response based on prompt: {prompt}"

class OllamaWrapper:
    """Wrapper for the Ollama API to handle generation and embeddings."""
    
    def __init__(self, config=None):
        """Initialize the Ollama wrapper with configuration."""
        self.config = config or Config.OLLAMA
        self.base_url = self.config["base_url"]
        self.gen_model = self.config["generation_model"]
        self.embed_model = self.config["embedding_model"]
        self.temperature = self.config["temperature"]
        self.max_tokens = self.config["max_tokens"]
    
    def generate(self, prompt, system_prompt=None):
        """Generate text using Ollama API."""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.gen_model,
                "prompt": prompt,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False  # Explicitly disable streaming to get a complete response
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.debug(f"Sending request to Ollama generate API: {url}")
            response = requests.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Ollama API returned status code {response.status_code}: {response.text}")
                # Try to use a fallback model if specified model not found
                if response.status_code == 404:
                    logger.warning(f"Model {self.gen_model} not found, trying llama2 as fallback...")
                    payload["model"] = "llama2"
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        logger.info("Successfully used llama2 as fallback")
                    else:
                        logger.error(f"Fallback model also failed with status {response.status_code}")
                        return f"Error: Ollama API returned status code {response.status_code}"
                else:
                    return f"Error: Ollama API returned status code {response.status_code}"
            
            try:
                # Handle Ollama's response format
                content = response.content.decode('utf-8')
                
                # Some versions of Ollama might return multiple JSON objects
                # Split by newlines and parse the first complete JSON object
                if '\n' in content:
                    first_json = content.split('\n')[0].strip()
                    data = json.loads(first_json)
                else:
                    data = json.loads(content)
                
                return data.get("response", "")
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parsing error: {json_err} - Content: {response.content[:100]}")
                # Try to extract just the response text without parsing JSON
                if '"response":"' in content:
                    # Simple string extraction as fallback
                    start = content.find('"response":"') + 12
                    end = content.find('","', start)
                    if end > start:
                        return content[start:end]
                return "Error: Could not parse Ollama response"
                
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {e}")
            return f"Error generating text: {str(e)}"
    
    def get_embeddings(self, texts):
        """
        Get embeddings for a list of texts using Ollama API.
        If the embedding model is not available, falls back to a simple
        deterministic embedding function.
        """
        if not isinstance(texts, list):
            texts = [texts]
            
        try:
            url = f"{self.base_url}/api/embeddings"
            
            embeddings = []
            for text in texts:
                payload = {
                    "model": self.embed_model,
                    "prompt": text
                }
                
                logger.debug(f"Sending request to Ollama embeddings API: {url}")
                response = requests.post(url, json=payload)
                
                if response.status_code == 200:
                    embedding = response.json().get("embedding", [])
                    
                    # Verify embedding dimension matches Config.EMBEDDING_DIMENSION
                    embedding_dim = len(embedding)
                    expected_dim = Config.EMBEDDING_DIMENSION
                    
                    if embedding_dim != expected_dim:
                        logger.warning(f"Embedding dimension mismatch! Got {embedding_dim}, expected {expected_dim}")
                        
                        if embedding_dim > expected_dim:
                            # Truncate the embedding to match expected dimension
                            logger.info(f"Truncating embedding from {embedding_dim} to {expected_dim}")
                            embedding = embedding[:expected_dim]
                        else:
                            # Extend the embedding with zeros
                            logger.info(f"Extending embedding from {embedding_dim} to {expected_dim}")
                            embedding.extend([0.0] * (expected_dim - embedding_dim))
                            
                        # Renormalize the embedding
                        norm = np.linalg.norm(embedding)
                        if norm > 0:
                            embedding = [x / norm for x in embedding]
                    
                    embeddings.append(embedding)
                else:
                    logger.warning(f"Embeddings API failed with status {response.status_code}: {response.text}")
                    logger.warning("Using fallback deterministic embedding function")
                    
                    # If API fails, use a fallback deterministic embedding function
                    fallback_embedding = self._deterministic_embedding(text, dimension=Config.EMBEDDING_DIMENSION)
                    embeddings.append(fallback_embedding)
                
            return embeddings if len(texts) > 1 else embeddings[0]
        except Exception as e:
            logger.error(f"Error getting embeddings from Ollama: {e}")
            logger.warning("Using fallback deterministic embedding function")
            
            # Use fallback deterministic embedding function
            embeddings = [self._deterministic_embedding(text, dimension=Config.EMBEDDING_DIMENSION) for text in texts]
            return embeddings if len(texts) > 1 else embeddings[0]
    
    def _deterministic_embedding(self, text, dimension=None):
        """
        Create a simple deterministic embedding based on the text.
        This is only used as a fallback when the embedding API is not available.
        
        Args:
            text: The text to create an embedding for
            dimension: Size of the embedding vector, defaults to Config.EMBEDDING_DIMENSION
            
        Returns:
            A numpy array of the specified dimension
        """
        # Use the configured embedding dimension if none provided
        if dimension is None:
            dimension = Config.EMBEDDING_DIMENSION
            
        # Create a seed based on the sum of character codes
        seed = sum(ord(c) for c in text)
        np.random.seed(seed)
        
        # Create a random vector with the seed
        embedding = np.random.randn(dimension)
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()