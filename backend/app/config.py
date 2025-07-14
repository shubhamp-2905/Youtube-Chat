import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Vector Store Configuration
    VECTOR_STORE_PATH = "data/vectors"
    TRANSCRIPTS_PATH = "data/transcripts"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Text Splitting Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Retrieval Configuration
    TOP_K_CHUNKS = 5
    
    # LLM Configuration
    GEMINI_MODEL = "gemini-pro"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # CORS Configuration
    ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

# Create directories if they don't exist
os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(Config.TRANSCRIPTS_PATH, exist_ok=True)