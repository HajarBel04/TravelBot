// frontend/src/components/itinerary/DayItinerary.tsx
import React from 'react';
import { 
  SunIcon, 
  CloudIcon, 
  MoonIcon 
} from '@heroicons/react/24/outline';

interface DayItineraryProps {
  day: {
    day: number;
    title: string;
    morning: string[];
    afternoon: string[];
    evening: string[];
  };
}

export default function DayItinerary({ day }: DayItineraryProps) {
  return (
    <div>
      <h3 className="text-lg font-medium text-gray-800 mb-4">{day.title}</h3>
      
      {day.morning.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <div className="bg-yellow-100 p-1.5 rounded-full mr-2">
              <SunIcon className="h-5 w-5 text-yellow-500" />
            </div>
            <h4 className="font-medium text-gray-700">Morning (8:00 AM - 12:00 PM)</h4>
          </div>
          
          <ul className="space-y-2 pl-10">
            {day.morning.map((activity, index) => (
              <li key={index} className="text-gray-600 text-sm">
                {activity}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {day.afternoon.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <div className="bg-blue-100 p-1.5 rounded-full mr-2">
              <CloudIcon className="h-5 w-5 text-blue-500" />
            </div>
            <h4 className="font-medium text-gray-700">Afternoon (12:00 PM - 5:00 PM)</h4>
          </div>
          
          <ul className="space-y-2 pl-10">
            {day.afternoon.map((activity, index) => (
              <li key={index} className="text-gray-600 text-sm">
                {activity}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {day.evening.length > 0 && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <div className="bg-purple-100 p-1.5 rounded-full mr-2">
              <MoonIcon className="h-5 w-5 text-purple-500" />
            </div>
            <h4 className="font-medium text-gray-700">Evening (5:00 PM - 10:00 PM)</h4>
          </div>
          
          <ul className="space-y-2 pl-10">
            {day.evening.map((activity, index) => (
              <li key={index} className="text-gray-600 text-sm">
                {activity}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}