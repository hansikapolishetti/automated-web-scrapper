import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function CategoryCard({ categoryId, title, description, icon, image, gradient }) {
  const navigate = useNavigate();

  return (
    <div 
      onClick={() => navigate(`/category/${categoryId || encodeURIComponent(title.toLowerCase())}`)}
      className={`group flex flex-col rounded-[1.5rem] p-6 border border-white/80 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer relative overflow-hidden bg-gradient-to-br ${gradient}`}
    >
      {/* Product Image - top area */}
      <div className="relative w-full h-40 mb-6 rounded-xl overflow-hidden shadow-sm bg-white/60">
        <img 
          src={image} 
          alt={title} 
          onError={(e) => { e.target.src = "/images/categories/placeholder.jpg"; }}
          className="w-full h-full object-cover transform scale-100 group-hover:scale-110 transition-transform duration-500 ease-in-out"
        />
        {/* Overlay gradient to fade bottom */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/30 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        {/* Floating icon */}
        <div className="absolute top-3 right-3 w-10 h-10 bg-white/90 backdrop-blur-md rounded-xl flex items-center justify-center text-xl shadow-sm border border-white/50 transform group-hover:scale-110 group-hover:-rotate-6 transition-all duration-300">
          {icon}
        </div>
      </div>
      
      {/* Title & Badge */}
      <div className="flex flex-col mb-1 z-10">
        <h3 className="text-lg font-bold tracking-tight text-gray-900 group-hover:text-slate-950 transition-colors mb-2">
          {title}
        </h3>
        
        {/* Product Count Badge */}
        <div className="self-start">
          <span className="inline-block px-2.5 py-1 bg-white shadow-sm ring-1 ring-black/5 rounded-full text-[10px] sm:text-[11px] font-bold text-gray-700 group-hover:text-indigo-600 transition-all duration-300">
            {description} Products
          </span>
        </div>
      </div>
      
      {/* Explore Arrow Line */}
      <div className="flex items-center gap-2 text-gray-800 text-xs sm:text-sm font-bold mt-3 pt-3 border-t border-black/10 z-10 flex-grow-0">
        <span className="group-hover:text-indigo-700 transition-colors">Explore</span>
        <div className="w-8 h-8 rounded-full flex items-center justify-center bg-white shadow-sm ml-auto group-hover:bg-indigo-600 group-hover:text-white transition-all duration-300">
          <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </div>
      </div>
    </div>
  );
}
