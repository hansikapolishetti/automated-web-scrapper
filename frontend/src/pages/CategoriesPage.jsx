import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import CategorySidebar from '../components/filters/CategorySidebar';
import ProductGrid from '../components/products/ProductGrid';

const MOCK_PRODUCTS = [
  {
    title: "Apple MacBook Air M2 (2022) - Starlight",
    price: "₹99,900",
    oldPrice: "₹1,14,900",
    rating: 4.8,
    image: "https://m.media-amazon.com/images/I/71vFKBpKakL._SX679_.jpg",
    store: "Amazon",
    tag: "Lowest Ever"
  },
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
  },
  {
    title: "Apple iPhone 15 Pro (128 GB) - Natural Titanium",
    price: "₹1,34,900",
    rating: 4.8,
    image: "https://m.media-amazon.com/images/I/81+GIkwqLIL._SX679_.jpg",
    store: "Flipkart"
  }
];

export default function CategoriesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  
  useEffect(() => {
    // Scroll to top when page mounts
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
      <Navbar forceDarkText={true} />
      
      <main className="pt-28 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 lg:p-5 rounded-2xl shadow-sm border border-slate-200">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight lg:pl-2">Marketplace Deals</h1>
            
            <div className="relative w-full md:w-96 group">
              <input 
                type="text" 
                placeholder="Search products..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-xl border-2 border-slate-100 bg-slate-50 focus:bg-white focus:ring-4 focus:ring-blue-100/50 focus:border-blue-400 outline-none transition-all font-semibold text-slate-700 placeholder-slate-400 shadow-inner group-hover:border-slate-200"
              />
              <svg className="w-5 h-5 text-slate-400 absolute left-4 top-3.5 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <div className="w-full lg:w-[280px] flex-shrink-0">
              <CategorySidebar />
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
