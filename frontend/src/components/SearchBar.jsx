import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchSearchSuggestions, fetchSearchByLink } from '../lib/api';

// Helper to highlight matching text
const HighlightText = ({ text, highlight }) => {
  if (!highlight || !highlight.trim()) return <span>{text}</span>;
  const escapeRegExp = (string) => string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapeRegExp(highlight.trim())})`, 'gi');
  const parts = text.split(regex);
  
  return (
    <span>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <span key={i} className="text-indigo-600 font-bold">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  );
};

export default function SearchBar() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [processedSuggestions, setProcessedSuggestions] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [linkState, setLinkState] = useState(null);

  const containerRef = useRef(null);
  const navigate = useNavigate();

  const isProductUrl = (str) =>
    /^https?:\/\/(www\.)?(amazon\.in|amazon\.com|flipkart\.com)\//.test(str.trim());

  useEffect(() => {
    setLinkState(null);
    if (isProductUrl(query)) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    if (query.trim().length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    const handler = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await fetchSearchSuggestions(query.trim());
        setSuggestions(results || []);
        
        // Process tags and mock ratings
        if (results && results.length > 0) {
          const validResults = results.slice(0, 8); // Max 8 items
          
          // Find lowest price for "Best Deal"
          const prices = validResults.map(r => r.price).filter(p => typeof p === 'number' && !isNaN(p));
          const minPrice = prices.length > 0 ? Math.min(...prices) : null;
          
          const tagged = validResults.map((item, index) => {
            let tag = null;
            let tagColor = '';
            
            // Generate a fake rating based on string length to make it deterministic but varied
            const nameLen = item.name ? item.name.length : 10;
            const fakeRating = (4.0 + ((nameLen % 10) / 10)).toFixed(1);
            const reviews = 100 + (nameLen * 13 % 900);
            
            if (minPrice !== null && item.price === minPrice) {
              tag = 'Best Deal';
              tagColor = 'bg-green-100 text-green-700 border-green-200';
            } else if (index === 0) {
              tag = 'Highly Relevant';
              tagColor = 'bg-indigo-100 text-indigo-700 border-indigo-200';
            } else if (parseFloat(fakeRating) >= 4.7) {
              tag = 'Popular';
              tagColor = 'bg-orange-100 text-orange-700 border-orange-200';
            } else if (minPrice !== null && item.price <= minPrice * 1.1) {
               tag = 'Budget';
               tagColor = 'bg-blue-100 text-blue-700 border-blue-200';
            }

            return { ...item, tag, tagColor, fakeRating, reviews };
          });
          
          setProcessedSuggestions(tagged);
        } else {
          setProcessedSuggestions([]);
        }
        
        setShowSuggestions(true);
        setSelectedIndex(-1);
      } catch (err) {
        console.error('Suggestion fetch failed:', err);
      } finally {
        setIsLoading(false);
      }
    }, 300);
    return () => clearTimeout(handler);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = async (e, overrideQuery) => {
    if (e) e.preventDefault();
    const q = (overrideQuery ?? query).trim();
    if (!q) return;
    setShowSuggestions(false);
    if (isProductUrl(q)) {
      setLinkState('searching');
      try {
        const result = await fetchSearchByLink(q);
        if (result?.found && result?.slug) {
          navigate(`/product/${result.slug}`);
        } else {
          setLinkState('not_found');
        }
      } catch {
        setLinkState('not_found');
      }
      return;
    }
    navigate('/search?q=' + encodeURIComponent(q));
  };

  const handleSuggestionClick = (item) => {
    setShowSuggestions(false);
    navigate(`/product/${item.slug}`);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => (prev < processedSuggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => (prev > -1 ? prev - 1 : -1));
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && showSuggestions) {
        e.preventDefault();
        handleSuggestionClick(processedSuggestions[selectedIndex]);
      } else {
        handleSearch();
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  return (
    <div ref={containerRef} className="w-full max-w-4xl mx-auto mt-4 relative group z-[100] transition-all">
      <form onSubmit={(e) => handleSearch(e)} className="relative">
        <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
          <svg className="h-7 w-7 text-white/70 group-focus-within:text-white transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <input
          type="text"
          className="block w-full pl-16 pr-44 py-6 text-xl border border-white/20 rounded-[2.5rem] bg-white/10 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.1)] focus:border-white/40 focus:ring-4 focus:ring-white/20 focus:bg-white/15 outline-none transition-all placeholder-white/70 text-white font-medium"
          placeholder="Search product or paste Amazon/Flipkart link..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => query.length >= 2 && !isProductUrl(query) && setShowSuggestions(true)}
        />
        
        <button 
          type="submit"
          disabled={linkState === 'searching'}
          className="absolute inset-y-3 right-3 bg-white text-blue-700 hover:bg-slate-50 hover:text-blue-800 px-8 rounded-full font-bold text-lg transition-all shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] hover:-translate-y-0.5 active:scale-95 flex items-center cursor-pointer disabled:opacity-60 disabled:cursor-wait"
        >
          {linkState === 'searching' ? (
           <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin inline-block"></span>
              Finding...
            </span>
          ) : (
            isProductUrl(query) ? 'Find Product' : 'Search'
          )}
        </button>
      </form>

      {/* URL not-found feedback */}
      {linkState === 'not_found' && (
        <div className="mt-3 px-5 py-3 bg-red-500/20 border border-red-400/40 rounded-2xl text-white/90 text-sm font-semibold flex items-center gap-2 backdrop-blur-sm">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          This product isn't in our database yet. Try searching by name instead.
        </div>
      )}

      {/* URL detected hint */}
      {isProductUrl(query) && !linkState && (
        <div className="mt-3 px-5 py-2.5 bg-white/10 border border-white/20 rounded-2xl text-white/80 text-sm font-medium flex items-center gap-2 backdrop-blur-sm">
          <svg className="w-4 h-4 flex-shrink-0 text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
          </svg>
          Product link detected — click <strong className="text-white">Find Product</strong> to look it up
        </div>
      )}

      {/* Intelligent Suggestions Dropdown */}
      {showSuggestions && (processedSuggestions.length > 0 || isLoading) && (
        <div
          className="absolute top-full left-0 right-0 mt-3 bg-white rounded-[16px] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.15)] border border-slate-200/60 overflow-hidden backdrop-blur-xl"
          style={{ animation: 'suggestionFadeIn 0.2s ease-out' }}
        >
          {/* Header section */}
          <div className="bg-slate-50/80 px-4 py-2.5 border-b border-slate-100/80 flex items-center justify-between">
             <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Top Matches</span>
             <span className="text-xs font-medium text-slate-400">Press Enter to select</span>
          </div>

          {isLoading && processedSuggestions.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-3 py-10 text-slate-400">
              <div className="w-6 h-6 border-2 border-slate-200 border-t-indigo-500 rounded-full animate-spin"></div>
              <span className="text-sm font-medium">Finding best deals…</span>
            </div>
          ) : (
            <div className="suggestions-scroll" style={{ maxHeight: '340px', overflowY: 'auto' }}>
              {processedSuggestions.map((item, index) => {
                const isAmazon = item.website === 'amazon';
                const isSelected = selectedIndex === index;
                const storeName = isAmazon ? 'Amazon' : 'Flipkart';
                
                return (
                  <div
                    key={item.slug + index}
                    onClick={() => handleSuggestionClick(item)}
                    onMouseEnter={() => setSelectedIndex(index)}
                    className={`flex items-center gap-4 px-4 py-3 cursor-pointer transition-all duration-150 border-l-4 ${
                      isSelected ? 'bg-indigo-50/50 border-indigo-500' : 'bg-white border-transparent hover:bg-slate-50'
                    } ${index !== processedSuggestions.length - 1 ? 'border-b border-slate-50' : ''}`}
                  >
                    {/* Image Thumbnail */}
                    <div className="w-12 h-12 rounded-lg bg-white border border-slate-100 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-sm p-1">
                      <img
                        src={item.image}
                        alt=""
                        className="w-full h-full object-contain mix-blend-multiply"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0 py-0.5 flex flex-col justify-between">
                      {/* Top row: Title and Price */}
                      <div className="flex items-start justify-between gap-3">
                         <h4 className={`text-[14px] font-semibold truncate leading-snug ${isSelected ? 'text-indigo-950' : 'text-slate-800'}`}>
                           <HighlightText text={item.name || ''} highlight={query} />
                         </h4>
                         <span className="text-[15px] font-bold text-indigo-700 flex-shrink-0">
                           ₹{item.price?.toLocaleString('en-IN')}
                         </span>
                      </div>
                      
                      {/* Bottom row: Store, Rating, Tags */}
                      <div className="flex items-center gap-3 mt-1 text-[12px]">
                         {/* Store Logo/Name */}
                         <div className="flex items-center gap-1.5 font-medium">
                           <span className={isAmazon ? 'text-orange-600' : 'text-blue-600'}>{storeName}</span>
                         </div>
                         
                         <span className="w-1 h-1 rounded-full bg-slate-200"></span>
                         
                         {/* Optional Rating */}
                         <div className="flex items-center gap-1 text-slate-500 font-medium">
                            <svg className="w-3.5 h-3.5 text-yellow-400 pb-[1px]" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            {item.fakeRating} <span className="text-slate-400">({item.reviews})</span>
                         </div>
                         
                         {/* Dynamic Tag */}
                         {item.tag && (
                           <>
                             <span className="w-1 h-1 rounded-full bg-slate-200 hidden sm:block"></span>
                             <span className={`hidden sm:inline-flex px-1.5 py-0.5 rounded border text-[10px] font-bold tracking-wide uppercase ${item.tagColor}`}>
                               {item.tag}
                             </span>
                           </>
                         )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer Action */}
          {processedSuggestions.length > 0 && (
            <button
              type="button"
              onClick={(e) => handleSearch(e)}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-slate-50 hover:bg-slate-100 text-sm text-indigo-600 font-bold transition-colors border-t border-slate-100"
            >
              See all results for "{query}"
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
