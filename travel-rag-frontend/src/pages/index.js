// src/pages/index.js
import React from 'react';
import Head from 'next/head';
import Layout from '../components/layout/Layout'; // Update this path
import ChatInterface from '../components/chat/ChatInterface'; // Update this path


export default function Home() {
  return (
    <Layout>
      <Head>
        <title>Travel RAG - AI Travel Assistant</title>
        <meta name="description" content="AI-powered travel assistant to help plan your perfect trip" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="max-w-4xl mx-auto">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            Your AI Travel Planning Assistant
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Describe your travel preferences, and I'll create a personalized itinerary
          </p>
        </div>

        <ChatInterface />
      </div>
    </Layout>
  );
}