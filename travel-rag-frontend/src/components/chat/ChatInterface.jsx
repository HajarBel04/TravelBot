// components/chat/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useEmailProcessor } from '../../../hooks/useRagApi';
import MessageList from './MessageList.jsx';
import TypingIndicator from './TypingIndicator';
import SuggestedPrompts from './SuggestedPrompts';

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: "Hello! I'm your AI travel assistant. Tell me about your dream vacation, and I'll create a personalized itinerary for you."
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const { processEmail, loading, result } = useEmailProcessor();
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Example suggested prompts
  const suggestedPrompts = [
    "I want to plan a beach vacation to Maldives for 2 weeks in July. We are a couple with a budget of $5000.",
    "Looking for a family-friendly trip to Rome for 5 days in August with kids aged 8 and 10. Budget: $3000.",
    "Planning a hiking adventure in the Swiss Alps for a week in September. I'm a solo traveler with a $2000 budget."
  ];

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage = {
      type: 'user',
      content: inputValue
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    try {
      // Process the email with RAG system
      const ragResult = await processEmail(userMessage.content);

      if (ragResult) {
        // Add assistant response with the RAG result
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: "I've analyzed your request and created a travel proposal for you:",
          ragResult: ragResult
        }]);
      } else {
        // Handle error case
        setMessages(prev => [...prev, {
          type: 'assistant',
          content: "I'm sorry, I couldn't process your request. Please try again with more details about your travel plans."
        }]);
      }
    } catch (error) {
      console.error('Error processing request:', error);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: "I'm sorry, there was an error processing your request. Please try again later."
      }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestedPrompt = (prompt) => {
    setInputValue(prompt);
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      
      {loading && (
        <div className="px-4 pb-2">
          <TypingIndicator />
        </div>
      )}
      
      <div className="p-4 bg-white border-t border-gray-200">
        {messages.length === 1 && (
          <div className="mb-4">
            <SuggestedPrompts prompts={suggestedPrompts} onSelectPrompt={handleSuggestedPrompt} />
          </div>
        )}
        
        <div className="flex items-center">
          <textarea
            className="flex-1 border border-gray-300 rounded-l-lg p-3 focus:outline-none focus:ring-2 focus:ring-[#00aa6c] resize-none"
            placeholder="Describe your travel plans..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            rows="2"
            disabled={loading}
          />
          <button
            className={`bg-[#00aa6c] hover:bg-[#008a57] text-white p-3 rounded-r-lg ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            onClick={handleSendMessage}
            disabled={loading || !inputValue.trim()}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}