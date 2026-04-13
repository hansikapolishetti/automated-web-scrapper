import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function CategoryCard({ title, priceRange, icon }) {
  const navigate = useNavigate();

  return (
    <div 
      onClick={() => navigate('/compare?q=' + encodeURIComponent(title))}
      className="group relative p-8 rounded-[2.5rem] transition-all duration-300 cursor-pointer overflow-hidden border border-slate-100 shadow-xl shadow-slate-200/50 bg-white hover:-translate-y-2 hover:shadow-[0_25px_60px_rgba(59,130,246,0.3)] hover:border-indigo-500"
    >
      {/* Background Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-0"></div>
      
      {/* Decorative large bg icon */}
      <div className="absolute top-0 right-0 p-6 opacity-[0.04] group-hover:opacity-10 group-hover:invert transform translate-x-1/4 -translate-y-1/4 group-hover:scale-110 transition-all duration-500 pointer-events-none z-0">
        <span className="text-9xl">{icon}</span>
      </div>
      
      {/* Card Content Layer */}
      <div className="flex flex-col h-full relative z-10">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl mb-6 shadow-inner transition-all duration-300 bg-slate-50 group-hover:scale-110 group-hover:bg-white/20 group-hover:text-white">
          {icon}
        </div>
        
        <h3 className="text-2xl font-extrabold tracking-tight mb-2 text-slate-900 transition-colors duration-300 group-hover:text-white">
          {title}
        </h3>
        
        <div className="self-start inline-block px-4 py-1.5 rounded-full text-sm font-bold mb-8 transition-colors duration-300 bg-slate-100 text-slate-600 group-hover:bg-white/20 group-hover:text-blue-50">
          {priceRange}
        </div>
        
        <div className="mt-auto pt-4 flex items-center gap-1 group-hover:gap-3 transition-all duration-300">
          <span className="font-bold text-sm text-blue-600 transition-colors duration-300 group-hover:text-white">
            Explore Category
          </span>
          <div className="w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 bg-blue-50 text-blue-600 group-hover:bg-white group-hover:text-indigo-600">
            <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
