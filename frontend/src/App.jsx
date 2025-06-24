import React, { useState } from 'react'
import VideoInput from './components/VideoInput'
import ChatInterface from './components/ChatInterface'

function App() {
  const [currentVideo, setCurrentVideo] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleVideoProcessed = (videoData) => {
    setCurrentVideo(videoData)
    setIsProcessing(false)
  }

  const handleVideoProcessing = () => {
    setIsProcessing(true)
    setCurrentVideo(null)
  }

  return (
    <div className="min-h-screen bg-base-200" data-theme="youtube">
      {/* Header */}
      <div className="navbar youtube-gradient shadow-lg">
        <div className="container mx-auto">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white">
              📺 YouTube Chatbot
            </h1>
          </div>
          <div className="flex-none">
            <div className="text-white text-sm">
              Ask questions about YouTube videos
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Video Input Section */}
          <div className="mb-8">
            <VideoInput 
              onVideoProcessed={handleVideoProcessed}
              onVideoProcessing={handleVideoProcessing}
              isProcessing={isProcessing}
            />
          </div>

          {/* Processing State */}
          {isProcessing && (
            <div className="text-center py-8">
              <div className="loading-dots mx-auto mb-4">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
              </div>
              <p className="text-gray-600">Processing video transcript...</p>
            </div>
          )}

          {/* Chat Interface */}
          {currentVideo && !isProcessing && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">
                  📹 Current Video:
                </h3>
                <p className="text-gray-600">{currentVideo.title}</p>
                <p className="text-sm text-gray-500">
                  Video ID: {currentVideo.video_id}
                </p>
              </div>
              
              <ChatInterface videoId={currentVideo.video_id} />
            </div>
          )}

          {/* Welcome Message */}
          {!currentVideo && !isProcessing && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎬</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Welcome to YouTube Chatbot
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Paste a YouTube video URL above to get started. I'll analyze the video's 
                transcript and answer any questions you have about the content. 
                No more watching entire videos to find specific information!
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="text-gray-400">
            YouTube Chatbot - Get instant answers from video content
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App