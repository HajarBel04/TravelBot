// components/itinerary/RagResultRenderer.jsx
import React from 'react';
import DayItinerary from './DayItinerary'; // If you have this component already
import WeatherSection from './WeatherSection'; // If you have this component already

export default function RagResultRenderer({ result }) {
  if (!result) return null;
  
  return (
    <div className="mt-4 space-y-6">
      {/* Extracted Information */}
      {result.extracted_info && (
        <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-500">
          <h3 className="text-lg font-medium text-blue-800 mb-2">Understanding Your Request</h3>
          <div className="grid grid-cols-1 gap-2">
            {result.extracted_info.destination && (
              <div><span className="font-medium">Destination:</span> {result.extracted_info.destination}</div>
            )}
            {result.extracted_info.dates && (
              <div><span className="font-medium">Dates:</span> {result.extracted_info.dates}</div>
            )}
            {result.extracted_info.duration && (
              <div><span className="font-medium">Duration:</span> {result.extracted_info.duration}</div>
            )}
            {result.extracted_info.travelers && (
              <div><span className="font-medium">Travelers:</span> {result.extracted_info.travelers}</div>
            )}
            {result.extracted_info.budget && (
              <div><span className="font-medium">Budget:</span> {result.extracted_info.budget}</div>
            )}
            {result.extracted_info.interests && (
              <div><span className="font-medium">Interests:</span> {result.extracted_info.interests}</div>
            )}
          </div>
        </div>
      )}
      
      {/* Proposal/Itinerary */}
      {result.proposal && (
        <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-lg font-medium text-gray-800 mb-2">Travel Proposal</h3>
          <div className="prose max-w-none">
            {result.proposal.split('\n').map((line, i) => (
              line.startsWith('# ') ? 
                <h2 key={i} className="text-xl font-bold mt-4 mb-2">{line.substring(2)}</h2> :
              line.startsWith('## ') ?
                <h3 key={i} className="text-lg font-semibold mt-3 mb-2">{line.substring(3)}</h3> :
              line.startsWith('### ') ?
                <h4 key={i} className="text-md font-medium mt-2 mb-1">{line.substring(4)}</h4> :
              line.startsWith('- ') ?
                <div key={i} className="ml-4">• {line.substring(2)}</div> :
              line === '' ?
                <div key={i} className="h-2"></div> :
                <p key={i} className="my-1">{line}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Recommended Packages */}
      {result.recommended_packages && result.recommended_packages.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Recommended Packages</h3>
          <div className="grid grid-cols-1 gap-4">
            {result.recommended_packages.map((pkg, index) => (
              <div key={index} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
                <h4 className="text-md font-semibold text-[#00aa6c]">{pkg.name}</h4>
                <div className="mt-2 text-sm">
                  <div><span className="font-medium">Location:</span> {pkg.location || pkg.destination}</div>
                  <div><span className="font-medium">Duration:</span> {pkg.duration}</div>
                  <div><span className="font-medium">Price:</span> ${typeof pkg.price === 'object' ? pkg.price.amount : pkg.price}</div>
                </div>
                <p className="mt-2 text-sm text-gray-600">{pkg.description?.substring(0, 100)}...</p>
                {pkg.activities && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {Array.isArray(pkg.activities) ? 
                      pkg.activities.slice(0, 4).map((activity, i) => (
                        <span key={i} className="bg-green-50 text-green-700 text-xs px-2 py-1 rounded-full">
                          {typeof activity === 'object' ? activity.name : activity}
                        </span>
                      )) : null
                    }
                    {Array.isArray(pkg.activities) && pkg.activities.length > 4 && (
                      <span className="text-xs text-gray-500">+{pkg.activities.length - 4} more</span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Performance Metrics */}
      {result.timings && (
        <div className="mt-4 text-xs text-gray-500">
          <p>Processing time: {Math.round(result.timings.total_ms)}ms</p>
        </div>
      )}
    </div>
  );
}