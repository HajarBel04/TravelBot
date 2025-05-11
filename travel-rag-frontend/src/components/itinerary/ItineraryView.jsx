// src/components/itinerary/ItineraryView.jsx
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown'; // Install with: npm install react-markdown

export default function ItineraryView({ content, extractedInfo, packages }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [showInfo, setShowInfo] = useState(true);

  // Get destination information
  const destination = extractedInfo?.destination || 
                     (packages && packages.length > 0 ? packages[0]?.location : 'Your Destination');
  
  // Parse markdown sections
  const extractSection = (sectionTitle) => {
    if (!content) return '';
    
    // Look for section headers (## Section Title)
    const regex = new RegExp(`## ${sectionTitle}[\\s\\S]*?(?=## |$)`, 'i');
    const match = content.match(regex);
    return match ? match[0] : '';
  };
  
  const overviewSection = content ? content.split('## Day')[0] : '';
  const daysSection = content ? content.match(/## Day[\s\S]*?(?=## Practical|$)/i)?.[0] || '' : '';
  const practicalSection = extractSection('Practical Information');
  const weatherSection = extractSection('Weather Forecast');
  const tipsSection = extractSection('Travel Tips');
  
  // Extract day count
  const dayRegex = /## Day (\d+)/g;
  let match;
  let maxDay = 0;
  while ((match = dayRegex.exec(content)) !== null) {
    const day = parseInt(match[1]);
    if (day > maxDay) maxDay = day;
  }
  const daysCount = maxDay || 3; // Default to 3 if no days found
  
  const [activeDay, setActiveDay] = useState(1);
  
  const handleDayClick = (day) => {
    setActiveDay(day);
  };
  
  const getDayContent = (day) => {
    const dayRegex = new RegExp(`## Day ${day}[\\s\\S]*?(?=## Day|## Practical|$)`, 'i');
    const match = content.match(dayRegex);
    return match ? match[0] : '';
  };

  return (
    <div className="bg-white rounded-lg overflow-hidden border border-gray-200">
      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex overflow-x-auto">
          <button 
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 ${activeTab === 'overview' ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]' : 'text-gray-500'}`}
          >
            Overview
          </button>
          <button 
            onClick={() => setActiveTab('itinerary')}
            className={`px-4 py-2 ${activeTab === 'itinerary' ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]' : 'text-gray-500'}`}
          >
            Day by Day
          </button>
          <button 
            onClick={() => setActiveTab('practical')}
            className={`px-4 py-2 ${activeTab === 'practical' ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]' : 'text-gray-500'}`}
          >
            Practical Info
          </button>
          <button 
            onClick={() => setActiveTab('weather')}
            className={`px-4 py-2 ${activeTab === 'weather' ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]' : 'text-gray-500'}`}
          >
            Weather
          </button>
          <button 
            onClick={() => setActiveTab('tips')}
            className={`px-4 py-2 ${activeTab === 'tips' ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]' : 'text-gray-500'}`}
          >
            Travel Tips
          </button>
        </div>
      </div>
      
      {/* Header with destination info */}
      <div className="relative h-40 overflow-hidden">
        <img 
          src={`https://source.unsplash.com/featured/?${destination?.split(',')[0]},travel`} 
          alt={destination}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
        <div className="absolute bottom-0 left-0 w-full p-4 text-white">
          <h2 className="text-xl font-bold">
            {destination}
          </h2>
          
          {/* Quick facts */}
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm">
            {extractedInfo?.budget && (
              <div className="flex items-center">
                <span className="mr-1">💰</span>
                <span>{extractedInfo.budget}</span>
              </div>
            )}
            
            {extractedInfo?.travelers && (
              <div className="flex items-center">
                <span className="mr-1">👥</span>
                <span>{extractedInfo.travelers}</span>
              </div>
            )}
            
            {extractedInfo?.duration && (
              <div className="flex items-center">
                <span className="mr-1">📅</span>
                <span>{extractedInfo.duration}</span>
              </div>
            )}
            
            {extractedInfo?.travel_type && (
              <div className="flex items-center">
                <span className="mr-1">❤️</span>
                <span>{extractedInfo.travel_type}</span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Rating bar - TripAdvisor style */}
      <div className="bg-[#f2b203] text-black px-4 py-2 flex justify-between items-center">
        <div className="flex items-center">
          <div className="flex mr-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <span key={star} className="text-white">★</span>
            ))}
          </div>
          <span className="text-sm font-medium">AI Generated</span>
        </div>
        <span className="text-xs font-medium bg-white px-2 py-1 rounded-full">Personalized Itinerary</span>
      </div>
      
      {/* Content based on active tab */}
      <div className="p-4">
        {activeTab === 'overview' && (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{overviewSection}</ReactMarkdown>
          </div>
        )}
        
        {activeTab === 'itinerary' && (
          <div>
            {/* Day selector */}
            <div className="overflow-x-auto flex space-x-2 mb-4">
              {Array.from({ length: daysCount }, (_, i) => i + 1).map((day) => (
                <button
                  key={day}
                  onClick={() => handleDayClick(day)}
                  className={`flex flex-col items-center justify-center min-w-[60px] py-2 px-1 rounded-md text-xs font-medium transition-colors ${
                    activeDay === day
                      ? 'bg-[#00aa6c] text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  <span className="text-xs uppercase">Day</span>
                  <span className="text-lg font-bold">{day}</span>
                </button>
              ))}
            </div>
            
            {/* Day content */}
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{getDayContent(activeDay)}</ReactMarkdown>
            </div>
          </div>
        )}
        
        {activeTab === 'practical' && (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{practicalSection}</ReactMarkdown>
          </div>
        )}
        
        {activeTab === 'weather' && (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{weatherSection}</ReactMarkdown>
          </div>
        )}
        
        {activeTab === 'tips' && (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{tipsSection}</ReactMarkdown>
          </div>
        )}
      </div>
      
      {/* Export buttons */}
      <div className="border-t border-gray-200 p-4 flex justify-end space-x-2">
        <button className="inline-flex items-center px-3 py-1 bg-[#00aa6c] text-white text-sm rounded-md hover:bg-[#008a57] transition-colors">
          <span className="mr-1">📥</span>
          Save PDF
        </button>
        
        <button className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200 transition-colors">
          <span className="mr-1">📤</span>
          Share
        </button>
      </div>
    </div>
  );
}