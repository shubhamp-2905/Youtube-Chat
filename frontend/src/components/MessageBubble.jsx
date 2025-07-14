// src/components/MessageBubble.jsx
import React from 'react';
import '../styles/MessageBubble.css';

const MessageBubble = ({ message }) => {
  return (
    <div className={`message-bubble ${message.type}`}>
      <p>{message.text}</p>
    </div>
  );
};

export default MessageBubble;