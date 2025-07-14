import google.generativeai as genai
from typing import Dict, Any, Optional
from app.config import Config

class LLMHandler:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            print(f"Gemini model '{self.model_name}' initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini model: {str(e)}")
            raise Exception(f"Failed to initialize Gemini model: {str(e)}")
    
    def generate_response(self, query: str, context: str, video_id: str = None) -> Dict[str, Any]:
        """
        Generate response using Gemini with context from video transcript
        """
        try:
            # Create prompt with context
            prompt = self._create_prompt(query, context, video_id)
            
            print(f"Generating response for query: '{query[:50]}...'")
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            if response.text:
                print("Response generated successfully")
                return {
                    'response': response.text,
                    'query': query,
                    'video_id': video_id,
                    'has_context': bool(context.strip()),
                    'context_length': len(context)
                }
            else:
                print("Empty response from Gemini")
                return {
                    'response': "I apologize, but I couldn't generate a response. Please try rephrasing your question.",
                    'query': query,
                    'video_id': video_id,
                    'error': "Empty response from model"
                }
                
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error while generating a response. Please try again.",
                'query': query,
                'video_id': video_id,
                'error': str(e)
            }
    
    def _create_prompt(self, query: str, context: str, video_id: str = None) -> str:
        """
        Create a well-structured prompt for the LLM
        """
        base_prompt = """You are an AI assistant that helps users understand YouTube video content. You have access to the transcript of a YouTube video and can answer questions based on that content.

Instructions:
1. Answer the user's question based primarily on the provided video transcript context
2. Be accurate and only use information from the provided context
3. If the context doesn't contain enough information to answer the question, say so clearly
4. Provide clear, concise, and helpful responses
5. If relevant, you can reference specific parts of the video content
6. Maintain a friendly and helpful tone

"""
        
        if context.strip():
            context_prompt = f"""Video Transcript Context:
{context}

"""
        else:
            context_prompt = "No specific video context was found for this query.\n\n"
        
        user_prompt = f"""User Question: {query}

Please provide a comprehensive answer based on the video transcript context above."""
        
        return base_prompt + context_prompt + user_prompt
    
    def generate_summary(self, full_transcript: str, video_id: str = None) -> Dict[str, Any]:
        """
        Generate a summary of the entire video transcript
        """
        try:
            prompt = f"""Please provide a comprehensive summary of this YouTube video transcript. 
            
Key points to include:
1. Main topic/theme of the video
2. Key points discussed
3. Important insights or conclusions
4. Structure/flow of the content

Transcript:
{full_transcript[:8000]}...  # Limit to avoid token limits

Please provide a clear and structured summary."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3,
                )
            )
            
            if response.text:
                return {
                    'summary': response.text,
                    'video_id': video_id,
                    'transcript_length': len(full_transcript)
                }
            else:
                return {
                    'summary': "Unable to generate summary",
                    'video_id': video_id,
                    'error': "Empty response from model"
                }
                
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {
                'summary': "Error generating summary",
                'video_id': video_id,
                'error': str(e)
            }
    
    def chat_without_context(self, query: str) -> Dict[str, Any]:
        """
        Generate response without video context (general chat)
        """
        try:
            prompt = f"""You are a helpful AI assistant. The user is asking a general question not related to any specific video content.

User Question: {query}

Please provide a helpful and informative response."""

            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            
            if response.text:
                return {
                    'response': response.text,
                    'query': query,
                    'has_context': False
                }
            else:
                return {
                    'response': "I apologize, but I couldn't generate a response. Please try rephrasing your question.",
                    'query': query,
                    'error': "Empty response from model"
                }
                
        except Exception as e:
            print(f"Error in general chat: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error. Please try again.",
                'query': query,
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model
        """
        return {
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'api_configured': bool(self.api_key)
        }