import re
from typing import Optional
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various YouTube URL formats
    """
    if not url:
        return None
    
    # Regular expression patterns for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def is_valid_youtube_url(url: str) -> bool:
    """
    Check if the URL is a valid YouTube URL
    """
    if not url:
        return False
    
    youtube_domains = [
        'youtube.com',
        'www.youtube.com',
        'youtu.be',
        'www.youtu.be',
        'm.youtube.com'
    ]
    
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check if domain is YouTube
        if domain not in youtube_domains:
            return False
        
        # Check if we can extract a video ID
        video_id = extract_video_id(url)
        return video_id is not None and len(video_id) == 11
        
    except Exception:
        return False

def get_video_info_from_url(url: str) -> dict:
    """
    Extract basic info from YouTube URL
    """
    try:
        video_id = extract_video_id(url)
        
        if not video_id:
            return {
                'valid': False,
                'error': 'Invalid YouTube URL'
            }
        
        # Create standard YouTube URL
        standard_url = f"https://www.youtube.com/watch?v={video_id}"
        
        return {
            'valid': True,
            'video_id': video_id,
            'original_url': url,
            'standard_url': standard_url,
            'embed_url': f"https://www.youtube.com/embed/{video_id}",
            'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }

def normalize_youtube_url(url: str) -> Optional[str]:
    """
    Normalize YouTube URL to standard format
    """
    video_id = extract_video_id(url)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def extract_playlist_id(url: str) -> Optional[str]:
    """
    Extract playlist ID from YouTube URL (future feature)
    """
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if 'list' in query_params:
            return query_params['list'][0]
        
        return None
        
    except Exception:
        return None

def is_youtube_shorts_url(url: str) -> bool:
    """
    Check if URL is a YouTube Shorts URL
    """
    return '/shorts/' in url.lower()

def validate_and_clean_url(url: str) -> dict:
    """
    Validate and clean YouTube URL with detailed response
    """
    try:
        # Remove whitespace
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Check if it's a valid YouTube URL
        if not is_valid_youtube_url(url):
            return {
                'valid': False,
                'error': 'Not a valid YouTube URL',
                'original_url': url
            }
        
        # Extract video information
        video_info = get_video_info_from_url(url)
        
        if not video_info['valid']:
            return video_info
        
        # Additional checks
        is_shorts = is_youtube_shorts_url(url)
        playlist_id = extract_playlist_id(url)
        
        return {
            'valid': True,
            'video_id': video_info['video_id'],
            'original_url': url,
            'clean_url': video_info['standard_url'],
            'embed_url': video_info['embed_url'],
            'thumbnail_url': video_info['thumbnail_url'],
            'is_shorts': is_shorts,
            'playlist_id': playlist_id,
            'message': 'URL validated and cleaned successfully'
        }
        
    except Exception as e:
        return {
            'valid': False,
            'error': f'Error processing URL: {str(e)}',
            'original_url': url
        }