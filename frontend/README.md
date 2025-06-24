# YouTube Chatbot - RAG-based Video Q&A

A smart chatbot that analyzes YouTube video transcripts and answers questions about the content using RAG (Retrieval-Augmented Generation) and Google's Gemini AI.

## Features

- 📺 Process any YouTube video with captions
- 🤖 AI-powered question answering using Gemini
- 🔍 RAG-based retrieval for accurate responses
- 💬 Real-time chat interface
- 🎨 YouTube Premium themed UI
- ⚡ Fast and responsive design

## Tech Stack

**Frontend:**
- React 18 with Vite
- DaisyUI + Tailwind CSS
- Axios for API calls

**Backend:**
- Python Flask
- Google Gemini AI (gemini-pro)
- LangChain for RAG implementation
- FAISS for vector storage
- YouTube Transcript API

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Google AI API key (for Gemini)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

5. Run the Flask server:
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file in the frontend directory:
```bash
VITE_API_URL=http://localhost:5000/api
```

4. Start the development server:
```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Paste a YouTube video URL in the input field
3. Click "Analyze Video" and wait for processing
4. Once processed, start asking questions about the video content
5. The AI will provide answers based on the video transcript

## API Endpoints

- `POST /api/process-video` - Process a YouTube video
- `POST /api/chat` - Send a question about a processed video
- `GET /api/video-info/<video_id>` - Get information about a processed video

## How It Works

1. **Video Processing**: Extract transcript from YouTube video using YouTube Transcript API
2. **Text Chunking**: Split transcript into manageable chunks using LangChain
3. **Embedding Generation**: Generate embeddings using Google's embedding model
4. **Vector Storage**: Store embeddings in FAISS vector database
5. **Query Processing**: When user asks a question, find relevant chunks using similarity search
6. **Answer Generation**: Use Gemini AI to generate contextual answers based on retrieved chunks

## Limitations

- Only works with YouTube videos that have captions/transcripts
- Processing time depends on video length
- Answers are limited to the content available in the transcript
- Requires active internet connection

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.