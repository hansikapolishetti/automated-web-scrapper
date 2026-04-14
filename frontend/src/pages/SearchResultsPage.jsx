import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import FilterSidebar from '../components/filters/FilterSidebar';
import ProductGrid from '../components/products/ProductGrid';

const MOCK_PRODUCTS = [
  {
    title: "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
    price: "₹26,990",
    oldPrice: "₹34,990",
    rating: 4.7,
    image: "https://m.media-amazon.com/images/I/51aXvjzcukL._SX522_.jpg",
    store: "Flipkart",
    tag: "Great Deal"
  },
  {
    title: "Samsung Galaxy S23 Ultra 5G (Phantom Black, 256GB)",
    price: "₹1,24,999",
    rating: 4.9,
    image: "https://m.media-amazon.com/images/I/61VfL-aiToL._SX679_.jpg",
    store: "Amazon",
    tag: "Above Average"
  },
  {
    title: "Dell XPS 13 (2023) Ultrabook i7 13th Gen",
    price: "₹1,10,500",
    oldPrice: "₹1,30,000",
    rating: 4.5,
    image: "https://m.media-amazon.com/images/I/61r1H+N8ZQL._SX679_.jpg",
    store: "Flipkart"
  },
  {
    title: "Logitech MX Master 3S Advanced Wireless Mouse",
    price: "₹8,995",
    rating: 4.8,
    image: "https://m.media-amazon.com/images/I/61ni3t1ryQL._SX679_.jpg",
    store: "Amazon",
    tag: "Lowest Ever"
  }
];

export default function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [localQuery, setLocalQuery] = useState(query);
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo(0, 0);
    setLocalQuery(query);
  }, [query]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (localQuery.trim().length > 0) {
      navigate('/search?q=' + encodeURIComponent(localQuery.trim()));
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
                  Showing {MOCK_PRODUCTS.length} products matching your query
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
              <ProductGrid products={MOCK_PRODUCTS} />
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
