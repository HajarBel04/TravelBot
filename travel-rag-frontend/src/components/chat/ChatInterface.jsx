// src/components/chat/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import MessageItem from './MessageItem';
import SuggestedPrompts from './SuggestedPrompts';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI travel assistant. Tell me about the trip you\'re planning, and I\'ll help you create the perfect travel itinerary.',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingTime, setProcessingTime] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    const assistantLoadingMessage = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      processing: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantLoadingMessage]);
    setInputValue('');
    setIsProcessing(true);
    
    const startTime = Date.now();

    try {
      // Call your API endpoint
      const response = await fetch('/api/process-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userMessage.content }),
      });

      const data = await response.json();
      const processingMs = Date.now() - startTime;
      setProcessingTime(processingMs);

      // Update the loading message with the actual response
      setMessages((prev) =>
        prev.map((msg, index) => {
          if (index === prev.length - 1 && msg.processing) {
            return {
              role: 'assistant',
              content: data.proposal,
              timestamp: new Date(),
              extracted_info: data.extracted_info,
              packages: data.recommended_packages,
              timings: data.timings,
            };
          }
          return msg;
        })
      );
    } catch (error) {
      console.error('Error processing request:', error);
      
      // Update the loading message with an error
      setMessages((prev) =>
        prev.map((msg, index) => {
          if (index === prev.length - 1 && msg.processing) {
            return {
              role: 'assistant',
              content: 'Sorry, I encountered an error while processing your request. Please try again.',
              timestamp: new Date(),
              error: true,
            };
          }
          return msg;
        })
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
  };

  const suggestedPrompts = [
    "I'm planning a beach vacation for my family of 4 in Hawaii next summer.",
    "I need a 7-day itinerary for Paris with a focus on museums and local cuisine.",
    "What mountain destinations would you recommend for a hiking trip in October?",
    "I'm looking for a budget-friendly city break for a long weekend.",
  ];

  return (
    <div className="flex flex-col h-[500px] bg-white rounded-b-xl overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4">
        {messages.map((message, index) => (
          <div key={index} className="mb-4">
            <MessageItem message={message} />
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex items-center space-x-2 text-[#00aa6c]">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
            </div>
            <span className="text-sm">Creating your personalized travel itinerary...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {messages.length === 1 && (
        <div className="px-6 py-4 bg-blue-50 border-t border-blue-100">
          <h3 className="text-sm font-medium text-[#00aa6c] mb-2">Popular searches:</h3>
          <SuggestedPrompts prompts={suggestedPrompts} onSelect={handleSuggestionClick} />
        </div>
      )}
      
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSubmit} className="flex items-center relative">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Where would you like to travel? (e.g., 'Beach vacation in Bali for 2 weeks')"
            className="flex-1 border border-gray-300 rounded-full py-3 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-[#00aa6c] focus:border-transparent resize-none h-12 overflow-hidden"
            rows="1"
            disabled={isProcessing}
          />
          <button
            type="submit"
            className={`absolute right-2 p-2 rounded-full ${
              isProcessing ? 'bg-gray-300 cursor-not-allowed' : 'bg-[#00aa6c] hover:bg-[#008a57]'
            } text-white`}
            disabled={isProcessing}
          >
            🚀
          </button>
        </form>
        <p className="mt-2 text-xs text-gray-500 text-center">
          Ask about destinations, accommodations, activities, or specific travel preferences
        </p>
      </div>
    </div>
  );
}