import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SearchBar() {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim().length > 0) {
      navigate('/compare?q=' + encodeURIComponent(query.trim()));
    }
  };

  return (
    <form onSubmit={handleSearch} className="w-full max-w-4xl mx-auto mt-4 relative group z-10 transition-all">
      <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
        <svg className="h-7 w-7 text-white/70 group-focus-within:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      
      <input
        type="text"
        className="block w-full pl-16 pr-44 py-6 text-xl border border-white/20 rounded-[2.5rem] bg-white/10 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.1)] focus:border-white/40 focus:ring-4 focus:ring-white/20 focus:bg-white/15 outline-none transition-all placeholder-white/70 text-white font-medium"
        placeholder="Search product model or paste link..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      
      <button 
        type="submit" 
        className="absolute inset-y-3 right-3 bg-white text-blue-700 hover:bg-slate-50 hover:text-blue-800 px-8 rounded-full font-bold text-lg transition-all shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] hover:-translate-y-0.5 active:scale-95 flex items-center cursor-pointer"
      >
        Search
      </button>
    </form>
  );
}
