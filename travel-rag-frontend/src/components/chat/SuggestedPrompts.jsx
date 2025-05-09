// components/chat/SuggestedPrompts.jsx
import React from 'react';

export default function SuggestedPrompts({ prompts, onSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {prompts.map((prompt, index) => (
        <button
          key={index}
          onClick={() => onSelect(prompt)}
          className="bg-white border border-blue-200 rounded-full px-3 py-1 text-sm text-blue-700 hover:bg-blue-100 transition-colors"
        >
          {prompt.length > 40 ? prompt.substring(0, 37) + '...' : prompt}
        </button>
      ))}
    </div>
  );
}