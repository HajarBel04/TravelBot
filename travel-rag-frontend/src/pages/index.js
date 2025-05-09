// src/pages/index.js
import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Layout from '../components/layout/Layout';
import ChatInterface from '../components/chat/ChatInterface';

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>TravelRAG - Your AI Travel Assistant</title>
        <meta name="description" content="AI-powered travel assistant to help plan your perfect trip" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Hero Section */}
      <div className="relative">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80" 
            alt="Travel" 
            className="w-full h-[500px] object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-40"></div>
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center text-white">
          <div className="inline-block bg-[#f2b203] text-black font-bold py-2 px-4 rounded-full mb-6">
            Travelers' Choice
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            Your AI Travel Planning Assistant
          </h1>
          <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">
            Describe your travel preferences, and we'll create a personalized itinerary just for you.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button className="bg-[#00aa6c] hover:bg-[#008a57] text-white font-bold py-3 px-8 rounded-full text-lg">
              Get Started
            </button>
            <button className="bg-white hover:bg-gray-100 text-gray-800 font-bold py-3 px-8 rounded-full text-lg">
              Explore Destinations
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-xl shadow-xl overflow-hidden">
          <div className="bg-[#00aa6c] p-4 text-white">
            <h2 className="text-2xl font-bold">AI Travel Assistant</h2>
            <p className="text-sm">Tell me about your trip, and I'll plan the perfect itinerary</p>
          </div>
          
          <ChatInterface />
        </div>
        
        {/* Popular Destinations Section */}
        <div className="mt-16">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Popular Destinations</h2>
            <Link href="/destinations" className="text-[#00aa6c] hover:text-[#008a57] font-medium">
              View All
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Destination Card 1 */}
            <div className="relative rounded-lg overflow-hidden shadow-lg group">
              <img 
                src="https://images.unsplash.com/photo-1525874684015-58379d421a52?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2270&q=80" 
                alt="Rome" 
                className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                <h3 className="text-xl font-bold mb-1">Rome, Italy</h3>
                <div className="flex items-center mb-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg key={star} className="w-4 h-4 text-[#f2b203] fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-sm">4,228 reviews</span>
                </div>
                <p className="text-sm text-gray-200 mb-3">Experience history, culture, and amazing cuisine in the Eternal City.</p>
                <button className="bg-[#00aa6c] hover:bg-[#008a57] text-white px-4 py-2 rounded-full text-sm font-medium">
                  Plan Trip
                </button>
              </div>
            </div>
            
            {/* Destination Card 2 */}
            <div className="relative rounded-lg overflow-hidden shadow-lg group">
              <img 
                src="https://images.unsplash.com/photo-1602002418816-5c0aeef426aa?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2274&q=80" 
                alt="Maldives" 
                className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                <h3 className="text-xl font-bold mb-1">Maldives</h3>
                <div className="flex items-center mb-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg key={star} className="w-4 h-4 text-[#f2b203] fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-sm">3,845 reviews</span>
                </div>
                <p className="text-sm text-gray-200 mb-3">Crystal clear waters and white sandy beaches in this tropical paradise.</p>
                <button className="bg-[#00aa6c] hover:bg-[#008a57] text-white px-4 py-2 rounded-full text-sm font-medium">
                  Plan Trip
                </button>
              </div>
            </div>
            
            {/* Destination Card 3 */}
            <div className="relative rounded-lg overflow-hidden shadow-lg group">
              <img 
                src="https://images.unsplash.com/photo-1516774935807-3f60068700d3?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
                alt="Swiss Alps" 
                className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 p-4 text-white">
                <h3 className="text-xl font-bold mb-1">Swiss Alps</h3>
                <div className="flex items-center mb-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <svg key={star} className="w-4 h-4 text-[#f2b203] fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-sm">2,567 reviews</span>
                </div>
                <p className="text-sm text-gray-200 mb-3">Breathtaking views and exhilarating hiking trails in majestic mountains.</p>
                <button className="bg-[#00aa6c] hover:bg-[#008a57] text-white px-4 py-2 rounded-full text-sm font-medium">
                  Plan Trip
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Testimonials Section */}
        <div className="mt-16 bg-white rounded-xl shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">What Travelers Say</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex text-[#f2b203]">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg key={star} className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                  </svg>
                ))}
              </div>
              <p className="mt-4 text-gray-600">"The AI travel assistant created a perfect Paris itinerary for our family. It suggested activities for our kids and found amazing restaurants within our budget."</p>
              <div className="mt-4 flex items-center">
                <div className="flex-shrink-0">
                  <span className="inline-block h-10 w-10 rounded-full bg-[#00aa6c] text-white flex items-center justify-center font-bold">JD</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">John Doe</p>
                  <p className="text-sm text-gray-500">Family Traveler</p>
                </div>
              </div>
            </div>
            
            {/* Testimonial 2 */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex text-[#f2b203]">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg key={star} className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                  </svg>
                ))}
              </div>
              <p className="mt-4 text-gray-600">"I was planning a last-minute trip to Japan and this tool saved me hours of research. It created a comprehensive itinerary with all the must-see attractions."</p>
              <div className="mt-4 flex items-center">
                <div className="flex-shrink-0">
                  <span className="inline-block h-10 w-10 rounded-full bg-[#f2b203] text-white flex items-center justify-center font-bold">AS</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Amanda Smith</p>
                  <p className="text-sm text-gray-500">Solo Adventurer</p>
                </div>
              </div>
            </div>
            
            {/* Testimonial 3 (continued) */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex text-[#f2b203]">
                {[1, 2, 3, 4, 5].map((star) => (
                  <svg key={star} className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                  </svg>
                ))}
              </div>
              <p className="mt-4 text-gray-600">"We used this for our honeymoon in Bali. The customized itinerary balanced relaxation time with adventure perfectly. Couldn't recommend it more!"</p>
              <div className="mt-4 flex items-center">
                <div className="flex-shrink-0">
                  <span className="inline-block h-10 w-10 rounded-full bg-[#00aa6c] text-white flex items-center justify-center font-bold">MJ</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">Michael Johnson</p>
                  <p className="text-sm text-gray-500">Couple Traveler</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}