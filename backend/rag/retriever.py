from typing import List, Dict, Any
from rag.embedding_model import EmbeddingModel
from rag.vector_store import VectorStore
from app.config import Config

class Retriever:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.top_k = Config.TOP_K_CHUNKS
    
    def retrieve_context(self, query: str, video_id: str = None) -> Dict[str, Any]:
        """
        Retrieve relevant context for a given query
        """
        try:
            print(f"Retrieving context for query: '{query[:50]}...'")
            
            # Generate embedding for the query
            query_embedding = self.embedding_model.generate_single_embedding(query)
            
            # Search for similar chunks in vector store
            similar_chunks = self.vector_store.search_similar(
                query_embedding=query_embedding,
                video_id=video_id,
                top_k=self.top_k
            )
            
            if not similar_chunks:
                print("No relevant context found")
                return {
                    'context': "",
                    'relevant_chunks': [],
                    'query': query,
                    'video_id': video_id
                }
            
            # Combine relevant chunks into context
            context_parts = []
            relevant_chunks = []
            
            for chunk in similar_chunks:
                context_parts.append(chunk['text'])
                relevant_chunks.append({
                    'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                    'similarity': round(chunk['similarity'], 3),
                    'chunk_id': chunk['metadata']['chunk_id']
                })
            
            # Join context with separators
            context = "\n\n".join(context_parts)
            
            print(f"Retrieved {len(similar_chunks)} relevant chunks")
            
            return {
                'context': context,
                'relevant_chunks': relevant_chunks,
                'query': query,
                'video_id': video_id,
                'total_chunks': len(similar_chunks)
            }
            
        except Exception as e:
            print(f"Error retrieving context: {str(e)}")
            return {
                'context': "",
                'relevant_chunks': [],
                'query': query,
                'video_id': video_id,
                'error': str(e)
            }
    
    def retrieve_with_threshold(self, query: str, video_id: str = None, 
                              similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Retrieve context with minimum similarity threshold
        """
        try:
            # Get initial results
            result = self.retrieve_context(query, video_id)
            
            if 'error' in result:
                return result
            
            # Filter by similarity threshold
            filtered_chunks = [
                chunk for chunk in result['relevant_chunks'] 
                if chunk['similarity'] >= similarity_threshold
            ]
            
            if not filtered_chunks:
                return {
                    'context': "",
                    'relevant_chunks': [],
                    'query': query,
                    'video_id': video_id,
                    'message': f"No chunks found above similarity threshold {similarity_threshold}"
                }
            
            # Rebuild context from filtered chunks
            context_parts = []
            for chunk in filtered_chunks:
                # Get full text from original chunks
                for original_chunk in result['relevant_chunks']:
                    if original_chunk['chunk_id'] == chunk['chunk_id']:
                        context_parts.append(original_chunk['text'])
                        break
            
            context = "\n\n".join(context_parts)
            
            return {
                'context': context,
                'relevant_chunks': filtered_chunks,
                'query': query,
                'video_id': video_id,
                'total_chunks': len(filtered_chunks),
                'similarity_threshold': similarity_threshold
            }
            
        except Exception as e:
            print(f"Error retrieving with threshold: {str(e)}")
            return {
                'context': "",
                'relevant_chunks': [],
                'query': query,
                'video_id': video_id,
                'error': str(e)
            }
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the retrieval system
        """
        try:
            vector_stats = self.vector_store.get_collection_stats()
            embedding_info = self.embedding_model.get_model_info()
            
            return {
                'vector_store': vector_stats,
                'embedding_model': embedding_info,
                'top_k_chunks': self.top_k
            }
            
        except Exception as e:
            print(f"Error getting retrieval stats: {str(e)}")
            return {'error': str(e)}