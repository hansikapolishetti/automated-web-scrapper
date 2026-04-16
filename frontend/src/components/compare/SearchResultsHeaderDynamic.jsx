import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { formatCountLabel } from '../../lib/productAdapters';

export default function SearchResultsHeaderDynamic({ query, total = 0, category = 'laptops' }) {
  const [localQuery, setLocalQuery] = useState(query || '');
  const navigate = useNavigate();

  useEffect(() => {
    setLocalQuery(query || '');
  }, [query]);

  const handleSearch = (event) => {
    event.preventDefault();
    if (localQuery.trim().length > 0) {
      navigate(`/compare?q=${encodeURIComponent(localQuery.trim())}&category=${encodeURIComponent(category)}`);
    }
  };

  return (
    <div className="bg-white border-b border-slate-200 pt-32 pb-12 relative z-10 animate-fade-in-up">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col lg:flex-row lg:items-center justify-between gap-8">
        <div>
          <p className="text-blue-600 font-bold text-sm tracking-widest uppercase mb-2">PriceScout Scanner</p>
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tight">
            Matches for <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">"{query}"</span>
          </h1>
          <p className="mt-3 text-sm font-medium text-slate-500">
            {formatCountLabel(total)} comparison-ready results from the database
          </p>
        </div>

        <form onSubmit={handleSearch} className="w-full lg:w-[450px] relative transition-all">
          <input
            type="text"
            className="w-full pl-6 pr-32 py-4 text-lg border-2 border-slate-100 rounded-full bg-slate-50 shadow-sm focus:border-blue-400 focus:ring-4 focus:ring-blue-100/50 outline-none transition-all placeholder-slate-400 text-slate-800 font-semibold"
            placeholder="Search another product..."
            value={localQuery}
            onChange={(event) => setLocalQuery(event.target.value)}
          />
          <button type="submit" className="absolute inset-y-2 right-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-6 rounded-full font-bold transition-all shadow-md active:scale-95">
            Search
          </button>
        </form>
      </div>
    </div>
  );
}
