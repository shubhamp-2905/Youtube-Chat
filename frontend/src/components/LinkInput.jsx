import { useState } from "react";
import axios from "axios";

function LinkInput({ onProcessed }) {
  const [url, setUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:8000/process", { url });
      onProcessed();
    } catch (err) {
      alert("Failed to process the video.");
    }
  };

  return (
    <div className="container">
      <h2>Enter YouTube Video URL</h2>
      <form onSubmit={handleSubmit} className="input-group">
        <input
          type="text"
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button type="submit">Process</button>
      </form>
    </div>
  );
}

export default LinkInput;
