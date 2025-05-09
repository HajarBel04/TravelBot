// frontend/src/components/itinerary/ItineraryView.tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  ChevronDownIcon, 
  ChevronUpIcon,
  CalendarDaysIcon,
  MapPinIcon,
  CurrencyDollarIcon,
  UserGroupIcon,
  HeartIcon,
  DocumentArrowDownIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { jsPDF } from 'jspdf';
import { toPng } from 'html-to-image';
import DayItinerary from './DayItinerary';
import WeatherSection from './WeatherSection';

interface ItineraryViewProps {
  content: string;
  extractedInfo?: any;
  packages?: any[];
}

interface ParsedItinerary {
  title: string;
  overview: string;
  days: {
    day: number;
    title: string;
    morning: string[];
    afternoon: string[];
    evening: string[];
  }[];
  practicalInfo: {
    accommodations: string[];
    transportation: string[];
    costs: string[];
  };
  weather?: any;
  destinationInfo?: any;
  travelTips?: string[];
}

export default function ItineraryView({ content, extractedInfo, packages }: ItineraryViewProps) {
  const [parsedItinerary, setParsedItinerary] = useState<ParsedItinerary | null>(null);
  const [activeDay, setActiveDay] = useState(1);
  const [showWeather, setShowWeather] = useState(true);
  const [showDestinationInfo, setShowDestinationInfo] = useState(true);
  const itineraryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (content) {
      const parsedData = parseItineraryContent(content);
      setParsedItinerary(parsedData);
    }
  }, [content]);

  const parseItineraryContent = (markdown: string): ParsedItinerary => {
    // This is a simplified parser - in a real implementation, you would want a more robust markdown parser
    const lines = markdown.split('\n');
    let title = 'Travel Itinerary';
    let overview = '';
    const days: any[] = [];
    const practicalInfo = {
      accommodations: [],
      transportation: [],
      costs: []
    };
    let weather: any = null;
    let destinationInfo: any = null;
    let travelTips: string[] = [];

    // Extract title (first h1)
    const titleMatch = markdown.match(/^# (.*?)$/m);
    if (titleMatch) {
      title = titleMatch[1];
    }

    // Extract overview
    const overviewStart = markdown.indexOf('## Overview');
    const overviewEnd = markdown.indexOf('## Day 1');
    if (overviewStart !== -1 && overviewEnd !== -1) {
      overview = markdown.substring(overviewStart + 11, overviewEnd).trim();
    }

    // Extract day sections
    const dayMatches = markdown.match(/## Day \d+[\s\S]*?(?=## Day \d+|## Practical|$)/g) || [];
    dayMatches.forEach((dayContent, index) => {
      const dayNumber = index + 1;
      const dayTitle = `Day ${dayNumber}`;
      
      const morning: string[] = [];
      const afternoon: string[] = [];
      const evening: string[] = [];

      if (dayContent.includes('### Morning')) {
        const morningStart = dayContent.indexOf('### Morning');
        const morningEnd = dayContent.indexOf('### Afternoon') !== -1 
          ? dayContent.indexOf('### Afternoon') 
          : dayContent.indexOf('### Evening') !== -1
            ? dayContent.indexOf('### Evening')
            : dayContent.length;
            
        const morningContent = dayContent.substring(morningStart, morningEnd);
        const morningItems = morningContent.match(/- (.*?)$/gm);
        if (morningItems) {
          morningItems.forEach(item => morning.push(item.replace('- ', '')));
        }
      }

      if (dayContent.includes('### Afternoon')) {
        const afternoonStart = dayContent.indexOf('### Afternoon');
        const afternoonEnd = dayContent.indexOf('### Evening') !== -1 
          ? dayContent.indexOf('### Evening') 
          : dayContent.length;
            
        const afternoonContent = dayContent.substring(afternoonStart, afternoonEnd);
        const afternoonItems = afternoonContent.match(/- (.*?)$/gm);
        if (afternoonItems) {
          afternoonItems.forEach(item => afternoon.push(item.replace('- ', '')));
        }
      }

      if (dayContent.includes('### Evening')) {
        const eveningStart = dayContent.indexOf('### Evening');
        const eveningEnd = dayContent.length;
            
        const eveningContent = dayContent.substring(eveningStart, eveningEnd);
        const eveningItems = eveningContent.match(/- (.*?)$/gm);
        if (eveningItems) {
          eveningItems.forEach(item => evening.push(item.replace('- ', '')));
        }
      }

      days.push({
        day: dayNumber,
        title: dayTitle,
        morning,
        afternoon,
        evening
      });
    });

    // Extract practical information
    const practicalStart = markdown.indexOf('## Practical Information');
    if (practicalStart !== -1) {
      const practicalEnd = markdown.indexOf('##', practicalStart + 1) !== -1 
        ? markdown.indexOf('##', practicalStart + 1) 
        : markdown.length;
        
      const practicalContent = markdown.substring(practicalStart, practicalEnd);
      
      if (practicalContent.includes('### Recommended Accommodations')) {
        const accomStart = practicalContent.indexOf('### Recommended Accommodations');
        const accomEnd = practicalContent.indexOf('###', accomStart + 1) !== -1 
          ? practicalContent.indexOf('###', accomStart + 1) 
          : practicalContent.length;
          
        const accomContent = practicalContent.substring(accomStart, accomEnd);
        const accomItems = accomContent.match(/- (.*?)$/gm) || accomContent.match(/\* (.*?)$/gm);
        if (accomItems) {
          accomItems.forEach(item => practicalInfo.accommodations.push(item.replace(/^[- *] /, '')));
        }
      }
      
      if (practicalContent.includes('### Transportation Options')) {
        const transStart = practicalContent.indexOf('### Transportation Options');
        const transEnd = practicalContent.indexOf('###', transStart + 1) !== -1 
          ? practicalContent.indexOf('###', transStart + 1) 
          : practicalContent.length;
          
        const transContent = practicalContent.substring(transStart, transEnd);
        const transItems = transContent.match(/- (.*?)$/gm) || transContent.match(/\* (.*?)$/gm);
        if (transItems) {
          transItems.forEach(item => practicalInfo.transportation.push(item.replace(/^[- *] /, '')));
        }
      }
      
      if (practicalContent.includes('### Estimated Costs')) {
        const costStart = practicalContent.indexOf('### Estimated Costs');
        const costEnd = practicalContent.length;
          
        const costContent = practicalContent.substring(costStart, costEnd);
        const costItems = costContent.match(/- (.*?)$/gm) || costContent.match(/\* (.*?)$/gm);
        if (costItems) {
          costItems.forEach(item => practicalInfo.costs.push(item.replace(/^[- *] /, '')));
        }
      }
    }

    // Extract weather information
    const weatherStart = markdown.indexOf('## Weather Forecast');
    if (weatherStart !== -1) {
      const weatherEnd = markdown.indexOf('##', weatherStart + 1) !== -1 
        ? markdown.indexOf('##', weatherStart + 1) 
        : markdown.length;
        
      const weatherContent = markdown.substring(weatherStart, weatherEnd);
      
      // Parse weather data from the content
      const weatherItems = weatherContent.match(/- (.*?)$/gm) || [];
      
      if (weatherItems.length > 0) {
        weather = {
          days: weatherItems.map(item => {
            const weatherText = item.replace('- ', '');
            const weatherParts = weatherText.split(':');
            const date = weatherParts[0].trim();
            const details = weatherParts[1] ? weatherParts[1].trim() : '';
            
            return { date, details };
          })
        };
      }
    }

    // Extract destination information
    const destInfoStart = markdown.indexOf('## Destination Information');
    if (destInfoStart !== -1) {
      const destInfoEnd = markdown.indexOf('##', destInfoStart + 1) !== -1 
        ? markdown.indexOf('##', destInfoStart + 1) 
        : markdown.length;
        
      const destInfoContent = markdown.substring(destInfoStart, destInfoEnd);
      
      destinationInfo = {};
      
      // Extract country info
      const countryMatch = destInfoContent.match(/Country: (.*?)$/m);
      if (countryMatch) {
        destinationInfo.country = countryMatch[1].trim();
      }
      
      // Extract continent info
      const continentMatch = destInfoContent.match(/Continent: (.*?)$/m);
      if (continentMatch) {
        destinationInfo.continent = continentMatch[1].trim();
      }
    }

    // Extract travel tips
    const travelTipsStart = markdown.indexOf('## Travel Tips');
    if (travelTipsStart !== -1) {
      const travelTipsEnd = markdown.indexOf('##', travelTipsStart + 1) !== -1 
        ? markdown.indexOf('##', travelTipsStart + 1) 
        : markdown.length;
        
      const travelTipsContent = markdown.substring(travelTipsStart, travelTipsEnd);
      
      // Extract all sections with tips
      const tipSections = travelTipsContent.match(/### .*?\n[\s\S]*?(?=### |$)/g) || [];
      
      tipSections.forEach(section => {
        const tipItems = section.match(/- (.*?)$/gm) || [];
        tipItems.forEach(item => {
          travelTips.push(item.replace('- ', ''));
        });
      });
    }

    return {
      title,
      overview,
      days,
      practicalInfo,
      weather,
      destinationInfo,
      travelTips
    };
  };

  const exportPDF = async () => {
    if (!itineraryRef.current) return;
    
    const pdf = new jsPDF('p', 'mm', 'a4');
    
    try {
      const canvas = await toPng(itineraryRef.current, { quality: 0.95 });
      
      const imgProps = pdf.getImageProperties(canvas);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      
      pdf.addImage(canvas, 'PNG', 0, 0, pdfWidth, pdfHeight);
      
      pdf.save(`${parsedItinerary?.title || 'travel-itinerary'}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
    }
  };

  const handleDayClick = (day: number) => {
    setActiveDay(day);
  };

  if (!parsedItinerary) {
    return (
      <div className="animate-pulse p-4">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6 mb-6"></div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="mb-6">
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div ref={itineraryRef} className="bg-white rounded-lg overflow-hidden">
      {/* Header with destination info */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-500 text-white p-4">
        <h2 className="text-xl font-semibold">{parsedItinerary.title}</h2>
        
        {parsedItinerary.destinationInfo && (
          <div className="flex items-center mt-1 text-sm">
            <MapPinIcon className="h-4 w-4 mr-1" />
            <span>
              {parsedItinerary.destinationInfo.country}
              {parsedItinerary.destinationInfo.continent && `, ${parsedItinerary.destinationInfo.continent}`}
            </span>
          </div>
        )}
      </div>
      
      {/* Overview section */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="font-medium text-gray-800 mb-2">Overview</h3>
        <p className="text-gray-600 text-sm">{parsedItinerary.overview}</p>
        
        {/* Quick facts */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
          {extractedInfo?.budget && (
            <div className="flex items-center text-sm text-gray-700">
              <CurrencyDollarIcon className="h-4 w-4 text-blue-500 mr-1" />
              <span>Budget: {extractedInfo.budget}</span>
            </div>
          )}
          
          {extractedInfo?.travelers && (
            <div className="flex items-center text-sm text-gray-700">
              <UserGroupIcon className="h-4 w-4 text-blue-500 mr-1" />
              <span>Travelers: {extractedInfo.travelers}</span>
            </div>
          )}
          
          {extractedInfo?.duration && (
            <div className="flex items-center text-sm text-gray-700">
              <CalendarDaysIcon className="h-4 w-4 text-blue-500 mr-1" />
              <span>Duration: {extractedInfo.duration}</span>
            </div>
          )}
          
          {extractedInfo?.travel_type && (
            <div className="flex items-center text-sm text-gray-700">
              <HeartIcon className="h-4 w-4 text-blue-500 mr-1" />
              <span>Type: {extractedInfo.travel_type}</span>
            </div>
          )}
        </div>
      </div>
      
      {/* Day selector */}
      <div className="p-4 bg-gray-50 border-b border-gray-200 overflow-x-auto">
        <div className="flex space-x-2">
          {parsedItinerary.days.map((day) => (
            <button
              key={day.day}
              onClick={() => handleDayClick(day.day)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                activeDay === day.day
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Day {day.day}
            </button>
          ))}
        </div>
      </div>
      
      {/* Active day itinerary */}
      <div className="p-4">
        {parsedItinerary.days.map((day) => (
          <div
            key={day.day}
            className={`${activeDay === day.day ? 'block' : 'hidden'}`}
          >
            <DayItinerary day={day} />
          </div>
        ))}
      </div>
      
      {/* Weather section */}
      {parsedItinerary.weather && (
        <div className="border-t border-gray-200">
          <button
            onClick={() => setShowWeather(!showWeather)}
            className="w-full p-4 flex justify-between items-center bg-blue-50 hover:bg-blue-100 transition-colors"
          >
            <h3 className="font-medium text-blue-800">Weather Forecast</h3>
            {showWeather ? (
              <ChevronUpIcon className="h-5 w-5 text-blue-500" />
            ) : (
              <ChevronDownIcon className="h-5 w-5 text-blue-500" />
            )}
          </button>
          
          {showWeather && (
            <div className="p-4 bg-blue-50">
              <WeatherSection weather={parsedItinerary.weather} />
            </div>
          )}
        </div>
      )}
      
      {/* Practical information */}
      <div className="border-t border-gray-200">
        <button
          onClick={() => setShowDestinationInfo(!showDestinationInfo)}
          className="w-full p-4 flex justify-between items-center bg-gray-50 hover:bg-gray-100 transition-colors"
        >
          <h3 className="font-medium text-gray-800">Practical Information</h3>
          {showDestinationInfo ? (
            <ChevronUpIcon className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-gray-500" />
          )}
        </button>
        
        {showDestinationInfo && (
          <div className="p-4">
            {parsedItinerary.practicalInfo.accommodations.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-800 mb-2">Recommended Accommodations</h4>
                <ul className="list-disc list-inside text-gray-600 text-sm">
                  {parsedItinerary.practicalInfo.accommodations.map((accommodation, index) => (
                    <li key={index}>{accommodation}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {parsedItinerary.practicalInfo.transportation.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-800 mb-2">Transportation Options</h4>
                <ul className="list-disc list-inside text-gray-600 text-sm">
                  {parsedItinerary.practicalInfo.transportation.map((option, index) => (
                    <li key={index}>{option}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {parsedItinerary.practicalInfo.costs.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-800 mb-2">Estimated Costs</h4>
                <ul className="list-disc list-inside text-gray-600 text-sm">
                  {parsedItinerary.practicalInfo.costs.map((cost, index) => (
                    <li key={index}>{cost}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Travel tips */}
      {parsedItinerary.travelTips.length > 0 && (
        <div className="border-t border-gray-200 p-4">
          <h3 className="font-medium text-gray-800 mb-2">Travel Tips</h3>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {parsedItinerary.travelTips.slice(0, 6).map((tip, index) => (
              <li key={index} className="flex items-start">
                <span className="inline-block w-4 h-4 rounded-full bg-blue-100 text-blue-600 flex-shrink-0 mr-2 mt-1 flex items-center justify-center text-xs">
                  ✓
                </span>
                <span className="text-sm text-gray-600">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {/* Export buttons */}
      <div className="border-t border-gray-200 p-4 flex justify-end space-x-2">
        <button
          onClick={exportPDF}
          className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
        >
          <DocumentArrowDownIcon className="h-4 w-4 mr-1" />
          Save PDF
        </button>
        
        <button
          className="inline-flex items-center px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200 transition-colors"
        >
          <ShareIcon className="h-4 w-4 mr-1" />
          Share
        </button>
      </div>
    </div>
  );
}