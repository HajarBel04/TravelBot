// frontend/src/components/chat/MessageItem.tsx
import React, { useState } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import ItineraryView from '../itinerary/ItineraryView';

interface MessageProps {
  message: {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    processing?: boolean;
    error?: boolean;
    extracted_info?: any;
    packages?: any[];
    timings?: {
      extraction_ms: number;
      generation_ms: number;
      total_ms: number;
    };
  };
}

export default function MessageItem({ message }: MessageProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [viewMode, setViewMode] = useState<'raw' | 'itinerary'>('itinerary');
  
  // Determine if this is an itinerary response
  const isItinerary = message.role === 'assistant' && 
                     (message.content.includes('# ') || 
                      message.content.includes('Itinerary') || 
                      message.content.includes('Day '));

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  return (
    <div
      className={`mb-4 ${
        message.role === 'user' ? 'flex justify-end' : 'flex justify-start'
      }`}
    >
      <div
        className={`rounded-lg px-4 py-3 max-w-[85%] ${
          message.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-none'
            : message.error
            ? 'bg-red-50 text-red-800 rounded-bl-none border border-red-200'
            : 'bg-white shadow-sm border border-gray-200 rounded-bl-none'
        }`}
      >
        {message.role === 'assistant' && isItinerary && !message.error ? (
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-medium text-gray-900">Travel Proposal</h3>
              
              <div className="flex space-x-2">
                <div className="inline-flex rounded-md shadow-sm" role="group">
                  <button
                    type="button"
                    onClick={() => setViewMode('itinerary')}
                    className={`px-3 py-1 text-xs font-medium rounded-l-lg border ${
                      viewMode === 'itinerary'
                        ? 'bg-blue-50 text-blue-700 border-blue-200'
                        : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    Itinerary View
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode('raw')}
                    className={`px-3 py-1 text-xs font-medium rounded-r-lg border ${
                      viewMode === 'raw'
                        ? 'bg-blue-50 text-blue-700 border-blue-200'
                        : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    Raw Markdown
                  </button>
                </div>
                
                {message.timings && (
                  <button
                    type="button"
                    onClick={toggleDetails}
                    className="inline-flex items-center text-xs text-gray-500 hover:text-gray-700"
                  >
                    Details
                    {showDetails ? (
                      <ChevronUpIcon className="ml-1 h-4 w-4" />
                    ) : (
                      <ChevronDownIcon className="ml-1 h-4 w-4" />
                    )}
                  </button>
                )}
              </div>
            </div>

            {viewMode === 'itinerary' ? (
              <ItineraryView 
                content={message.content} 
                extractedInfo={message.extracted_info} 
                packages={message.packages} 
              />
            ) : (
              <div className="prose prose-sm max-w-none overflow-auto text-gray-800">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}

            {showDetails && message.timings && (
              <div className="mt-4 border-t border-gray-200 pt-3 text-xs text-gray-500">
                <h4 className="font-medium text-gray-700 mb-1">Processing Details</h4>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <p className="font-medium">Extraction</p>
                    <p>{(message.timings.extraction_ms / 1000).toFixed(2)}s</p>
                  </div>
                  <div>
                    <p className="font-medium">Generation</p>
                    <p>{(message.timings.generation_ms / 1000).toFixed(2)}s</p>
                  </div>
                  <div>
                    <p className="font-medium">Total Time</p>
                    <p>{(message.timings.total_ms / 1000).toFixed(2)}s</p>
                  </div>
                </div>
                {message.extracted_info && (
                  <div className="mt-2">
                    <p className="font-medium">Extracted Information</p>
                    <pre className="mt-1 bg-gray-100 p-2 rounded text-xs overflow-auto max-h-32">
                      {JSON.stringify(message.extracted_info, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            {message.content}
          </div>
        )}
        
        <div className="mt-1 text-xs opacity-70 text-right">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}