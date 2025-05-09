// src/pages/dashboard.js
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);
  
  // Sample data for charts
  const performanceData = [
    { name: 'Jan', extraction: 550, generation: 800, total: 1200 },
    { name: 'Feb', extraction: 520, generation: 780, total: 1150 },
    { name: 'Mar', extraction: 600, generation: 820, total: 1300 },
    { name: 'Apr', extraction: 580, generation: 850, total: 1280 },
    { name: 'May', extraction: 530, generation: 790, total: 1180 },
  ];

  const cacheData = [
    { name: 'Mon', hits: 85, misses: 15 },
    { name: 'Tue', hits: 80, misses: 20 },
    { name: 'Wed', hits: 90, misses: 10 },
    { name: 'Thu', hits: 70, misses: 30 },
    { name: 'Fri', hits: 95, misses: 5 },
  ];
  
  const pieData = [
    { name: 'Beach', value: 35 },
    { name: 'Mountain', value: 25 },
    { name: 'City', value: 30 },
    { name: 'Adventure', value: 10 },
  ];
  
  const COLORS = ['#00aa6c', '#f2b203', '#2563eb', '#ef4444'];
  
  // Popular destinations data
  const popularDestinations = [
    { name: 'Paris', count: 42, trend: 'up' },
    { name: 'Rome', count: 38, trend: 'up' },
    { name: 'New York', count: 31, trend: 'down' },
    { name: 'Tokyo', count: 27, trend: 'same' },
    { name: 'Bali', count: 23, trend: 'up' },
  ];
  
  // Simulate loading data
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <Layout>
      <Head>
        <title>Dashboard - TravelRAG</title>
        <meta name="description" content="System performance dashboard for TravelRAG" />
      </Head>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* TripAdvisor-style dashboard header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="text-gray-500">Monitor your travel assistant performance</p>
            </div>
            
            <div className="flex items-center space-x-2">
              <select 
                value={period} 
                onChange={(e) => setPeriod(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[#00aa6c]"
              >
                <option value="day">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="year">This Year</option>
              </select>
              
              <button className="bg-[#00aa6c] hover:bg-[#008a57] text-white px-4 py-2 rounded-md">
                Export Data
              </button>
            </div>
          </div>
        </div>
        
        {/* TripAdvisor-style stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center mb-3">
              <div className="bg-blue-100 p-2 rounded-full mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <p className="text-gray-500">Total Requests</p>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">2,548</h3>
            <div className="mt-1 flex items-center text-xs">
              <span className="text-green-500 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                12.3% 
              </span>
              <span className="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center mb-3">
              <div className="bg-green-100 p-2 rounded-full mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <p className="text-gray-500">Cache Hit Rate</p>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">82.5%</h3>
            <div className="mt-1 flex items-center text-xs">
              <span className="text-green-500 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                5.2% 
              </span>
              <span className="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center mb-3">
              <div className="bg-yellow-100 p-2 rounded-full mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-gray-500">Avg. Response Time</p>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">1.8s</h3>
            <div className="mt-1 flex items-center text-xs">
              <span className="text-red-500 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                3.1% 
              </span>
              <span className="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center mb-3">
              <div className="bg-[#00aa6c]/10 p-2 rounded-full mr-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#00aa6c]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z" />
                </svg>
              </div>
              <p className="text-gray-500">User Satisfaction</p>
            </div>
            <h3 className="text-2xl font-bold text-gray-900">94.2%</h3>
            <div className="mt-1 flex items-center text-xs">
              <span className="text-green-500 flex items-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                2.8% 
              </span>
              <span className="text-gray-500 ml-1">vs last month</span>
            </div>
          </div>
        </div>
        
        {/* Tab navigation */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-3 px-4 text-sm font-medium ${
                activeTab === 'overview'
                  ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('performance')}
              className={`ml-8 py-3 px-4 text-sm font-medium ${
                activeTab === 'performance'
                  ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Performance
            </button>
            <button
              onClick={() => setActiveTab('destinations')}
              className={`ml-8 py-3 px-4 text-sm font-medium ${
                activeTab === 'destinations'
                  ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Popular Destinations
            </button>
            <button
              onClick={() => setActiveTab('cache')}
              className={`ml-8 py-3 px-4 text-sm font-medium ${
                activeTab === 'cache'
                  ? 'border-b-2 border-[#00aa6c] text-[#00aa6c]'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Cache Statistics
            </button>
          </nav>
        </div>
        
        {/* Loading state */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#00aa6c]"></div>
          </div>
        ) : (
          <>
            {/* Overview tab */}
            {activeTab === 'overview' && (
              <div>
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Performance chart */}
                  <div className="lg:col-span-2 bg-white p-4 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Time</h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={performanceData}
                          margin={{ top: 10, right: 30, left: 20, bottom: 40 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip 
                            formatter={(value) => [`${value} ms`, null]}
                            labelFormatter={(label) => `Month: ${label}`}
                            contentStyle={{ backgroundColor: '#fff', borderColor: '#ddd' }}
                          />
                          <Legend />
                          <Bar dataKey="extraction" fill="#3B82F6" name="Extraction Time" />
                          <Bar dataKey="generation" fill="#10B981" name="Generation Time" />
                          <Bar dataKey="total" fill="#6366F1" name="Total Time" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  
                  {/* Distribution pie chart */}
                  <div className="bg-white p-4 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Travel Type Distribution</h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                            label={({name, percent}) => `${name} ${(percent * 100).toFixed(0)}%`}
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => [`${value}%`, null]} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
                
                {/* Popular destinations */}
                <div className="mt-6 bg-white p-4 rounded-lg shadow-md">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Popular Destinations</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Destination
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Search Count
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Trend
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {popularDestinations.map((destination, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">{destination.name}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{destination.count}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              {destination.trend === 'up' && (
                                <span className="flex items-center text-green-600">
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                  </svg>
                                  Increasing
                                </span>
                              )}
                              {destination.trend === 'down' && (
                                <span className="flex items-center text-red-600">
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </svg>
                                  Decreasing
                                </span>
                              )}
                              {destination.trend === 'same' && (
                                <span className="flex items-center text-gray-600">
                                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                                  </svg>
                                  Stable
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
            
            {/* Performance tab */}
            {activeTab === 'performance' && (
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Time Breakdown</h3>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={performanceData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip 
                          formatter={(value) => [`${value} ms`, null]}
                          contentStyle={{ backgroundColor: '#fff', borderColor: '#ddd' }}
                        />
                        <Legend />
                        <Bar dataKey="extraction" stackId="a" fill="#00aa6c" name="Information Extraction" />
                        <Bar dataKey="generation" stackId="a" fill="#f2b203" name="Proposal Generation" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Metrics</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">Extraction Completeness</span>
                          <span className="text-sm font-medium text-gray-700">75%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div className="bg-[#00aa6c] h-2.5 rounded-full" style={{ width: '75%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">Generation Quality</span>
                          <span className="text-sm font-medium text-gray-700">89%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div className="bg-[#00aa6c] h-2.5 rounded-full" style={{ width: '89%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">Structure Score</span>
                          <span className="text-sm font-medium text-gray-700">92%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div className="bg-[#00aa6c] h-2.5 rounded-full" style={{ width: '92%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-700">Information Density</span>
                          <span className="text-sm font-medium text-gray-700">68%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div className="bg-[#00aa6c] h-2.5 rounded-full" style={{ width: '68%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Comparison to Baseline</h3>
                    <div className="space-y-6">
                      <div className="flex items-center">
                        <div className="w-1/2">
                          <p className="text-sm text-gray-500">Current Extraction Time</p>
                          <p className="text-xl font-bold">432 ms</p>
                        </div>
                        <div className="w-1/2 text-right">
                          <p className="text-sm text-gray-500">Baseline</p>
                          <p className="text-xl font-bold text-gray-400">550 ms</p>
                        </div>
                        <div className="ml-4 p-1 rounded bg-green-100 text-green-600 text-xs font-medium">
                          -21.5%
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        <div className="w-1/2">
                          <p className="text-sm text-gray-500">Current Generation Time</p>
                          <p className="text-xl font-bold">1,247 ms</p>
                        </div>
                        <div className="w-1/2 text-right">
                          <p className="text-sm text-gray-500">Baseline</p>
                          <p className="text-xl font-bold text-gray-400">1,350 ms</p>
                        </div>
                        <div className="ml-4 p-1 rounded bg-green-100 text-green-600 text-xs font-medium">
                          -7.6%
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        <div className="w-1/2">
                          <p className="text-sm text-gray-500">Current Total Time</p>
                          <p className="text-xl font-bold">1,752 ms</p>
                        </div>
                        <div className="w-1/2 text-right">
                          <p className="text-sm text-gray-500">Baseline</p>
                          <p className="text-xl font-bold text-gray-400">2,135 ms</p>
                        </div>
                        <div className="ml-4 p-1 rounded bg-green-100 text-green-600 text-xs font-medium">
                          -17.9%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Destinations tab */}
            {activeTab === 'destinations' && (
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Popular Destinations</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={popularDestinations.map(d => ({ name: d.name, count: d.count }))}
                        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
                        layout="vertical"
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" />
                        <YAxis dataKey="name" type="category" width={80} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="count" fill="#00aa6c" name="Search Count" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Destination Types</h3>
                    <div className="h-80">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                            label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {pieData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => [`${value}%`, null]} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Top Destination Details</h3>
                    <div className="space-y-6">
                      <div className="text-center mb-4">
                        <img 
                          src="https://images.unsplash.com/photo-1502602898657-3e91760cbb34?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1473&q=80" 
                          alt="Paris" 
                          className="w-full h-32 object-cover rounded-lg mb-2"
                        />
                        <h4 className="text-lg font-bold text-gray-900">Paris, France</h4>
                        <div className="flex justify-center mt-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <svg 
                              key={star} 
                              className="w-4 h-4 text-[#f2b203] fill-current" 
                              xmlns="http://www.w3.org/2000/svg" 
                              viewBox="0 0 20 20"
                            >
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                          ))}
                          <span className="ml-1 text-sm text-gray-600">(4.8)</span>
                        </div>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Search Count:</span>
                          <span className="font-medium text-gray-900">42</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Trip Type:</span>
                          <span className="font-medium text-gray-900">City</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Avg. Trip Length:</span>
                          <span className="font-medium text-gray-900">5 days</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Avg. Budget:</span>
                          <span className="font-medium text-gray-900">$2,100</span>
                        </div>
                      </div>
                      
                      <button className="w-full bg-[#00aa6c] hover:bg-[#008a57] text-white py-2 rounded-md text-sm font-medium">
                        View Destination Details
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Cache tab */}
            {activeTab === 'cache' && (
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Cache Hit/Miss Ratio</h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={cacheData}
                        margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="hits" 
                          stroke="#00aa6c" 
                          name="Cache Hits %" 
                          activeDot={{ r: 8 }} 
                        />
                        <Line 
                          type="monotone" 
                          dataKey="misses" 
                          stroke="#ef4444" 
                          name="Cache Misses %" 
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Cache Statistics</h3>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Cache Type
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Entries
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Hit Rate
                            </th>
                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                              Memory Usage
                            </th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          <tr>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">Response Cache</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">42</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">78%</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">1.24 MB</div>
                            </td>
                          </tr>
                          <tr>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">Destination Cache</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">18</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">85%</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">0.75 MB</div>
                            </td>
                          </tr>
                          <tr>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">Vector Cache</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">156</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">92%</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">24.5 MB</div>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                  
                  <div className="bg-white p-6 rounded-lg shadow-md">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Cache Optimization</h3>
                    <div className="space-y-4">
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h4 className="text-sm font-medium text-blue-800 mb-2 flex items-center">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Optimization Recommendations
                        </h4>
                        <ul className="text-sm text-blue-700 space-y-2 ml-6 list-disc">
                          <li>Increase response cache TTL from 7 to 14 days</li>
                          <li>Clean up rarely accessed cache entries (25 entries accessed only once)</li>
                          <li>Preload popular destinations for faster retrieval</li>
                        </ul>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Cache Efficiency Score</h4>
                        <div className="flex items-center">
                          <div className="w-full bg-gray-200 rounded-full h-2.5 mr-2">
                            <div className="bg-[#00aa6c] h-2.5 rounded-full" style={{ width: '82%' }}></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900">82%</span>
                        </div>
                        <p className="mt-1 text-xs text-gray-500">15% improvement since last month</p>
                      </div>
                      
                      <div className="pt-4 border-t border-gray-200">
                        <div className="flex justify-between mb-1">
                          <h4 className="text-sm font-medium text-gray-700">Last Cache Rebuild</h4>
                          <span className="text-sm text-gray-500">2 days ago</span>
                        </div>
                        <div className="flex justify-between">
                          <h4 className="text-sm font-medium text-gray-700">Next Scheduled Optimization</h4>
                          <span className="text-sm text-gray-500">In 5 days</span>
                        </div>
                      </div>
                      
                      <div className="pt-4">
                        <button className="px-4 py-2 bg-[#00aa6c] hover:bg-[#008a57] text-white rounded-md text-sm font-medium">
                          Run Cache Optimization
                        </button>
                        <button className="ml-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-md text-sm font-medium">
                          Export Cache Metrics
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Cache Content Analysis</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Most Cached Destinations</h4>
                      <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                        <li>Paris, France (12 entries)</li>
                        <li>Rome, Italy (9 entries)</li>
                        <li>New York, USA (7 entries)</li>
                        <li>Tokyo, Japan (6 entries)</li>
                        <li>Bali, Indonesia (5 entries)</li>
                      </ol>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Cache Age Distribution</h4>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>0-1 days</span>
                            <span>15 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '25%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>2-3 days</span>
                            <span>22 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '37%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>4-7 days</span>
                            <span>18 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '30%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>8+ days</span>
                            <span>5 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '8%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Access Frequency</h4>
                      <div className="space-y-2">
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>1 access</span>
                            <span>25 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#f2b203] h-1.5 rounded-full" style={{ width: '42%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>2-5 accesses</span>
                            <span>19 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '32%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>6-10 accesses</span>
                            <span>10 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '17%' }}></div>
                          </div>
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-600 mb-1">
                            <span>11+ accesses</span>
                            <span>6 entries</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div className="bg-[#00aa6c] h-1.5 rounded-full" style={{ width: '10%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        
        {/* TripAdvisor-style help card */}
        <div className="mt-8 bg-[#f2b203]/10 border border-[#f2b203]/30 rounded-lg p-4 flex items-start">
          <div className="p-2 bg-[#f2b203] rounded-full mr-3 flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="font-medium text-gray-900 mb-1">Dashboard Help</h3>
            <p className="text-sm text-gray-700 mb-2">
              This dashboard provides analytics about your TravelRAG system performance and usage. 
              You can monitor processing times, cache efficiency, and popular destinations.
            </p>
            <button className="text-sm text-[#00aa6c] font-medium hover:text-[#008a57]">
              Read more about dashboard metrics
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}