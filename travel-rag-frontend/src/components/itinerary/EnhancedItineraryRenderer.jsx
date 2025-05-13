// src/components/itinerary/EnhancedItineraryRenderer.jsx
import React, { useState } from 'react';

export default function EnhancedItineraryRenderer({ proposal, extractedInfo, packages }) {
  const [activeDay, setActiveDay] = useState(1);
  
  // Parse the itinerary from the proposal
  const parsedItinerary = parseItinerary(proposal);
  
  // Get number of days in the itinerary
  const daysCount = parsedItinerary.days.length || 1;
  
  // Get destination from extracted info or the first package
  const destination = extractedInfo?.destination || 
    (packages && packages.length > 0 ? packages[0]?.location || packages[0]?.destination : 'Your Destination');
  
  // Get weather data if available in packages
  const weatherData = packages && packages.length > 0 ? 
    packages.find(pkg => pkg.weather_data)?.weather_data : null;
  
  // Function to render the weather icon based on precipitation
  const renderWeatherIcon = (precipitation) => {
    if (precipitation > 5) {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      );
    } else {
      return (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mx-auto text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      );
    }
  };
  
  // Function to format date string
  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch (e) {
      return dateString;
    }
  };
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-md overflow-hidden">
      {/* Hero banner with destination image */}
      <div className="relative h-60">
        <img 
          src={`https://source.unsplash.com/featured/?${destination?.split(',')[0]},travel`}
          alt={destination}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"></div>
        
        {/* Title overlay */}
        <div className="absolute bottom-0 left-0 w-full p-6 text-white">
          <div className="flex items-center mb-2">
            <div className="bg-[#f2b203] text-black text-xs font-bold px-2 py-1 rounded-sm mr-2">
              AI GENERATED
            </div>
            <h4 className="text-sm text-gray-200">Personalized Itinerary</h4>
          </div>
          <h1 className="text-3xl font-bold">{parsedItinerary.title || `Your Trip to ${destination}`}</h1>
          
          {/* Trip details */}
          <div className="flex flex-wrap gap-x-4 gap-y-2 mt-2">
            {extractedInfo?.dates && (
              <div className="flex items-center text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{extractedInfo.dates}</span>
              </div>
            )}
            
            {extractedInfo?.duration && (
              <div className="flex items-center text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{extractedInfo.duration}</span>
              </div>
            )}
            
            {extractedInfo?.travelers && (
              <div className="flex items-center text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <span>{extractedInfo.travelers}</span>
              </div>
            )}
            
            {extractedInfo?.budget && (
              <div className="flex items-center text-sm">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>{extractedInfo.budget}</span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="p-6">
        {/* Trip overview */}
        {parsedItinerary.overview && (
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-3 text-gray-900">Trip Overview</h2>
            <p className="text-gray-700">{parsedItinerary.overview}</p>
          </div>
        )}
        
        {/* Days navigation */}
        <div className="mb-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900">Day by Day Itinerary</h2>
          <div className="flex overflow-x-auto pb-2 gap-2">
            {parsedItinerary.days.map((day, index) => (
              <button
                key={index}
                onClick={() => setActiveDay(index + 1)}
                className={`flex flex-col items-center min-w-[70px] p-2 rounded-lg transition-colors ${
                  activeDay === index + 1
                    ? 'bg-[#00aa6c] text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="text-xs font-medium uppercase">Day</span>
                <span className="text-xl font-bold">{index + 1}</span>
                <span className="text-xs truncate w-full text-center">{
                  day.title 
                    ? (day.title.includes(':') ? day.title.split(':')[1]?.trim() : day.title) 
                    : ''
                }</span>
              </button>
            ))}
          </div>
        </div>
        
        {/* Active day content */}
        {parsedItinerary.days[activeDay - 1] && (
        <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-bold mb-4 text-gray-900">
            Day {activeDay}{parsedItinerary.days[activeDay - 1].title ? `: ${parsedItinerary.days[activeDay - 1].title}` : ''}
            </h3>
            
            {parsedItinerary.days[activeDay - 1].description && (
            <p className="text-sm text-gray-700 mb-4">{parsedItinerary.days[activeDay - 1].description}</p>
            )}
            
            {/* Morning activities */}
            {parsedItinerary.days[activeDay - 1].morning?.length > 0 && (
            <div className="mb-6">
                <div className="flex items-center mb-3">
                <div className="bg-yellow-100 p-1.5 rounded-full mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                </div>
                <h4 className="font-bold text-gray-800">Morning (8:00 AM - 12:00 PM)</h4>
                </div>
                <div className="border-l-2 border-yellow-200 pl-4 ml-3 space-y-3">
                {parsedItinerary.days[activeDay - 1].morning.map((activity, i) => (
                    <div key={i} className="relative">
                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-yellow-400" />
                    <div>
                        <p className="text-gray-800">{activity}</p>
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}
            
            {/* Afternoon activities */}
            {parsedItinerary.days[activeDay - 1].afternoon?.length > 0 && (
            <div className="mb-6">
                <div className="flex items-center mb-3">
                <div className="bg-blue-100 p-1.5 rounded-full mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h4 className="font-bold text-gray-800">Afternoon (12:00 PM - 5:00 PM)</h4>
                </div>
                <div className="border-l-2 border-blue-200 pl-4 ml-3 space-y-3">
                {parsedItinerary.days[activeDay - 1].afternoon.map((activity, i) => (
                    <div key={i} className="relative">
                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-blue-400" />
                    <div>
                        <p className="text-gray-800">{activity}</p>
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}
            
            {/* Evening activities */}
            {parsedItinerary.days[activeDay - 1].evening?.length > 0 && (
            <div className="mb-6">
                <div className="flex items-center mb-3">
                <div className="bg-purple-100 p-1.5 rounded-full mr-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                </div>
                <h4 className="font-bold text-gray-800">Evening (5:00 PM - 10:00 PM)</h4>
                </div>
                <div className="border-l-2 border-purple-200 pl-4 ml-3 space-y-3">
                {parsedItinerary.days[activeDay - 1].evening.map((activity, i) => (
                    <div key={i} className="relative">
                    <div className="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-purple-400" />
                    <div>
                        <p className="text-gray-800">{activity}</p>
                    </div>
                    </div>
                ))}
                </div>
            </div>
            )}
        </div>
        )}  
                
        {/* Additional information panels */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Practical information panel */}
          {parsedItinerary.practicalInfo && parsedItinerary.practicalInfo.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-bold mb-3 text-gray-900">Practical Information</h3>
              <div className="space-y-3">
                {parsedItinerary.practicalInfo.map((info, index) => (
                  <div key={index} className="flex">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#00aa6c] mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <p className="text-sm text-gray-700">{info}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Travel tips panel */}
          {parsedItinerary.travelTips && parsedItinerary.travelTips.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-bold mb-3 text-gray-900">Travel Tips</h3>
              <div className="space-y-3">
                {parsedItinerary.travelTips.map((tip, index) => (
                  <div key={index} className="flex">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#f2b203] mr-2 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-gray-700">{tip}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Weather forecast if available */}
        {weatherData && weatherData.daily && (
          <div className="mt-6 border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-bold mb-3 text-gray-900">Weather Forecast</h3>
            <div className="flex overflow-x-auto pb-2 gap-4">
              {weatherData.daily.time && weatherData.daily.time.slice(0, 5).map((date, index) => {
                const maxTemp = weatherData.daily.temperature_2m_max && weatherData.daily.temperature_2m_max[index] !== undefined ? 
                  weatherData.daily.temperature_2m_max[index] : null;
                  
                const minTemp = weatherData.daily.temperature_2m_min && weatherData.daily.temperature_2m_min[index] !== undefined ? 
                  weatherData.daily.temperature_2m_min[index] : null;
                  
                const precipitation = weatherData.daily.precipitation_sum && weatherData.daily.precipitation_sum[index] !== undefined ? 
                  weatherData.daily.precipitation_sum[index] : 0;
                
                return (
                  <div key={index} className="min-w-[100px] bg-blue-50 rounded-lg p-3 text-center">
                    <p className="font-medium text-sm text-gray-800">{formatDate(date)}</p>
                    <div className="my-2">
                      {renderWeatherIcon(precipitation)}
                    </div>
                    {(maxTemp !== null && minTemp !== null) ? (
                      <div className="flex justify-between items-center text-sm px-1">
                        <span className="font-medium text-blue-700">{Math.round(minTemp)}°</span>
                        <span className="text-gray-400">|</span>
                        <span className="font-medium text-red-600">{Math.round(maxTemp)}°</span>
                      </div>
                    ) : (
                      <div className="text-sm text-gray-600">Weather data unavailable</div>
                    )}
                    <p className="text-xs text-gray-600 mt-1">
                      {precipitation > 0 ? `${precipitation}mm` : 'No rain'}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        
        {/* Export/save buttons */}
        <div className="mt-8 flex justify-end space-x-3">
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md text-sm font-medium flex items-center hover:bg-gray-200">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
            </svg>
            Share
          </button>
          <button className="px-4 py-2 bg-[#00aa6c] text-white rounded-md text-sm font-medium flex items-center hover:bg-[#008a57]">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Save as PDF
          </button>
        </div>
      </div>
    </div>
  );
}

// Helper function to parse the itinerary from proposal text
function parseItinerary(proposal) {
  if (!proposal) return { 
    title: '', 
    overview: '', 
    days: [], 
    practicalInfo: [],
    travelTips: [] 
  };
  
  const result = {
    title: '',
    overview: '',
    days: [],
    practicalInfo: [],
    travelTips: []
  };
  
  // Get title (first h1 or first line)
  const titleMatch = proposal.match(/# (.*)/);
  if (titleMatch) result.title = titleMatch[1];
  
  // Extract overview (text before first day heading)
  const dayHeaderMatch = proposal.match(/## Day \d+/);
  if (dayHeaderMatch) {
    const overviewText = proposal.substring(0, dayHeaderMatch.index).trim();
    // Remove the title if it's in the overview
    result.overview = overviewText.replace(/# .*\n/, '').trim();
  }
  
    // Extract days with proper formatting
  const dayRegex = /## Day (\d+)(?::|) ?(.*?)(?=## Day \d+|## Practical|## Travel Tips|## Weather|$)/gs;
  let match;
  
  while ((match = dayRegex.exec(proposal)) !== null) {
    const dayNumber = parseInt(match[1]);
    // Remove any "### Morning" from the title
    const title = match[2] ? match[2].trim().replace(/### Morning.*$/m, '') : '';
    const content = match[0].split('\n').slice(1).join('\n').trim();
    
    // Parse morning, afternoon, evening activities
    const day = {
      number: dayNumber,
      title: title, // Clean title
      description: '',
      morning: [],
      afternoon: [],
      evening: []
    };
    
    // Extract morning activities, clean up the "### Morning" formatting
    const morningMatch = content.match(/### Morning.*?\n([\s\S]*?)(?=### Afternoon|### Evening|$)/s);
    if (morningMatch) {
      day.morning = parseActivities(morningMatch[1]);
    }
    
    // Extract afternoon activities
    const afternoonMatch = content.match(/### Afternoon.*?\n([\s\S]*?)(?=### Evening|$)/s);
    if (afternoonMatch) {
      day.afternoon = parseActivities(afternoonMatch[1]);
    }
    
    // Extract evening activities
    const eveningMatch = content.match(/### Evening.*?\n([\s\S]*?)$/s);
    if (eveningMatch) {
      day.evening = parseActivities(eveningMatch[1]);
    }
      
    // If no structured content, just add all content as description
    if (day.morning.length === 0 && day.afternoon.length === 0 && day.evening.length === 0) {
      day.description = content;
      
      // Try to parse unstructured activities (bullet points or numbered lists)
      const activities = parseActivities(content);
      if (activities.length > 0) {
        // Distribute activities evenly throughout the day
        const third = Math.ceil(activities.length / 3);
        day.morning = activities.slice(0, third);
        day.afternoon = activities.slice(third, third * 2);
        day.evening = activities.slice(third * 2);
      }
    }
    
    result.days.push(day);
  }
  
  // Extract practical information
  const practicalMatch = proposal.match(/## Practical Information\s+([\s\S]*?)(?=## |$)/);
  if (practicalMatch) {
    result.practicalInfo = parseActivities(practicalMatch[1]);
  }
  
  // Extract travel tips
  const tipsMatch = proposal.match(/## Travel Tips\s+([\s\S]*?)(?=## |$)/);
  if (tipsMatch) {
    result.travelTips = parseActivities(tipsMatch[1]);
  }
  
  return result;
}

// Helper function to parse activities from text (bullet points, numbered lists, or paragraphs)
function parseActivities(text) {
  if (!text) return [];
  
  // Try to match bullet points first
  const bulletMatches = text.match(/- (.*?)(?=\n- |\n\n|$)/gs);
  if (bulletMatches && bulletMatches.length > 0) {
    return bulletMatches.map(bullet => bullet.replace(/- /, '').trim());
  }
  
  // Try to match numbered lists
  const numberedMatches = text.match(/\d+\.\s+(.*?)(?=\n\d+\. |\n\n|$)/gs);
  if (numberedMatches && numberedMatches.length > 0) {
    return numberedMatches.map(item => item.replace(/\d+\.\s+/, '').trim());
  }
  
  // If no bullet points or numbers, split by lines or paragraphs
  const lines = text.split(/\n+/).filter(line => line.trim().length > 0);
  if (lines.length > 0) {
    return lines;
  }
  
  return [];
}