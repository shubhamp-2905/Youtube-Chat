from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from xml.etree.ElementTree import ParseError
import json
import os
from typing import Optional, Dict, Any
from utils.youtube_utils import extract_video_id
from app.config import Config


class DocumentLoader:
    def __init__(self):
        self.transcripts_path = Config.TRANSCRIPTS_PATH

    def load_transcript(self, youtube_url: str) -> Dict[str, Any]:
        try:
            video_id = extract_video_id(youtube_url)
            if not video_id:
                raise ValueError("❌ Invalid YouTube URL")

            transcript_file = os.path.join(self.transcripts_path, f"{video_id}.json")
            if os.path.exists(transcript_file):
                print(f"📄 Loading cached transcript for video: {video_id}")
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            print(f"🎬 Fetching transcript for video: {video_id}")
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

            try:
                transcript = transcripts.find_manually_created_transcript(['en'])
                print("✅ Using manually created English transcript.")
            except NoTranscriptFound:
                try:
                    transcript = transcripts.find_generated_transcript(['en'])
                    print("⚠️ Using auto-generated English transcript.")
                except NoTranscriptFound:
                    raise Exception("❌ No transcript available in English.")

            # ✅ SAFE FETCH WITH PARSE HANDLING
            try:
                transcript_list = transcript.fetch()
                if not transcript_list or len(transcript_list) == 0:
                    raise Exception("❌ Transcript fetch succeeded but returned empty. Possibly a YouTube error.")
            except ParseError as pe:
                raise Exception(f"❌ XML Parse Error while processing transcript: {str(pe)}")

            full_text = ""
            timestamps = []

            for segment in transcript_list:
                full_text += segment['text'] + " "
                timestamps.append({
                    'start': segment['start'],
                    'duration': segment['duration'],
                    'text': segment['text']
                })

            document_data = {
                'video_id': video_id,
                'url': youtube_url,
                'full_text': full_text.strip(),
                'timestamps': timestamps,
                'total_segments': len(timestamps)
            }

            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Transcript saved successfully. Total segments: {len(timestamps)}")
            return document_data

        except VideoUnavailable:
            raise Exception("❌ Video is unavailable.")
        except TranscriptsDisabled:
            raise Exception("❌ Transcripts are disabled for this video.")
        except NoTranscriptFound:
            raise Exception("❌ No transcript found.")
        except ParseError as pe:
            raise Exception(f"❌ XML Parse Error while processing transcript: {str(pe)}")
        except Exception as e:
            print(f"❌ General error: {str(e)}")
            raise Exception(f"Failed to load transcript: {str(e)}")

    def get_cached_transcript(self, video_id: str) -> Optional[Dict[str, Any]]:
        transcript_file = os.path.join(self.transcripts_path, f"{video_id}.json")
        if os.path.exists(transcript_file):
            with open(transcript_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def clear_cache(self, video_id: str = None):
        if video_id:
            transcript_file = os.path.join(self.transcripts_path, f"{video_id}.json")
            if os.path.exists(transcript_file):
                os.remove(transcript_file)
                print(f"🗑️ Cache cleared for video: {video_id}")
        else:
            for file in os.listdir(self.transcripts_path):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.transcripts_path, file))
            print("🧹 All transcript cache cleared")
