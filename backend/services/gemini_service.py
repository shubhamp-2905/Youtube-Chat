import google.generativeai as genai
import os

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.prompt_template = """
        You are a helpful YouTube video assistant. 
        Answer the user's question based ONLY on the provided video transcript context.
        If the context doesn't contain enough information to answer the question, politely say so.
        Be concise but comprehensive in your response.
        
        Video Transcript Context:
        {context}
        
        User Question: {question}
        
        Answer:
        """
    
    def generate_response(self, context, question):
        """Generate response using Gemini"""
        try:
            # Format the prompt
            formatted_prompt = self.prompt_template.format(
                context=context,
                question=question
            )
            
            # Generate response
            response = self.model.generate_content(formatted_prompt)
            
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Sorry, I couldn't generate a response. Please try again."