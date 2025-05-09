// pages/destinations.js
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';
import { MapPinIcon, GlobeAmericasIcon, BuildingOffice2Icon, MountainIcon, BeakerIcon } from '@heroicons/react/24/outline';

export default function Destinations() {
  const [destinations, setDestinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

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
            activities: ['Snorkeling', 'Scuba Diving', 'Beach Relaxation']
          },
          {
            id: 2,
            name: 'Mountain Adventure',
            location: 'Swiss Alps',
            description: 'Breathtaking views and exhilarating hiking trails in the majestic Swiss Alps.',
            type: 'mountain',
            image: 'https://images.unsplash.com/photo-1531795880031-cc62a7f784dd?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2274&q=80',
            continent: 'Europe',
            country: 'Switzerland',
            activities: ['Hiking', 'Skiing', 'Mountaineering']
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
            activities: ['Sightseeing', 'Museum Tours', 'Food Tastings']
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
            activities: ['Safari Tours', 'Wildlife Photography', 'Camping']
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
            activities: ['Shopping', 'Broadway Shows', 'Museum Visits']
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
            activities: ['Eiffel Tower Visit', 'Seine River Cruise', 'Wine Tasting']
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

  const getTypeIcon = (type) => {
    switch (type) {
      case 'beach':
        return <BeakerIcon className="h-5 w-5 text-blue-500" />;
      case 'mountain':
        return <MountainIcon className="h-5 w-5 text-green-500" />;
      case 'city':
        return <BuildingOffice2Icon className="h-5 w-5 text-purple-500" />;
      case 'adventure':
        return <GlobeAmericasIcon className="h-5 w-5 text-amber-500" />;
      default:
        return <MapPinIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  return (
    <Layout>
      <Head>
        <title>Destinations - Travel RAG System</title>
        <meta name="description" content="Explore our curated list of travel destinations" />
      </Head>

      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Explore Destinations
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Browse our curated collection of amazing travel destinations
          </p>
        </div>

        {/* Filters */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-full border ${
                filter === 'all'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              All Destinations
            </button>
            <button
              onClick={() => setFilter('beach')}
              className={`px-4 py-2 rounded-full border ${
                filter === 'beach'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Beaches
            </button>
            <button
              onClick={() => setFilter('mountain')}
              className={`px-4 py-2 rounded-full border ${
                filter === 'mountain'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Mountains
            </button>
            <button
              onClick={() => setFilter('city')}
              className={`px-4 py-2 rounded-full border ${
                filter === 'city'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Cities
            </button>
            <button
              onClick={() => setFilter('adventure')}
              className={`px-4 py-2 rounded-full border ${
                filter === 'adventure'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Adventure
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline"> {error}</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDestinations.map((destination) => (
              <div
                key={destination.id}
                className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
              >
                <div className="h-48 overflow-hidden">
                  <img
                    src={destination.image}
                    alt={destination.name}
                    className="w-full h-full object-cover transition-transform hover:scale-105 duration-500"
                  />
                </div>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h2 className="font-bold text-xl text-gray-900">{destination.name}</h2>
                    {getTypeIcon(destination.type)}
                  </div>
                  <div className="flex items-center mb-3 text-sm text-gray-500">
                    <MapPinIcon className="h-4 w-4 mr-1" />
                    <span>{destination.location}, {destination.country}</span>
                  </div>
                  <p className="text-gray-600 mb-4">{destination.description}</p>
                  
                  <div className="mb-4">
                    <h3 className="text-sm font-medium text-gray-700 mb-2">Popular Activities:</h3>
                    <div className="flex flex-wrap gap-1">
                      {destination.activities.map((activity, index) => (
                        <span
                          key={index}
                          className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded-full"
                        >
                          {activity}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <button
                    className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 text-white py-2 rounded-lg hover:from-blue-700 hover:to-cyan-600 transition-colors"
                  >
                    Plan My Trip
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}