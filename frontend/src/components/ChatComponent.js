import React, { useState, useEffect } from 'react';
import { socket } from '../services/socket';
import { useTranslation } from 'react-i18next';

const ChatComponent = () => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    socket.on('message', (msg) => {
      setMessages((prev) => [...prev, msg]);
    });
    return () => socket.off('message');
  }, []);

  const sendMessage = () => {
    if (input.trim()) {
      socket.emit('message', { text: input });
      setInput('');
    }
  };

  return (
    <div className="flex flex-col h-96 border rounded">
      <div className="flex-1 overflow-y-auto p-2">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2">
            <strong>{msg.user}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <div className="p-2 border-t">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder={t('send')}
          className="w-full p-2 border rounded"
        />
      </div>
    </div>
  );
};

export default ChatComponent;
