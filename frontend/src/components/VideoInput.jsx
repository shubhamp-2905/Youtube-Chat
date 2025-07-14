// src/components/VideoInput.jsx
import React, { useState } from 'react';
import '../styles/VideoInput.css';
import { processVideo } from '../utils/api';

const VideoInput = ({ onProcessed }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError(null);

    try {
      const result = await processVideo(url);
      onProcessed(result.video_id, result.video_info);
    } catch (err) {
      setError('Failed to process video. Please check the URL.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit();
  };

  return (
    <div className="video-input">
      <input
        type="text"
        placeholder="Enter YouTube video URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Process Video'}
      </button>
      {error && <p className="error-msg">{error}</p>}
    </div>
  );
};

export default VideoInput;