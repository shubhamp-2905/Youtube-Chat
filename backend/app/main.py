from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import RAG components
from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from rag.embedding_model import EmbeddingModel
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.llm_handler import LLMHandler
from utils.youtube_utils import validate_and_clean_url
from app.config import Config

# Initialize FastAPI app
app = FastAPI(
    title="YouTube RAG Chatbot API",
    description="A RAG-based chatbot for YouTube video content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_loader = DocumentLoader()
text_splitter = TextSplitter()
embedding_model = EmbeddingModel()
vector_store = VectorStore()
retriever = Retriever()
llm_handler = LLMHandler()

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2)

# Pydantic models
class VideoProcessRequest(BaseModel):
    youtube_url: str

class ChatRequest(BaseModel):
    query: str
    video_id: Optional[str] = None

class VideoProcessResponse(BaseModel):
    success: bool
    message: str
    video_id: Optional[str] = None
    video_info: Optional[Dict[str, Any]] = None
    processing_stats: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    query: str
    video_id: Optional[str] = None
    context_used: bool = False
    relevant_chunks: Optional[list] = None

# Global storage for processed videos
processed_videos = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "YouTube RAG Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if all components are working
        stats = vector_store.get_collection_stats()
        model_info = llm_handler.get_model_info()
        
        return {
            "status": "healthy",
            "components": {
                "vector_store": "ok" if 'error' not in stats else "error",
                "llm_handler": "ok" if model_info.get('api_configured') else "error",
                "embedding_model": "ok"
            },
            "stats": stats
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

def process_video_sync(youtube_url: str) -> Dict[str, Any]:
    """
    Synchronous video processing function with debug logging
    """
    try:
        print("🔍 Received YouTube URL:", youtube_url)

        # Step 1: Validate URL
        url_info = validate_and_clean_url(youtube_url)
        print("✅ URL Validation Result:", url_info)

        if not url_info['valid']:
            return {
                'success': False,
                'message': url_info['error'],
                'step': 'url_validation'
            }

        video_id = url_info['video_id']

        # Step 2: Check if already processed
        if vector_store.video_exists(video_id):
            return {
                'success': True,
                'message': 'Video already processed',
                'video_id': video_id,
                'video_info': url_info,
                'step': 'already_processed'
            }

        # Step 3: Load transcript
        print(f"🎬 Loading transcript for video: {video_id}")
        document_data = document_loader.load_transcript(url_info['clean_url'])

        # Step 4: Split text into chunks
        print("✂️ Splitting text into chunks...")
        chunks = text_splitter.split_text(document_data['full_text'])

        # Step 5: Generate embeddings
        print("🧠 Generating embeddings...")
        embedded_chunks = embedding_model.embed_chunks(chunks)

        # Step 6: Store in vector database
        print("📦 Storing in vector database...")
        success = vector_store.add_documents(video_id, embedded_chunks)

        if success:
            # Store video info
            processed_videos[video_id] = {
                'url_info': url_info,
                'document_data': document_data,
                'processing_stats': {
                    'total_chunks': len(chunks),
                    'transcript_length': len(document_data['full_text']),
                    'total_segments': document_data['total_segments']
                }
            }

            return {
                'success': True,
                'message': 'Video processed successfully',
                'video_id': video_id,
                'video_info': url_info,
                'processing_stats': processed_videos[video_id]['processing_stats'],
                'step': 'completed'
            }

        else:
            return {
                'success': False,
                'message': 'Failed to store video data',
                'step': 'vector_storage'
            }

    except Exception as e:
        print(f"❌ Error processing video: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing video: {str(e)}',
            'step': 'processing_error'
        }


@app.post("/process-video", response_model=VideoProcessResponse)
async def process_video(request: VideoProcessRequest):
    """
    Process a YouTube video for RAG
    """
    try:
        # Run the synchronous processing in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor, 
            process_video_sync, 
            request.youtube_url
        )
        
        if result['success']:
            return VideoProcessResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the RAG system
    """
    try:
        if request.video_id:
            # Chat with video context
            print(f"Chat request for video: {request.video_id}")
            
            # Check if video exists
            if not vector_store.video_exists(request.video_id):
                raise HTTPException(status_code=404, detail="Video not found. Please process the video first.")
            
            # Retrieve relevant context
            context_result = retriever.retrieve_context(request.query, request.video_id)
            
            # Generate response with context
            response_result = llm_handler.generate_response(
                request.query, 
                context_result['context'], 
                request.video_id
            )
            
            return ChatResponse(
                response=response_result['response'],
                query=request.query,
                video_id=request.video_id,
                context_used=True,
                relevant_chunks=context_result.get('relevant_chunks', [])
            )
        else:
            # General chat without video context
            print("General chat request (no video context)")
            response_result = llm_handler.chat_without_context(request.query)
            
            return ChatResponse(
                response=response_result['response'],
                query=request.query,
                context_used=False
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video/{video_id}/summary")
async def get_video_summary(video_id: str):
    """
    Get summary of a processed video
    """
    try:
        if not vector_store.video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get video data
        if video_id in processed_videos:
            document_data = processed_videos[video_id]['document_data']
            summary_result = llm_handler.generate_summary(
                document_data['full_text'], 
                video_id
            )
            return summary_result
        else:
            raise HTTPException(status_code=404, detail="Video data not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video/{video_id}/info")
async def get_video_info(video_id: str):
    """
    Get information about a processed video
    """
    try:
        if not vector_store.video_exists(video_id):
            raise HTTPException(status_code=404, detail="Video not found")
        
        if video_id in processed_videos:
            return processed_videos[video_id]
        else:
            # Return basic info from vector store
            chunks = vector_store.get_video_chunks(video_id)
            return {
                'video_id': video_id,
                'chunk_count': len(chunks),
                'status': 'processed'
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats():
    """
    Get system statistics
    """
    try:
        vector_stats = vector_store.get_collection_stats()
        retrieval_stats = retriever.get_retrieval_stats()
        model_info = llm_handler.get_model_info()
        
        return {
            'vector_store': vector_stats,
            'retrieval_system': retrieval_stats,
            'llm_model': model_info,
            'processed_videos_count': len(processed_videos)
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """
    Delete a processed video from the system
    """
    try:
        # Delete from vector store
        deleted = vector_store.delete_video(video_id)
        
        # Remove from processed videos
        if video_id in processed_videos:
            del processed_videos[video_id]
        
        if deleted:
            return {"message": f"Video {video_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Video not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)