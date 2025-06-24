from flask import Flask, request, jsonify
from flask_cors import CORS
from services.youtube_service import YouTubeService
from services.rag_service import RAGService
from services.gemini_service import GeminiService
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
youtube_service = YouTubeService()
rag_service = RAGService()
gemini_service = GeminiService()

# Store processed videos in memory (in production, use a database)
processed_videos = {}

@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'Video URL is required'}), 400
        
        # Extract video ID
        video_id = youtube_service.extract_video_id(video_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
        
        # Check if already processed
        if video_id in processed_videos:
            return jsonify({
                'video_id': video_id,
                'status': 'already_processed',
                'title': processed_videos[video_id].get('title', 'Unknown')
            })
        
        # Get transcript
        transcript = youtube_service.get_transcript(video_id)
        if not transcript:
            return jsonify({'error': 'No transcript available for this video'}), 400
        
        # Process with RAG
        vector_store = rag_service.process_transcript(transcript)
        
        # Store processed video
        processed_videos[video_id] = {
            'transcript': transcript,
            'vector_store': vector_store,
            'title': youtube_service.get_video_title(video_id)
        }
        
        return jsonify({
            'video_id': video_id,
            'status': 'processed',
            'title': processed_videos[video_id]['title']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        question = data.get('question')
        
        if not video_id or not question:
            return jsonify({'error': 'Video ID and question are required'}), 400
        
        if video_id not in processed_videos:
            return jsonify({'error': 'Video not processed yet'}), 400
        
        # Retrieve relevant context
        vector_store = processed_videos[video_id]['vector_store']
        relevant_chunks = rag_service.retrieve_relevant_chunks(vector_store, question)
        
        # Generate response using Gemini
        response = gemini_service.generate_response(relevant_chunks, question)
        
        return jsonify({
            'response': response,
            'video_id': video_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/video-info/<video_id>', methods=['GET'])
def get_video_info(video_id):
    try:
        if video_id in processed_videos:
            return jsonify({
                'video_id': video_id,
                'title': processed_videos[video_id]['title'],
                'status': 'processed'
            })
        else:
            return jsonify({'error': 'Video not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)