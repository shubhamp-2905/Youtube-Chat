// src/components/ChatInterface.jsx
import React, { useState } from 'react';
import MessageBubble from './MessageBubble';
import LoadingSpinner from './LoadingSpinner';
import '../styles/ChatInterface.css';
import { sendChatMessage } from '../utils/api';

const ChatInterface = ({ videoId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMessage = { type: 'user', text: input };
    setMessages([...messages, userMessage]);
    setLoading(true);

    try {
      const response = await sendChatMessage(input, videoId);
      const botMessage = { type: 'bot', text: response.response };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [...prev, { type: 'bot', text: 'Error: Could not fetch response.' }]);
    } finally {
      setLoading(false);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="chat-interface">
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        {loading && <LoadingSpinner />}
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Ask something about the video..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
