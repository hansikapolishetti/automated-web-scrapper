import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import CategorySidebar from '../components/filters/CategorySidebar';
import ProductGrid from '../components/products/ProductGrid';
import { fetchProducts } from '../lib/api';

export default function CategoriesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    window.scrollTo(0, 0);
    
    async function loadProducts() {
      setLoading(true);
      try {
        // Fetch all products across categories for the marketplace view
        const data = await fetchProducts({ limit: 48 });
        // Map backend products to frontend ProductCard format
        const formatted = (data.products || []).map(p => ({
          title: p.name,
          slug: p.slug,
          price: `₹${p.price?.toLocaleString('en-IN')}`,
          oldPrice: p.original_price ? `₹${p.original_price.toLocaleString('en-IN')}` : null,
          rating: p.rating,
          image: p.image,
          store: p.brand, // Using brand as store for variety in mock-replacement
          tag: p.price < 50000 ? "Great Deal" : null
        }));
        setProducts(formatted);
      } catch (err) {
        console.error('Failed to load marketplace products:', err);
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
  }, []);

  const filteredProducts = products.filter(p => 
    p.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
              {loading ? (
                <div className="flex justify-center py-20">
                  <div className="w-10 h-10 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
                </div>
              ) : (
                <ProductGrid products={filteredProducts} />
              )}
            </div>
          </div>
          
        </div>
      </main>
    </div>
  );
}
