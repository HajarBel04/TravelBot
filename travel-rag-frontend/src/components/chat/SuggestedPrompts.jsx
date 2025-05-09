// src/components/chat/SuggestedPrompts.jsx
import React from 'react';

export default function SuggestedPrompts({ prompts, onSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {prompts.map((prompt, index) => (
        <button
          key={index}
          onClick={() => onSelect(prompt)}
          className="bg-white border border-[#00aa6c] text-[#00aa6c] rounded-full px-3 py-1 text-sm hover:bg-[#00aa6c] hover:text-white transition-colors duration-200 shadow-sm"
        >
          {prompt.length > 40 ? prompt.substring(0, 37) + '...' : prompt}
        </button>
      ))}
    </div>
  );
}