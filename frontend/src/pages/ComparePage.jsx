import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import SearchResultsHeader from '../components/compare/SearchResultsHeader';
import MatchSection from '../components/compare/MatchSection';

/**
 * MOCK DATA GENERATOR
 * This simulates the robust comparison output expected from the Python backend.
 */
const generateMockData = (query) => {
  const baseName = query.trim() ? (query.charAt(0).toUpperCase() + query.slice(1)) : "Unknown Product";
  
  return {
    high_confidence: [
      {
        id: 1,
        name: `${baseName} (Standard Edition) - Midnight Black`,
        image: "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        specs: { ram: "8GB", storage: "256GB", display: "6.1\" OLED" },
        stores: [
          { storeName: "Amazon", price: 65900, link: "#" },
          { storeName: "Flipkart", price: 66999, link: "#" }
        ]
      }
    ],
    spec_matches: [
      {
        id: 2,
        name: `${baseName} (Pro Edition) - Titanium`,
        image: "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        specs: { ram: "8GB", storage: "512GB", display: "6.1\" OLED", cpu: "Pro Core" },
        stores: [
          { storeName: "Amazon", price: 110900, link: "#" },
          { storeName: "Flipkart", price: 108000, link: "#" },
          { storeName: "Reliance Digital", price: 111500, link: "#" }
        ]
      }
    ],
    possible_matches: [
      {
        id: 3,
        name: `Previous Generation ${baseName}`,
        image: "https://m.media-amazon.com/images/I/61bK6PMOC8L._SX679_.jpg",
        specs: { ram: "6GB", storage: "128GB", display: "6.1\" OLED" },
        stores: [
          { storeName: "Amazon", price: 54999, link: "#" },
          { storeName: "Flipkart", price: 55499, link: "#" }
        ]
      }
    ]
  };
};

export default function ComparePage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Reset page view on fresh search
    window.scrollTo(0, 0);
    document.title = `Compare ${query} | PriceScout`;
    
    // Simulate API fetch delay bridging search execution
    setLoading(true);
    const timer = setTimeout(() => {
      setData(generateMockData(query));
      setLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div className="min-h-screen bg-slate-50/50 font-sans text-slate-900 antialiased flex flex-col">
      <Navbar forceDarkText={true} />
      
      <SearchResultsHeader query={query} />
      
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 opacity-70 animate-fade-in-up">
            <div className="w-16 h-16 border-[5px] border-slate-200 border-t-cyan-500 rounded-full animate-spin mb-6"></div>
            <h2 className="text-2xl font-black text-slate-400">Scanning verified stores...</h2>
            <p className="text-slate-400 font-medium mt-2 tracking-widest text-sm uppercase">Matching Specifications</p>
          </div>
        ) : data ? (
          <div className="space-y-16">
            <MatchSection 
              level={1}
              title="High Confidence Matches" 
              description="Exact model parity found. These are identical listings parsed from both verified stores and represent accurate direct comparisons."
              products={data.high_confidence}
            />
            
            <div className="border-t border-slate-200"></div>
            
            <MatchSection 
              level={2}
              title="Specification Matches" 
              description="These products belong to the identical family but differ in internal configurations such as storage or RAM."
              products={data.spec_matches}
            />
            
            <div className="border-t border-slate-200"></div>
            
            <MatchSection 
              level={3}
              title="Possible Matches & Alternatives" 
              description="Previous generation models or highly similar competitor items mapping to your query. Good for budget checking."
              products={data.possible_matches}
            />
          </div>
        ) : null}
      </main>
      
      <footer className="py-12 bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm font-medium flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-xl mb-4">P</div>
          <p>&copy; {new Date().getFullYear()} PriceScout. Assisting your market research.</p>
        </div>
      </footer>
    </div>
  );
}
