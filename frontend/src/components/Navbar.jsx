import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Navbar({ forceDarkText = false }) {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const bgClass = forceDarkText
    ? 'bg-white border-b border-gray-200 py-3'
    : isScrolled
      ? 'bg-white/95 backdrop-blur-lg shadow-[0_4px_30px_rgba(0,0,0,0.06)] border-b border-gray-200 py-3'
      : 'bg-transparent py-5';

  const textClass      = (isScrolled || forceDarkText) ? 'text-slate-900' : 'text-white';
  const linkHoverClass = (isScrolled || forceDarkText) ? 'text-gray-700 font-semibold hover:text-indigo-600 transition-colors' : 'text-white/90 font-bold hover:text-cyan-400 transition-colors drop-shadow-sm';
  
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${bgClass}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3 cursor-pointer group">
            <Link to="/" className={`w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center text-white font-black text-2xl shadow-lg transition-transform duration-300 hover:scale-105 hover:-rotate-3`}>P</Link>
            <Link to="/" className={`font-extrabold text-2xl tracking-tighter ${textClass} transition-colors duration-300 drop-shadow-sm`}>PriceScout</Link>
          </div>
          
          <div className="hidden md:flex items-center space-x-10">
            <Link to="/" className={`font-bold transition-colors drop-shadow-sm ${linkHoverClass}`}>Home</Link>
            <Link to="/categories" className={`font-bold transition-colors drop-shadow-sm ${linkHoverClass}`}>Categories</Link>
          </div>
          
          <div className="flex items-center gap-6">
            <Link
              to="/login"
              className={`font-semibold transition-colors ${
                (isScrolled || forceDarkText)
                  ? 'text-gray-700 hover:text-indigo-600'
                  : 'text-white/90 hover:text-cyan-400'
              }`}
            >
              Login
            </Link>
            <button className={`md:hidden focus:outline-none p-2 hover:opacity-80 transition-opacity ${(isScrolled || forceDarkText) ? 'text-slate-700' : 'text-white'}`} aria-label="Open menu">
              <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
