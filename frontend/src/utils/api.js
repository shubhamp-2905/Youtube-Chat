// src/utils/api.js
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export const processVideo = async (url) => {
  const response = await axios.post(`${BASE_URL}/process-video`, { 
    youtube_url: url  // Changed from 'url' to 'youtube_url' to match backend model
  });
  return response.data;
};

export const sendChatMessage = async (message, video_id) => {
  const response = await axios.post(`${BASE_URL}/chat`, { 
    query: message,  // Changed from 'message' to 'query' to match backend model
    video_id: video_id 
  });
  return response.data;
};