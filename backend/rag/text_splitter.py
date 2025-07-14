import re
from typing import List, Dict, Any
from app.config import Config

class TextSplitter:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP
    
    def split_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap
        """
        try:
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Split into sentences for better chunking
            sentences = self._split_into_sentences(cleaned_text)
            
            chunks = []
            current_chunk = ""
            current_length = 0
            chunk_id = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                # If adding this sentence would exceed chunk size, save current chunk
                if current_length + sentence_length > self.chunk_size and current_chunk:
                    chunks.append({
                        'id': chunk_id,
                        'text': current_chunk.strip(),
                        'length': len(current_chunk.strip())
                    })
                    
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0:
                        overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                        current_chunk = overlap_text + " " + sentence
                        current_length = len(current_chunk)
                    else:
                        current_chunk = sentence
                        current_length = sentence_length
                else:
                    # Add sentence to current chunk
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                    current_length += sentence_length
            
            # Add the last chunk if it exists
            if current_chunk.strip():
                chunks.append({
                    'id': chunk_id,
                    'text': current_chunk.strip(),
                    'length': len(current_chunk.strip())
                })
            
            print(f"Text split into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            print(f"Error splitting text: {str(e)}")
            raise Exception(f"Failed to split text: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Fix common transcript issues
        text = text.replace(' .', '.')
        text = text.replace(' ,', ',')
        text = text.replace(' !', '!')
        text = text.replace(' ?', '?')
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using simple regex
        """
        # Split by sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter empty sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """
        Get the last part of text for overlap
        """
        if len(text) <= overlap_size:
            return text
        
        # Try to find a good breaking point (end of sentence)
        overlap_text = text[-overlap_size:]
        
        # Find the first sentence ending in the overlap
        for i, char in enumerate(overlap_text):
            if char in '.!?':
                return overlap_text[i+1:].strip()
        
        # If no sentence ending found, return the overlap as is
        return overlap_text.strip()
    
    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the chunks
        """
        if not chunks:
            return {'total_chunks': 0, 'total_length': 0, 'avg_length': 0}
        
        total_length = sum(chunk['length'] for chunk in chunks)
        avg_length = total_length / len(chunks)
        
        return {
            'total_chunks': len(chunks),
            'total_length': total_length,
            'avg_length': round(avg_length, 2),
            'min_length': min(chunk['length'] for chunk in chunks),
            'max_length': max(chunk['length'] for chunk in chunks)
        }