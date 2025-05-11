// components/chat/MessageList.jsx
import React from 'react';
import RagResultRenderer from '../itinerary/RagResultRenderer';

export default function MessageList({ messages }) {
  return (
    <div className="space-y-4">
      {messages.map((message, index) => (
        <div 
          key={index} 
          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div 
            className={`max-w-[80%] p-3 rounded-lg shadow-sm ${
              message.type === 'user' 
                ? 'bg-[#00aa6c]/10 text-gray-800 rounded-tr-none' 
                : 'bg-white border border-gray-200 text-gray-800 rounded-tl-none'
            }`}
          >
            <p className="whitespace-pre-wrap">{message.content}</p>
            
            {message.ragResult && <RagResultRenderer result={message.ragResult} />}
          </div>
        </div>
      ))}
    </div>
  );
}