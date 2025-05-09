// src/pages/destinations.js
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../components/layout/Layout';

export default function Destinations() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [viewType, setViewType] = useState('grid');

  useEffect(() => {
    // In a real app, fetch data from API
    const fetchDestinations = async () => {
      try {
        // For now, using mock data
        const mockDestinations = [
          {
            id: 1,
            name: 'Beach Getaway',
            location: 'Maldives',
            description: 'Experience crystal clear waters and white sandy beaches in this tropical paradise.',
            type: 'beach',
            image: 'https://images.unsplash.com/photo-1602002418816-5c0aeef426aa?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2274&q=80',
            continent: 'Asia',
            country: 'Maldives',
            activities: ['Snorkeling', 'Scuba Diving', 'Beach Relaxation'],
            rating: 4.8,
            reviews: 426,
            price: '$1500'
          },
          {
            id: 2,
            name: 'Mountain Adventure',
            location: 'Swiss Alps',
            description: 'Breathtaking views and exhilarating hiking trails in the majestic Swiss Alps.',
            type: 'mountain',
            image:'https://images.unsplash.com/photo-1516774935807-3f60068700d3?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
            continent: 'Europe',
            country: 'Switzerland',
            activities: ['Hiking', 'Skiing', 'Mountaineering'],
            rating: 4.9,
            reviews: 352,
            price: '$2200'
          },
          {
            id: 3,
            name: 'Cultural Experience',
            location: 'Rome',
            description: 'Immerse yourself in history and culture in the eternal city of Rome.',
            type: 'city',
            image: 'https://images.unsplash.com/photo-1525874684015-58379d421a52?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2270&q=80',
            continent: 'Europe',
            country: 'Italy',
            activities: ['Sightseeing', 'Museum Tours', 'Food Tastings'],
            rating: 4.7,
            reviews: 578,
            price: '$1800'
          },
          {
            id: 4,
            name: 'Wildlife Safari',
            location: 'Kenya',
            description: 'Witness the incredible wildlife of Africa in their natural habitat.',
            type: 'adventure',
            image: 'https://images.unsplash.com/photo-1532274402911-5a369e4c4bb5?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2270&q=80',
            continent: 'Africa',
            country: 'Kenya',
            activities: ['Safari Tours', 'Wildlife Photography', 'Camping'],
            rating: 4.9,
            reviews: 289,
            price: '$2500'
          },
          {
            id: 5,
            name: 'City Break',
            location: 'New York',
            description: 'Experience the energy and diversity of the city that never sleeps.',
            type: 'city',
            image: 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2270&q=80',
            continent: 'North America',
            country: 'United States',
            activities: ['Shopping', 'Broadway Shows', 'Museum Visits'],
            rating: 4.6,
            reviews: 842,
            price: '$1900'
          },
          {
            id: 6,
            name: 'Romantic Getaway',
            location: 'Paris',
            description: 'Discover the city of light and love with its charming streets and iconic landmarks.',
            type: 'city',
            image: 'https://images.unsplash.com/photo-1511739001486-6bfe10ce785f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2274&q=80',
            continent: 'Europe',
            country: 'France',
            activities: ['Eiffel Tower Visit', 'Seine River Cruise', 'Wine Tasting'],
            rating: 4.8,
            reviews: 763,
            price: '$2100'
          }
        ];

        setDestinations(mockDestinations);
        setLoading(false);
      } catch (err) {
        setError('Failed to load destinations');
        setLoading(false);
      }
    };

    fetchDestinations();
  }, []);

  const filteredDestinations = filter === 'all' 
    ? destinations 
    : destinations.filter(dest => dest.type === filter);

  // Function to render stars based on rating
  const renderRating = (rating) => {
    return (
      <div className="flex items-center">
        <div className="flex mr-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <svg 
              key={star} 
              className={`w-4 h-4 ${star <= Math.floor(rating) ? 'text-[#f2b203]' : 'text-gray-300'} fill-current`} 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          ))}
        </div>
        <span className="text-sm text-gray-600">{rating} ({typeof reviews === 'number' ? reviews.toLocaleString() : '0'} reviews)</span>
      </div>
    );
  };

  // Get trip type emoji
  const getTripTypeIcon = (type) => {
    switch(type) {
      case 'beach': return '🏖️';
      case 'mountain': return '⛰️';
      case 'city': return '🏙️';
      case 'adventure': return '🧗';
      default: return '✈️';
    }
  };

  return (
    <Layout>
      <Head>
        <title>Destinations - TravelRAG</title>
        <meta name="description" content="Explore top travel destinations with TravelRAG" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* TripAdvisor-style hero banner */}
        <div className="relative rounded-xl overflow-hidden mb-8 h-40 md:h-60">
          <img 
            src="https://images.unsplash.com/photo-1488085061387-422e29b40080?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80" 
            alt="Travel destinations" 
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-40"></div>
          <div className="absolute inset-0 flex flex-col justify-center px-6 text-white text-center">
            <h1 className="text-2xl md:text-4xl font-bold mb-2">Discover Amazing Destinations</h1>
            <p className="text-sm md:text-lg">Find the perfect location for your next adventure</p>
          </div>
        </div>

        {/* Search and filter section */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="relative flex-grow max-w-xl">
              <input
                type="text"
                placeholder="Search destinations..."
                className="w-full pl-10 pr-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#00aa6c]"
              />
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setViewType('grid')}
                className={`p-2 rounded ${viewType === 'grid' ? 'bg-gray-200' : 'bg-white'}`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </button>
              <button
                onClick={() => setViewType('list')}
                className={`p-2 rounded ${viewType === 'list' ? 'bg-gray-200' : 'bg-white'}`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
          
          {/* Category filters */}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-full font-medium text-sm transition-colors ${
                filter === 'all'
                  ? 'bg-[#00aa6c] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All Destinations
            </button>
            <button
              onClick={() => setFilter('beach')}
              className={`px-4 py-2 rounded-full font-medium text-sm transition-colors ${
                filter === 'beach'
                  ? 'bg-[#00aa6c] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🏖️ Beaches
            </button>
            <button
              onClick={() => setFilter('mountain')}
              className={`px-4 py-2 rounded-full font-medium text-sm transition-colors ${
                filter === 'mountain'
                  ? 'bg-[#00aa6c] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              ⛰️ Mountains
            </button>
            <button
              onClick={() => setFilter('city')}
              className={`px-4 py-2 rounded-full font-medium text-sm transition-colors ${
                filter === 'city'
                  ? 'bg-[#00aa6c] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🏙️ Cities
            </button>
            <button
              onClick={() => setFilter('adventure')}
              className={`px-4 py-2 rounded-full font-medium text-sm transition-colors ${
                filter === 'adventure'
                  ? 'bg-[#00aa6c] text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🧗 Adventures
            </button>
          </div>
        </div>

        {/* Results count */}
        <div className="flex justify-between items-center mb-4">
          <p className="text-gray-600">{filteredDestinations.length} destinations found</p>
          <div className="flex items-center">
            <span className="text-gray-600 mr-2">Sort by:</span>
            <select className="border border-gray-300 rounded-md px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-[#00aa6c]">
              <option>Recommended</option>
              <option>Price: Low to High</option>
              <option>Price: High to Low</option>
              <option>Rating</option>
            </select>
          </div>
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#00aa6c]"></div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-1">{error}</span>
          </div>
        )}

        {/* Grid view */}
        {!loading && !error && viewType === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDestinations.map((destination) => (
              <div key={destination.id} className="bg-white rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
                {/* TripAdvisor-style card with ribbon */}
                <div className="relative">
                  <img
                    src={destination.image}
                    alt={destination.name}
                    className="w-full h-48 object-cover"
                  />
                  {destination.rating >= 4.8 && (
                    <div className="absolute top-0 right-0 bg-[#f2b203] text-xs font-bold px-2 py-1 text-white">
                      Travelers' Choice
                    </div>
                  )}
                </div>
                
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h2 className="text-lg font-bold text-gray-900">{destination.name}</h2>
                    <span className="text-xl">{getTripTypeIcon(destination.type)}</span>
                  </div>
                  
                  <div className="flex items-center mb-2 text-sm text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    {destination.location}, {destination.country}
                  </div>
                  
                  {/* TripAdvisor-style ratings */}
                  {renderRating(destination.rating)}
                  
                  <p className="text-gray-600 text-sm my-3 line-clamp-2">{destination.description}</p>
                  
                  <div className="mb-3">
                    <div className="text-sm font-medium text-gray-900 mb-1">Popular Activities:</div>
                    <div className="flex flex-wrap gap-1">
                      {destination.activities.slice(0, 3).map((activity, index) => (
                        <span key={index} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">
                          {activity}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* Price line like TripAdvisor */}
                  <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
                    <div>
                      <p className="text-xs text-gray-500">From</p>
                      <p className="text-lg font-bold text-[#00aa6c]">{destination.price}</p>
                    </div>
                    <button className="px-4 py-2 bg-[#00aa6c] hover:bg-[#008a57] text-white rounded-full text-sm font-medium">
                      View Trip
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* List view */}
        {!loading && !error && viewType === 'list' && (
          <div className="space-y-4">
            {filteredDestinations.map((destination) => (
              <div key={destination.id} className="bg-white rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-shadow duration-300">
                <div className="flex flex-col md:flex-row">
                  <div className="relative md:w-1/3">
                    <img
                      src={destination.image}
                      alt={destination.name}
                      className="w-full h-48 md:h-full object-cover"
                    />
                    {destination.rating >= 4.8 && (
                      <div className="absolute top-0 right-0 bg-[#f2b203] text-xs font-bold px-2 py-1 text-white">
                        Travelers' Choice
                      </div>
                    )}
                  </div>
                  
                  <div className="p-4 md:w-2/3">
                    <div className="flex justify-between items-start mb-2">
                      <h2 className="text-lg font-bold text-gray-900">{destination.name}</h2>
                      <span className="text-xl">{getTripTypeIcon(destination.type)}</span>
                    </div>
                    
                    <div className="flex items-center mb-2 text-sm text-gray-600">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {destination.location}, {destination.country}
                    </div>
                    
                    {/* TripAdvisor-style ratings */}
                    {renderRating(destination.rating)}
                    
                    <p className="text-gray-600 text-sm my-3">{destination.description}</p>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium text-gray-900 mb-1">Popular Activities:</div>
                      <div className="flex flex-wrap gap-1">
                        {destination.activities.map((activity, index) => (
                          <span key={index} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full">
                            {activity}
                          </span>
                        ))}
                      </div>
                    </div>
                    
                    {/* Price line like TripAdvisor */}
                    <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
                      <div>
                        <p className="text-xs text-gray-500">From</p>
                        <p className="text-lg font-bold text-[#00aa6c]">{destination.price}</p>
                      </div>
                      <button className="px-4 py-2 bg-[#00aa6c] hover:bg-[#008a57] text-white rounded-full text-sm font-medium">
                        View Trip
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Pagination */}
        <div className="mt-8 flex justify-center">
          <nav className="inline-flex rounded-md shadow">
            <a href="#" className="px-3 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              Previous
            </a>
            <a href="#" className="px-3 py-2 border-t border-b border-gray-300 bg-white text-sm font-medium text-[#00aa6c]">
              1
            </a>
            <a href="#" className="px-3 py-2 border-t border-b border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              2
            </a>
            <a href="#" className="px-3 py-2 border-t border-b border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              3
            </a>
            <a href="#" className="px-3 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              Next
            </a>
          </nav>
        </div>
      </div>
    </Layout>
  );
}