// frontend/src/components/chat/ChatInterface.tsx
import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import { ExclamationCircleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import MessageItem from './MessageItem';
import SuggestedPrompts from './SuggestedPrompts';
import TypingIndicator from './TypingIndicator';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  processing?: boolean;
  error?: boolean;
}

interface ProcessedResponse {
  extracted_info: Record<string, any>;
  packages: Array<any>;
  proposal: string;
  timings?: {
    extraction_ms: number;
    generation_ms: number;
    total_ms: number;
  };
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI travel assistant. Tell me about the trip you\'re planning, and I\'ll help you create the perfect travel itinerary.',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingTime, setProcessingTime] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isProcessing) return;

    const userMessage: Message = {
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    const assistantLoadingMessage: Message = {
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
      const response = await axios.post('/api/process-email', {
        email: userMessage.content,
      });

      const data: ProcessedResponse = response.data;
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
              packages: data.packages,
              timings: data.timings,
            } as Message & { extracted_info?: any; packages?: any; timings?: any };
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

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const suggestedPrompts = [
    "I'm planning a beach vacation for my family of 4 in Hawaii next summer.",
    "I need a 7-day itinerary for Paris with a focus on museums and local cuisine.",
    "What mountain destinations would you recommend for a hiking trip in October?",
    "I'm looking for a budget-friendly city break for a long weekend.",
  ];

  return (
    <div className="flex flex-col h-[80vh] bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="bg-blue-600 text-white py-4 px-6">
        <h2 className="text-xl font-semibold">AI Travel Assistant</h2>
        {processingTime && !isProcessing && (
          <p className="text-xs text-blue-100">
            Last response generated in {(processingTime / 1000).toFixed(2)} seconds
          </p>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <MessageItem message={message} />
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isProcessing && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
      
      {messages.length === 1 && (
        <div className="px-6 py-4 bg-blue-50">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Try asking about:</h3>
          <SuggestedPrompts prompts={suggestedPrompts} onSelect={handleSuggestionClick} />
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Describe your travel plans..."
            className="flex-1 border border-gray-300 rounded-l-lg py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isProcessing}
          />
          <button
            type="submit"
            className={`bg-blue-600 hover:bg-blue-700 text-white rounded-r-lg py-3 px-4 flex items-center transition-colors ${
              isProcessing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <ArrowPathIcon className="h-5 w-5 animate-spin" />
            ) : (
              <PaperAirplaneIcon className="h-5 w-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}