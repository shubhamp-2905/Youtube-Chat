import chromadb
import json
import os
from typing import List, Dict, Any, Optional
from app.config import Config

class VectorStore:
    def __init__(self, collection_name: str = "youtube_transcripts"):
        self.collection_name = collection_name
        self.persist_directory = Config.VECTOR_STORE_PATH
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            print(f"ChromaDB client initialized with path: {self.persist_directory}")
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube video transcripts for RAG chatbot"}
            )
            print(f"Collection '{self.collection_name}' ready")
            
        except Exception as e:
            print(f"Error initializing vector store: {str(e)}")
            raise Exception(f"Failed to initialize vector store: {str(e)}")
    
    def add_documents(self, video_id: str, chunks: List[Dict[str, Any]]) -> bool:
        """
        Add document chunks to the vector store
        """
        try:
            # Check if video already exists
            if self.video_exists(video_id):
                print(f"Video {video_id} already exists in vector store")
                return True
            
            # Prepare data for ChromaDB
            documents = []
            embeddings = []
            ids = []
            metadatas = []
            
            for chunk in chunks:
                # Create unique ID for each chunk
                chunk_id = f"{video_id}_{chunk['id']}"
                
                documents.append(chunk['text'])
                embeddings.append(chunk['embedding'])
                ids.append(chunk_id)
                metadatas.append({
                    'video_id': video_id,
                    'chunk_id': chunk['id'],
                    'length': chunk['length']
                })
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks for video {video_id} to vector store")
            return True
            
        except Exception as e:
            print(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def search_similar(self, query_embedding: List[float], 
                      video_id: str = None, 
                      top_k: int = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents in the vector store
        """
        try:
            top_k = top_k or Config.TOP_K_CHUNKS
            
            # Prepare where clause for filtering by video_id if provided
            where_clause = {"video_id": video_id} if video_id else None
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            similar_chunks = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    chunk = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    similar_chunks.append(chunk)
            
            print(f"Found {len(similar_chunks)} similar chunks")
            return similar_chunks
            
        except Exception as e:
            print(f"Error searching vector store: {str(e)}")
            return []
    
    def video_exists(self, video_id: str) -> bool:
        """
        Check if a video already exists in the vector store
        """
        try:
            results = self.collection.get(
                where={"video_id": video_id},
                limit=1
            )
            return len(results['ids']) > 0
        except Exception as e:
            print(f"Error checking if video exists: {str(e)}")
            return False
    
    def get_video_chunks(self, video_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific video
        """
        try:
            results = self.collection.get(
                where={"video_id": video_id},
                include=['documents', 'metadatas']
            )
            
            chunks = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    chunk = {
                        'text': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Error getting video chunks: {str(e)}")
            return []
    
    def delete_video(self, video_id: str) -> bool:
        """
        Delete all chunks for a specific video
        """
        try:
            # Get all IDs for the video
            results = self.collection.get(
                where={"video_id": video_id}
            )
            
            if results['ids']:
                self.collection.delete(
                    ids=results['ids']
                )
                print(f"Deleted {len(results['ids'])} chunks for video {video_id}")
                return True
            else:
                print(f"No chunks found for video {video_id}")
                return False
                
        except Exception as e:
            print(f"Error deleting video chunks: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        """
        try:
            count = self.collection.count()
            
            # Get unique video count
            all_metadata = self.collection.get(include=['metadatas'])
            unique_videos = set()
            if all_metadata['metadatas']:
                for metadata in all_metadata['metadatas']:
                    unique_videos.add(metadata['video_id'])
            
            return {
                'total_chunks': count,
                'unique_videos': len(unique_videos),
                'collection_name': self.collection_name
            }
            
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {'error': str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection
        """
        try:
            # Delete the collection
            self.client.delete_collection(self.collection_name)
            
            # Recreate the collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "YouTube video transcripts for RAG chatbot"}
            )
            
            print(f"Collection '{self.collection_name}' cleared")
            return True
            
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False