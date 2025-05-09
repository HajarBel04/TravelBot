// components/chat/TypingIndicator.jsx
import React from 'react';

export default function TypingIndicator() {
  return (
    <div className="flex items-center space-x-2 mb-4">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '200ms' }}></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{ animationDelay: '400ms' }}></div>
      </div>
      <span className="text-sm text-gray-500">Generating travel proposal...</span>
    </div>
  );
}