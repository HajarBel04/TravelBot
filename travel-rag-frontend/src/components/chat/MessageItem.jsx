// src/components/chat/MessageItem.jsx
import React, { useState } from 'react';
import ItineraryView from '../itinerary/ItineraryView';

export default function MessageItem({ message }) {
  const [showDetails, setShowDetails] = useState(false);
  const [viewMode, setViewMode] = useState('itinerary');
  
  // Determine if this is an itinerary response
  const isItinerary = message.role === 'assistant' && 
                     (message.content?.includes('# ') || 
                      message.content?.includes('Itinerary') || 
                      message.content?.includes('Day '));

  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  // Function to safely render markdown
  const renderMarkdown = (content) => {
    if (!content) return '';
    
    // Plain text rendering - you can add a Markdown library later if needed
    return <div className="whitespace-pre-wrap">{content}</div>;
  };

  return (
    <>
      {message.role === 'user' ? (
        <div className="flex justify-end">
          <div className="bg-blue-50 text-gray-800 rounded-tl-xl rounded-tr-xl rounded-bl-xl px-4 py-3 max-w-[85%] shadow-sm border border-blue-100">
            <p className="text-sm">{message.content}</p>
            <div className="mt-1 text-right">
              <span className="text-xs text-gray-500">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      ) : message.processing ? (
        <div className="flex justify-start">
          <div className="bg-white rounded-tr-xl rounded-tl-xl rounded-br-xl px-4 py-3 max-w-[85%] shadow-sm border border-gray-100">
            <div className="flex space-x-1 items-center">
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
              <div className="w-2 h-2 bg-[#00aa6c] rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
            </div>
          </div>
        </div>
      ) : message.error ? (
        <div className="flex justify-start">
          <div className="bg-red-50 text-red-800 rounded-tr-xl rounded-tl-xl rounded-br-xl px-4 py-3 max-w-[85%] shadow-sm border border-red-100">
            <p className="text-sm">{message.content}</p>
            <div className="mt-1">
              <span className="text-xs text-red-500">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      ) : isItinerary ? (
        <div className="flex justify-start">
          <div className="bg-white rounded-tr-xl rounded-tl-xl rounded-br-xl max-w-[85%] shadow-md overflow-hidden border border-gray-200">
            <div className="bg-[#00aa6c] px-4 py-2 text-white flex justify-between items-center">
              <h3 className="font-medium">Travel Itinerary</h3>
              
              <div className="flex space-x-2 items-center">
                <div className="inline-flex rounded-md shadow-sm text-xs" role="group">
                  <button
                    type="button"
                    onClick={() => setViewMode('itinerary')}
                    className={`px-2 py-1 rounded-l-md ${
                      viewMode === 'itinerary'
                        ? 'bg-white text-[#00aa6c]'
                        : 'bg-[#00aa6c] text-white hover:bg-[#008a57]'
                    }`}
                  >
                    Pretty
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode('raw')}
                    className={`px-2 py-1 rounded-r-md ${
                      viewMode === 'raw'
                        ? 'bg-white text-[#00aa6c]'
                        : 'bg-[#00aa6c] text-white hover:bg-[#008a57]'
                    }`}
                  >
                    Text
                  </button>
                </div>
                
                {message.timings && (
                  <button
                    type="button"
                    onClick={toggleDetails}
                    className="text-white hover:text-gray-100"
                  >
                    {showDetails ? '▲' : '▼'}
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
              <div className="p-4 max-h-[400px] overflow-y-auto text-sm text-gray-800">
                {renderMarkdown(message.content)}
              </div>
            )}

            {showDetails && message.timings && (
              <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 text-xs text-gray-600">
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <p className="font-medium text-[#00aa6c]">Extraction:</p>
                    <p>{(message.timings.extraction_ms / 1000).toFixed(2)}s</p>
                  </div>
                  <div>
                    <p className="font-medium text-[#00aa6c]">Generation:</p>
                    <p>{(message.timings.generation_ms / 1000).toFixed(2)}s</p>
                  </div>
                  <div>
                    <p className="font-medium text-[#00aa6c]">Total:</p>
                    <p>{(message.timings.total_ms / 1000).toFixed(2)}s</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="px-4 py-2 border-t border-gray-200 bg-gray-50 flex justify-between items-center">
              <div className="flex space-x-2">
                <button className="text-[#00aa6c] hover:text-[#008a57] text-xs font-medium">
                  Save
                </button>
                <button className="text-[#00aa6c] hover:text-[#008a57] text-xs font-medium">
                  Share
                </button>
              </div>
              <span className="text-xs text-gray-500">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex justify-start">
          <div className="bg-white rounded-tr-xl rounded-tl-xl rounded-br-xl px-4 py-3 max-w-[85%] shadow-sm border border-gray-200">
            <p className="text-sm">{message.content}</p>
            <div className="mt-1">
              <span className="text-xs text-gray-500">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}