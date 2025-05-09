/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    images: {
      domains: [
        'images.unsplash.com',
        'source.unsplash.com',
        'localhost'
      ],
    },
    env: {
      // Backend API URL
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
      
      // Use mock data for development
      NEXT_PUBLIC_USE_MOCKS: process.env.NEXT_PUBLIC_USE_MOCKS || 'true',
      
      // App environment
      NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
    },
    async redirects() {
      return [
        {
          source: '/dashboard',
          destination: '/dashboard',
          permanent: true,
        },
      ];
    },
  };
  
  module.exports = nextConfig;