from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import re
import requests

class YouTubeService:
    def __init__(self):
        pass
    
    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^&\n?#]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just an ID
        if len(url) == 11 and url.isalnum():
            return url
        
        return None
    
    def get_transcript(self, video_id):
        """Get transcript for a YouTube video"""
        try:
            # Try to get English transcript first
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=['en', 'en-US', 'en-GB']
            )
            
            # Flatten to plain text
            transcript = " ".join(chunk["text"] for chunk in transcript_list)
            return transcript
            
        except TranscriptsDisabled:
            print(f"No captions available for video {video_id}")
            return None
        except Exception as e:
            print(f"Error getting transcript: {str(e)}")
            return None
    
    def get_video_title(self, video_id):
        """Get video title (basic implementation)"""
        try:
            # This is a simple approach - in production, you might want to use YouTube API
            url = f"https://www.youtube.com/watch?v={video_id}"
            response = requests.get(url)
            
            # Extract title from HTML (basic regex)
            title_match = re.search(r'<title>(.+?) - YouTube</title>', response.text)
            if title_match:
                return title_match.group(1)
            else:
                return f"Video {video_id}"
                
        except Exception as e:
            print(f"Error getting video title: {str(e)}")
            return f"Video {video_id}"