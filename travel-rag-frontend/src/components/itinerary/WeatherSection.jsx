// components/itinerary/WeatherSection.jsx
import React from 'react';
import { 
  SunIcon, 
  CloudIcon, 
  CloudRainIcon 
} from '@heroicons/react/24/outline';

export default function WeatherSection({ weather }) {
  const getWeatherIcon = (details) => {
    if (details.toLowerCase().includes('rain') || details.toLowerCase().includes('precipitation')) {
      return <CloudRainIcon className="h-6 w-6 text-blue-500" />;
    } else if (details.toLowerCase().includes('cloud')) {
      return <CloudIcon className="h-6 w-6 text-gray-500" />;
    } else {
      return <SunIcon className="h-6 w-6 text-yellow-500" />;
    }
  };

  const getTemperatureRange = (details) => {
    // Extract temperature range from details (e.g., "26.5°C to 32.1°C, Precipitation: 0.0mm")
    const tempMatch = details.match(/(\d+\.?\d*)°C to (\d+\.?\d*)°C/);
    if (tempMatch) {
      return { min: parseFloat(tempMatch[1]), max: parseFloat(tempMatch[2]) };
    }
    return null;
  };

  const getPrecipitation = (details) => {
    // Extract precipitation from details
    const precipMatch = details.match(/Precipitation: (\d+\.?\d*)mm/);
    if (precipMatch) {
      return parseFloat(precipMatch[1]);
    }
    return 0;
  };

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {weather.days.map((day, index) => {
          const tempRange = getTemperatureRange(day.details);
          const precip = getPrecipitation(day.details);
          
          return (
            <div 
              key={index} 
              className="bg-white rounded-lg overflow-hidden shadow-sm border border-blue-100"
            >
              <div className="bg-blue-50 p-3 text-center">
                <div className="text-sm font-medium text-blue-800">{day.date}</div>
              </div>
              
              <div className="p-4 flex flex-col items-center">
                <div className="mb-2">
                  {getWeatherIcon(day.details)}
                </div>
                
                {tempRange && (
                  <div className="flex items-center justify-center space-x-2 mb-1">
                    <span className="text-blue-700 text-sm font-medium">{tempRange.min}°C</span>
                    <span className="text-gray-400">|</span>
                    <span className="text-red-500 text-sm font-medium">{tempRange.max}°C</span>
                  </div>
                )}
                
                <div className="text-xs text-gray-500">
                  {precip > 0 
                    ? `${precip}mm precipitation` 
                    : 'No precipitation'
                  }
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 bg-blue-50 p-3 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-2">Packing Suggestions</h4>
        <ul className="text-sm text-blue-700 grid grid-cols-1 md:grid-cols-2 gap-2">
          <li className="flex items-center">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Light, breathable clothing
          </li>
          <li className="flex items-center">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Sun hat and sunglasses
          </li>
          <li className="flex items-center">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Sunscreen (SPF 30+)
          </li>
          <li className="flex items-center">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Light rain jacket or umbrella
          </li>
        </ul>
      </div>
    </div>
  );
}