// src/App.jsx
import React, { useState } from 'react';
import VideoInput from './components/VideoInput';
import ChatInterface from './components/ChatInterface';
import './styles/App.css';

const App = () => {
  const [videoId, setVideoId] = useState(null);
  const [videoInfo, setVideoInfo] = useState(null);

  const handleProcessed = (id, info) => {
    setVideoId(id);
    setVideoInfo(info);
  };

  return (
    <div className="App">
      <h1 style={{ color: '#ff0000' }}>YouTube Chatbot</h1>
      <VideoInput onProcessed={handleProcessed} />
      {videoId && <ChatInterface videoId={videoId} />}
    </div>
  );
};

export default App;
