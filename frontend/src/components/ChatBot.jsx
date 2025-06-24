import { useState } from "react";
import axios from "axios";

function ChatBot() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { type: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    setInput("");

    try {
      const res = await axios.post("http://localhost:8000/chat", { question: input });
      const botMsg = { type: "bot", text: res.data.answer };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [...prev, { type: "bot", text: "Something went wrong!" }]);
    }
  };

  return (
    <div className="container">
      <h2>YouTube ChatBot</h2>
      <div className="chat-box">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="input-group">
        <input
          type="text"
          placeholder="Ask something about the video..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default ChatBot;
