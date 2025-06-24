import React, { useState } from 'react'
import { processVideo } from '../services/api'

const VideoInput = ({ onVideoProcessed, onVideoProcessing, isProcessing }) => {
  const [videoUrl, setVideoUrl] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!videoUrl.trim()) {
      setError('Please enter a YouTube URL')
      return
    }

    setError('')
    onVideoProcessing()

    try {
      const response = await processVideo(videoUrl)
      onVideoProcessed(response)
    } catch (err) {
      setError(err.message || 'Failed to process video')
      onVideoProcessed(null)
    }
  }

  const isValidYouTubeUrl = (url) => {
    const patterns = [
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\n?#]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^&\n?#]+)/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^&\n?#]+)/
    ]
    return patterns.some(pattern => pattern.test(url))
  }

  const handleInputChange = (e) => {
    const value = e.target.value
    setVideoUrl(value)
    
    if (value && !isValidYouTubeUrl(value)) {
      setError('Please enter a valid YouTube URL')
    } else {
      setError('')
    }
  }

  return (
    <div className="video-input-container p-6">
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">
          🎯 Enter YouTube Video URL
        </h2>
        <p className="text-gray-600 text-sm">
          Paste any YouTube video URL and I'll analyze its content for you
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              value={videoUrl}
              onChange={handleInputChange}
              placeholder="https://www.youtube.com/watch?v=..."
              className="input input-bordered w-full focus:outline-none focus:ring-2 focus:ring-red-500"
              disabled={isProcessing}
            />
          </div>
          
          <button
            type="submit"
            disabled={isProcessing || !videoUrl.trim() || (videoUrl && !isValidYouTubeUrl(videoUrl))}
            className="btn btn-primary px-8 disabled:opacity-50"
          >
            {isProcessing ? (
              <>
                <span className="loading loading-spinner loading-sm mr-2"></span>
                Processing...
              </>
            ) : (
              'Analyze Video'
            )}
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}
      </form>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">💡 Tips:</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Works with any public YouTube video that has captions</li>
          <li>• Supports youtube.com/watch, youtu.be, and youtube.com/embed URLs</li>
          <li>• Processing may take 10-30 seconds depending on video length</li>
          <li>• Once processed, you can ask any questions about the video content</li>
        </ul>
      </div>
    </div>
  )
}

export default VideoInput