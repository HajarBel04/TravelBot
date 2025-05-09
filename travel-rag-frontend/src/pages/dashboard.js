// pages/dashboard.js
import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
          throw new Error('Failed to fetch metrics');
        }
        const data = await response.json();
        setMetrics(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  // Mock data for development
  const mockPerformanceData = [
    { name: 'Jan', extraction: 550, generation: 800, total: 1200 },
    { name: 'Feb', extraction: 520, generation: 780, total: 1150 },
    { name: 'Mar', extraction: 600, generation: 820, total: 1300 },
    { name: 'Apr', extraction: 580, generation: 850, total: 1280 },
    { name: 'May', extraction: 530, generation: 790, total: 1180 },
  ];

  const mockCacheData = [
    { name: 'Mon', hits: 85, misses: 15 },
    { name: 'Tue', hits: 80, misses: 20 },
    { name: 'Wed', hits: 90, misses: 10 },
    { name: 'Thu', hits: 70, misses: 30 },
    { name: 'Fri', hits: 95, misses: 5 },
  ];

  return (
    <Layout>
      <Head>
        <title>Dashboard - Travel RAG System</title>
        <meta name="description" content="System performance metrics for the Travel RAG System" />
      </Head>

      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">System Dashboard</h1>
          <p className="mt-2 text-lg text-gray-600">
            Monitor performance metrics and system statistics
          </p>
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
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Metrics Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-blue-500 p-4">
                <h2 className="text-white text-xl font-semibold">Performance Metrics</h2>
              </div>
              <div className="p-4">
                <p className="text-gray-600 mb-4">Average processing times in milliseconds</p>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={mockPerformanceData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="extraction" fill="#3B82F6" name="Extraction Time" />
                      <Bar dataKey="generation" fill="#10B981" name="Generation Time" />
                      <Bar dataKey="total" fill="#6366F1" name="Total Time" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Cache Statistics Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-cyan-500 to-cyan-400 p-4">
                <h2 className="text-white text-xl font-semibold">Cache Performance</h2>
              </div>
              <div className="p-4">
                <p className="text-gray-600 mb-4">Cache hit/miss ratio over time</p>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={mockCacheData}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="hits" stroke="#10B981" name="Cache Hits %" />
                      <Line type="monotone" dataKey="misses" stroke="#EF4444" name="Cache Misses %" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Quality Metrics Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-amber-500 to-amber-400 p-4">
                <h2 className="text-white text-xl font-semibold">Quality Metrics</h2>
              </div>
              <div className="p-4">
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-800 mb-2">Extraction Completeness</h3>
                    <div className="relative pt-1">
                      <div className="overflow-hidden h-2 mb-1 text-xs flex rounded bg-amber-100">
                        <div 
                          style={{ width: `${(metrics?.performance?.extraction?.extraction_completeness || 0.6) * 100}%` }} 
                          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-amber-500"
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>0%</span>
                        <span>{Math.round((metrics?.performance?.extraction?.extraction_completeness || 0.6) * 100)}%</span>
                        <span>100%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-2">Generation Quality</h3>
                    <div className="relative pt-1">
                      <div className="overflow-hidden h-2 mb-1 text-xs flex rounded bg-amber-100">
                        <div 
                          style={{ width: `${(metrics?.performance?.generation?.quality_score || 0.8) * 100}%` }} 
                          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-amber-500"
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>0%</span>
                        <span>{Math.round((metrics?.performance?.generation?.quality_score || 0.8) * 100)}%</span>
                        <span>100%</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-800 mb-2">Retrieval Diversity</h3>
                    <div className="relative pt-1">
                      <div className="overflow-hidden h-2 mb-1 text-xs flex rounded bg-amber-100">
                        <div 
                          style={{ width: `${(metrics?.performance?.retrieval?.location_diversity || 0.7) * 100}%` }} 
                          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-amber-500"
                        ></div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>0%</span>
                        <span>{Math.round((metrics?.performance?.retrieval?.location_diversity || 0.7) * 100)}%</span>
                        <span>100%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* System Stats Card */}
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              <div className="bg-gradient-to-r from-purple-600 to-purple-500 p-4">
                <h2 className="text-white text-xl font-semibold">System Information</h2>
              </div>
              <div className="p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <h3 className="font-medium text-purple-800 mb-2">Vector Store</h3>
                    <p className="text-gray-600">Documents: {metrics?.vector_store?.documents || 'N/A'}</p>
                  </div>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h3 className="font-medium text-blue-800 mb-2">Response Cache</h3>
                    <p className="text-gray-600">Entries: {metrics?.cache?.response_cache?.total_entries || 'N/A'}</p>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h3 className="font-medium text-green-800 mb-2">Destination Cache</h3>
                    <p className="text-gray-600">Entries: {metrics?.cache?.destination_cache?.total_entries || 'N/A'}</p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h3 className="font-medium text-yellow-800 mb-2">Last Updated</h3>
                    <p className="text-gray-600">{metrics?.performance?.timestamp || 'Unknown'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}