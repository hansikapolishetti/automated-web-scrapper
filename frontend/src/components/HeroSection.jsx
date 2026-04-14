import React from 'react';
import SearchBar from './SearchBar';

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center pt-24 pb-16 overflow-hidden bg-gradient-to-br from-blue-700 via-purple-700 to-cyan-500">
      
      {/* Minimal Background Noise for texture without clutter */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20 mix-blend-overlay pointer-events-none"></div>
      
      {/* Background Soft Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[800px] h-[800px] bg-blue-500/20 rounded-full blur-[140px] pointer-events-none mix-blend-screen"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-cyan-400/20 rounded-full blur-[120px] pointer-events-none mix-blend-screen"></div>
      
      <div className="relative w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10 flex-1 flex flex-col justify-center">
        
        <h1 className="opacity-0 animate-fade-in-up md:text-[5.5rem] text-6xl font-black text-white tracking-tight leading-[1.1] drop-shadow-2xl max-w-5xl mx-auto">
          Find the Best Deals <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-blue-200 to-indigo-200 relative">
            Across the Web
          </span>
        </h1>
        
        <p className="opacity-0 animate-fade-in-up-delay-1 mt-8 max-w-4xl text-[1.35rem] leading-relaxed text-blue-50/90 mx-auto font-medium drop-shadow-md">
          Stop overpaying. We match products across top Indian stores to highlight the absolute best prices, real-time deal signals, and hidden variant differences.
        </p>
        
        <div className="opacity-0 animate-fade-in-up-delay-2 mt-12 mb-8">
          <SearchBar />
        </div>
        
      </div>
    </section>
  );
}
