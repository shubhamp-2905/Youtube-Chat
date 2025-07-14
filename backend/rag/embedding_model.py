from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
from app.config import Config

class EmbeddingModel:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
            print("Embedding model loaded successfully")
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            raise Exception(f"Failed to load embedding model: {str(e)}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        """
        try:
            print(f"Generating embeddings for {len(texts)} texts...")
            
            # Generate embeddings
            embeddings = self.model.encode(texts, show_progress_bar=True)
            
            # Convert to list of lists
            embeddings_list = [embedding.tolist() for embedding in embeddings]
            
            print(f"Generated {len(embeddings_list)} embeddings")
            return embeddings_list
            
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Failed to generate embeddings: {str(e)}")
    
    def generate_single_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        """
        try:
            embedding = self.model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            print(f"Error generating single embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add embeddings to text chunks
        """
        try:
            # Extract texts from chunks
            texts = [chunk['text'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.generate_embeddings(texts)
            
            # Add embeddings to chunks
            embedded_chunks = []
            for i, chunk in enumerate(chunks):
                embedded_chunk = chunk.copy()
                embedded_chunk['embedding'] = embeddings[i]
                embedded_chunks.append(embedded_chunk)
            
            print(f"Added embeddings to {len(embedded_chunks)} chunks")
            return embedded_chunks
            
        except Exception as e:
            print(f"Error embedding chunks: {str(e)}")
            raise Exception(f"Failed to embed chunks: {str(e)}")
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def find_most_similar(self, query_embedding: List[float], 
                         chunk_embeddings: List[Dict[str, Any]], 
                         top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar chunks to query embedding
        """
        try:
            similarities = []
            
            for chunk in chunk_embeddings:
                similarity = self.calculate_similarity(query_embedding, chunk['embedding'])
                chunk_with_similarity = chunk.copy()
                chunk_with_similarity['similarity'] = similarity
                similarities.append(chunk_with_similarity)
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            # Return top k results
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Error finding similar chunks: {str(e)}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model
        """
        try:
            # Get a sample embedding to determine dimensions
            sample_embedding = self.generate_single_embedding("test")
            
            return {
                'model_name': self.model_name,
                'embedding_dimension': len(sample_embedding),
                'max_sequence_length': self.model.max_seq_length if hasattr(self.model, 'max_seq_length') else 'Unknown'
            }
        except Exception as e:
            print(f"Error getting model info: {str(e)}")
            return {'model_name': self.model_name, 'error': str(e)}