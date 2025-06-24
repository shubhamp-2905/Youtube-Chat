import React, { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../services/api'

const ChatInterface = ({ videoId }) => {
  const [messages, setMessages] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Reset messages when video changes
    setMessages([
      {
        type: 'bot',
        content: 'Hi! I\'ve analyzed the video transcript. Ask me anything about the content!',
        timestamp: new Date()
      }
    ])
  }, [videoId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!currentMessage.trim() || isLoading) return

    const userMessage = {
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsLoading(true)

    try {
      const response = await sendMessage(videoId, currentMessage)
      
      const botMessage = {
        type: 'bot',
        content: response.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content.split('\n').map((line, index) => (
      <span key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </span>
    ))
  }

  const suggestedQuestions = [
    "Can you summarize the main points?",
    "What are the key topics discussed?",
    "Are there any important timestamps mentioned?",
    "What conclusions were drawn?"
  ]

  const handleSuggestedQuestion = (question) => {
    setCurrentMessage(question)
  }

  return (
    <div className="chat-interface">
      {/* Messages Container */}
      <div className="chat-container p-4 space-y-4 border border-gray-200 rounded-lg mb-4">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-2 ${
              message.type === 'user' ? 'message-user' : 'message-bot'
            }`}>
              <div className="text-sm">
                {formatMessage(message.content)}
              </div>
              <div className={`text-xs mt-1 opacity-70 ${
                message.type === 'user' ? 'text-white' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="message-bot max-w-xs lg:max-w-md px-4 py-2">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-gray-500 text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length === 1 && (
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">💭 Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuestion(question)}
                className="btn btn-outline btn-sm text-xs"
                disabled={isLoading}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder="Ask me anything about the video..."
            className="input input-bordered w-full focus:outline-none focus:ring-2 focus:ring-red-500"
            disabled={isLoading}
          />
        </div>
        
        <button
          type="submit"
          disabled={!currentMessage.trim() || isLoading}
          className="btn btn-primary px-6 disabled:opacity-50"
        >
          {isLoading ? (
            <span className="loading loading-spinner loading-sm"></span>
          ) : (
            <span>Send</span>
          )}
        </button>
      </form>

      {/* Chat Tips */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          💡 <strong>Pro tip:</strong> Be specific in your questions for better answers. 
          Ask about particular topics, quotes, or sections of the video.
        </p>
      </div>
    </div>
  )
}

export default ChatInterface