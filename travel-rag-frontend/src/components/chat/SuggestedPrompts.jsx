// src/components/chat/SuggestedPrompts.jsx
import React from 'react';

export default function SuggestedPrompts({ prompts, onSelectPrompt }) {
  return (
    <div className="grid gap-2">
      {prompts.map((prompt, index) => (
        <button
          key={index}
          onClick={() => onSelectPrompt(prompt)}
          className="text-left p-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-sm"
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}