import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import FilterSidebar from '../components/filters/FilterSidebar';
import ProductGrid from '../components/products/ProductGrid';
import { fetchSearch } from '../lib/api';

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || 'laptops';
  
  const [localQuery, setLocalQuery] = useState(query);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo(0, 0);
    setLocalQuery(query);
    
    async function loadResults() {
      if (!query) return;
      setLoading(true);
      try {
        const data = await fetchSearch(query, category);
        // Map comparison matches to grid items
        // We take the 'amazon' side as the primary display item for the grid
        const formatted = (data.all_comparable_matches || []).map(m => {
          const p = m.amazon || m.flipkart;
          return {
            title: p.name,
            slug: p.slug,
            price: `₹${p.price?.toLocaleString('en-IN')}`,
            oldPrice: p.original_price ? `₹${p.original_price.toLocaleString('en-IN')}` : null,
            rating: p.rating,
            image: p.image,
            store: p.website === 'amazon' ? 'Amazon' : 'Flipkart',
            tag: m.match_type === 'exact' ? 'Best Match' : m.confidence_label
          };
        });
        setProducts(formatted);
        setTotal(data.all_comparable_total || 0);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    }

    loadResults();
  }, [query, category]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (localQuery.trim().length > 0) {
      navigate(`/search?q=${encodeURIComponent(localQuery.trim())}&category=${category}`);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
      <Navbar forceDarkText={true} />
      
      <main className="pt-28 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mb-8 p-5 lg:p-6 bg-white rounded-2xl shadow-sm border border-slate-200">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              
              <div>
                <p className="text-sm font-bold text-blue-600 uppercase tracking-wider mb-1.5">Search Results</p>
                <h1 className="text-3xl font-black text-slate-900 tracking-tight leading-tight">
                  Results for <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-500">"{query}"</span>
                </h1>
                <p className="text-slate-500 text-sm mt-1.5">
                  {loading ? 'Searching marketplace...' : `Found ${total} verified matches`}
                </p>
              </div>
              
              <form onSubmit={handleSearch} className="relative w-full md:w-[400px] group flex-shrink-0">
                <input 
                  type="text" 
                  placeholder="Search another product..." 
                  value={localQuery}
                  onChange={(e) => setLocalQuery(e.target.value)}
                  className="w-full pl-12 pr-24 py-3.5 rounded-xl border-2 border-slate-100 bg-slate-50 focus:bg-white focus:ring-4 focus:ring-cyan-100/50 focus:border-cyan-400 outline-none transition-all font-semibold text-slate-700 placeholder-slate-400 shadow-inner group-hover:border-slate-200"
                />
                <svg className="w-5 h-5 text-slate-400 absolute left-4 top-4 group-hover:text-cyan-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <button type="submit" className="absolute right-2 top-2 bottom-2 bg-slate-900 hover:bg-blue-600 text-white px-5 rounded-lg font-bold transition-colors text-sm shadow-sm active:scale-95">
                  Search
                </button>
              </form>
              
            </div>
          </div>
          
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <div className="w-full lg:w-[280px] flex-shrink-0">
              <FilterSidebar />
            </div>
            
            {/* Product Grid Area */}
            <div className="flex-1">
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                  <div className="w-10 h-10 border-4 border-slate-200 border-t-cyan-500 rounded-full animate-spin"></div>
                  <p className="text-slate-400 font-medium text-sm animate-pulse">Scanning stores...</p>
                </div>
              ) : products.length > 0 ? (
                <ProductGrid products={products} />
              ) : (
                <div className="bg-white rounded-3xl p-12 text-center border border-dashed border-slate-300">
                  <h3 className="text-lg font-bold text-slate-800">No matches found</h3>
                  <p className="text-slate-500 mt-2">Try a different keyword or category.</p>
                </div>
              )}
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
