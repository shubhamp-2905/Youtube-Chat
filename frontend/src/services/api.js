import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for video processing
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message)
    
    // Handle different error types
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. The video might be too long or the server is busy.')
    }
    
    if (error.response) {
      // Server responded with error
      const message = error.response.data?.error || 'Server error occurred'
      throw new Error(message)
    } else if (error.request) {
      // Network error
      throw new Error('Unable to connect to server. Please check your connection.')
    } else {
      // Other error
      throw new Error('An unexpected error occurred')
    }
  }
)

export const processVideo = async (videoUrl) => {
  try {
    const response = await api.post('/process-video', {
      video_url: videoUrl
    })
    return response.data
  } catch (error) {
    console.error('Process video error:', error)
    throw error
  }
}

export const sendMessage = async (videoId, question) => {
  try {
    const response = await api.post('/chat', {
      video_id: videoId,
      question: question
    })
    return response.data
  } catch (error) {
    console.error('Send message error:', error)
    throw error
  }
}

export const getVideoInfo = async (videoId) => {
  try {
    const response = await api.get(`/video-info/${videoId}`)
    return response.data
  } catch (error) {
    console.error('Get video info error:', error)
    throw error
  }
}

export default api