from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Create router
router = APIRouter()

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2)

# Pydantic models
class VideoProcessRequest(BaseModel):
    youtube_url: str

class VideoProcessResponse(BaseModel):
    success: bool
    message: str
    video_id: Optional[str] = None
    video_info: Optional[Dict[str, Any]] = None
    processing_stats: Optional[Dict[str, Any]] = None

# Simple storage for processed videos (in production, use a database)
processed_videos = {}

def extract_video_id(youtube_url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

def validate_and_clean_url(youtube_url: str) -> Dict[str, Any]:
    """
    Validate and clean YouTube URL
    """
    video_id = extract_video_id(youtube_url)
    
    if not video_id:
        return {
            'valid': False,
            'error': 'Invalid YouTube URL format'
        }
    
    clean_url = f"https://www.youtube.com/watch?v={video_id}"
    
    return {
        'valid': True,
        'video_id': video_id,
        'clean_url': clean_url,
        'original_url': youtube_url
    }

def process_video_sync(youtube_url: str) -> Dict[str, Any]:
    """
    Synchronous video processing function (mock implementation)
    """
    try:
        # Step 1: Validate URL
        url_info = validate_and_clean_url(youtube_url)
        if not url_info['valid']:
            return {
                'success': False,
                'message': url_info['error'],
                'step': 'url_validation'
            }
        
        video_id = url_info['video_id']
        
        # Step 2: Check if already processed
        if video_id in processed_videos:
            return {
                'success': True,
                'message': 'Video already processed',
                'video_id': video_id,
                'video_info': url_info,
                'step': 'already_processed'
            }
        
        # Mock processing steps
        print(f"Processing video: {video_id}")
        
        # Simulate processing delay
        import time
        time.sleep(2)
        
        # Store mock processed video
        processed_videos[video_id] = {
            'url_info': url_info,
            'processing_stats': {
                'total_chunks': 50,
                'transcript_length': 5000,
                'total_segments': 25
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
            
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing video: {str(e)}',
            'step': 'processing_error'
        }

@router.post("/process-video", response_model=VideoProcessResponse)
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

@router.get("/video/{video_id}/info")
async def get_video_info(video_id: str):
    """
    Get information about a processed video
    """
    try:
        if video_id not in processed_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return processed_videos[video_id]
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{video_id}/summary")
async def get_video_summary(video_id: str):
    """
    Get summary of a processed video
    """
    try:
        if video_id not in processed_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Return mock summary
        return {
            'summary': f'This is a mock summary for video {video_id}. The video discusses various topics and provides insights.',
            'video_id': video_id,
            'key_points': [
                'Key point 1',
                'Key point 2', 
                'Key point 3'
            ]
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """
    Delete a processed video from the system
    """
    try:
        if video_id not in processed_videos:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Remove from processed videos
        del processed_videos[video_id]
        
        return {"message": f"Video {video_id} deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))