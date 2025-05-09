// src/components/layout/Layout.jsx
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

// Use simple emoji icons instead of Heroicons to avoid compatibility issues
export default function Layout({ children }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const router = useRouter();
  
  // Function to check if a route is active
  const isActive = (path) => {
    return router.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/" className="text-xl font-bold text-[#00aa6c]">
                  TravelRAG
                </Link>
              </div>
              <nav className="hidden md:ml-6 md:flex space-x-8">
                <Link 
                  href="/" 
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                    isActive('/') 
                      ? 'border-[#00aa6c] text-[#00aa6c]' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } text-sm font-medium`}
                >
                  Home
                </Link>
                <Link 
                  href="/destinations" 
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                    isActive('/destinations') 
                      ? 'border-[#00aa6c] text-[#00aa6c]' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } text-sm font-medium`}
                >
                  Destinations
                </Link>
                <Link 
                  href="/dashboard" 
                  className={`inline-flex items-center px-1 pt-1 border-b-2 ${
                    isActive('/dashboard') 
                      ? 'border-[#00aa6c] text-[#00aa6c]' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } text-sm font-medium`}
                >
                  Dashboard
                </Link>
              </nav>
            </div>
            
            {/* Search and menu buttons */}
            <div className="flex items-center">
              <button className="p-1 rounded-full text-gray-400 hover:text-gray-500">
                🔍
              </button>
              
              <button 
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="ml-4 md:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {isMenuOpen ? '✕' : '☰'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="pt-2 pb-3 space-y-1">
            <Link 
              href="/" 
              className={`block pl-3 pr-4 py-2 border-l-4 ${
                isActive('/') 
                  ? 'border-[#00aa6c] text-[#00aa6c] bg-[#00aa6c]/10' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              } text-base font-medium`}
            >
              Home
            </Link>
            <Link 
              href="/destinations" 
              className={`block pl-3 pr-4 py-2 border-l-4 ${
                isActive('/destinations') 
                  ? 'border-[#00aa6c] text-[#00aa6c] bg-[#00aa6c]/10' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              } text-base font-medium`}
            >
              Destinations
            </Link>
            <Link 
              href="/dashboard" 
              className={`block pl-3 pr-4 py-2 border-l-4 ${
                isActive('/dashboard') 
                  ? 'border-[#00aa6c] text-[#00aa6c] bg-[#00aa6c]/10' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              } text-base font-medium`}
            >
              Dashboard
            </Link>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>

      <footer className="bg-gray-800 text-white py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>&copy; {new Date().getFullYear()} TravelRAG. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}