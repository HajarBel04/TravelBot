// src/components/itinerary/ItineraryView.jsx
import React, { useState } from 'react';

export default function ItineraryView({ content, extractedInfo, packages }) {
  const [activeDay, setActiveDay] = useState(1);
  const [showInfo, setShowInfo] = useState(true);

  // This is simplified for the example
  // In a real app, you would parse the markdown content properly
  const destination = extractedInfo?.destination || (packages?.[0]?.location || 'Your Destination');
  const daysCount = 3; // This would be parsed from the content
  
  const handleDayClick = (day) => {
    setActiveDay(day);
  };

  return (
    <div className="bg-white rounded-lg overflow-hidden border border-gray-200">
      {/* Header with destination info */}
      <div className="relative h-40 overflow-hidden">
        <img 
          src={`https://source.unsplash.com/featured/?${destination.split(',')[0]},travel`} 
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
          <span className="text-sm font-medium">324 Reviews</span>
        </div>
        <span className="text-xs font-medium bg-white px-2 py-1 rounded-full">Travelers' Choice</span>
      </div>
      
      {/* Day selector - TripAdvisor style */}
      <div className="border-b border-gray-200 bg-white">
        <div className="px-4 py-2 overflow-x-auto flex space-x-2">
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
      </div>
      
      {/* Content area */}
      <div className="p-4">
        {/* Example day content - in a real app this would come from parsing the markdown */}
        {activeDay === 1 && (
          <div>
            <h3 className="text-lg font-medium text-gray-800 mb-2">Arrival & Exploration</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">AM</span>
                </div>
                <span>Arrive at your hotel and check in</span>
              </li>
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">PM</span>
                </div>
                <span>Explore the local neighborhood and enjoy dinner at a recommended restaurant</span>
              </li>
            </ul>
          </div>
        )}
        
        {activeDay === 2 && (
          <div>
            <h3 className="text-lg font-medium text-gray-800 mb-2">Cultural Immersion</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">AM</span>
                </div>
                <span>Visit the main cultural attractions and museums</span>
              </li>
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">PM</span>
                </div>
                <span>Take a guided walking tour of historical sites</span>
              </li>
            </ul>
          </div>
        )}
        
        {activeDay === 3 && (
          <div>
            <h3 className="text-lg font-medium text-gray-800 mb-2">Relaxation & Departure</h3>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">AM</span>
                </div>
                <span>Free time for shopping or relaxation</span>
              </li>
              <li className="flex items-start">
                <div className="bg-blue-100 p-1 rounded-full mr-2 mt-1">
                  <span className="text-blue-600 text-xs font-bold">PM</span>
                </div>
                <span>Check out and departure</span>
              </li>
            </ul>
          </div>
        )}
      </div>
      
      {/* Practical information */}
      <div className="border-t border-gray-200">
        <button
          onClick={() => setShowInfo(!showInfo)}
          className="w-full p-4 flex justify-between items-center bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <h3 className="font-medium text-gray-800">Practical Information</h3>
          {showInfo ? <span>▲</span> : <span>▼</span>}
        </button>
        
        {showInfo && (
          <div className="p-4">
            <div className="mb-4">
              <h4 className="font-medium text-gray-800 mb-2">Recommended Accommodations</h4>
              <ul className="list-disc list-inside text-gray-600 text-sm">
                <li>Luxury Hotel - City Center</li>
                <li>Boutique Hotel - Historic District</li>
                <li>Budget Hostel - Near Public Transportation</li>
              </ul>
            </div>
            
            <div className="mb-4">
              <h4 className="font-medium text-gray-800 mb-2">Transportation Options</h4>
              <ul className="list-disc list-inside text-gray-600 text-sm">
                <li>Public Transit - Affordable and convenient</li>
                <li>Taxi Services - Available throughout the city</li>
                <li>Rental Car - Recommended for exploring the outskirts</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-800 mb-2">Estimated Costs</h4>
              <ul className="list-disc list-inside text-gray-600 text-sm">
                <li>Accommodations: $100-300 per night</li>
                <li>Meals: $30-80 per day</li>
                <li>Activities: $20-50 per activity</li>
              </ul>
            </div>
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