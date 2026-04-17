import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import CategorySidebar from '../components/filters/CategorySidebar';
import ProductGrid from '../components/products/ProductGrid';
import { fetchProducts, fetchBrands } from '../lib/api';

const formatPrice = (price) => {
  if (!price) return "";
  if (typeof price === 'string' && price.includes('₹')) return price;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(price);
};

export default function CategoryProductsPage() {
  const { categoryName } = useParams();
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [selectedBrands, setSelectedBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    window.scrollTo(0, 0);
    
    async function loadData() {
      setLoading(true);
      try {
        const [prodData, brandData] = await Promise.all([
          fetchProducts({ category: categoryName, brands: selectedBrands, limit: 24 }),
          fetchBrands(categoryName)
        ]);
        
        const mappedProducts = (prodData.products || []).map(p => ({
          ...p,
          title: p.name,
          price: formatPrice(p.price),
          oldPrice: formatPrice(p.original_price),
          store: p.website ? p.website.charAt(0).toUpperCase() + p.website.slice(1) : 'Unknown'
        }));
        
        setProducts(mappedProducts);
        setBrands(brandData || []);
      } catch (err) {
        console.error("Failed to load category data:", err);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [categoryName, selectedBrands]);

  const handleBrandToggle = (brand) => {
    setSelectedBrands(prev => 
      prev.includes(brand) 
        ? prev.filter(b => b !== brand) 
        : [...prev, brand]
    );
  };

  const displayTitle = categoryName 
    ? categoryName.charAt(0).toUpperCase() + categoryName.slice(1).replace(/-/g, ' ') 
    : 'Category';

  const filteredProducts = products.filter(p => 
    p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.brand.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
      <Navbar forceDarkText={true} />
      
      <main className="pt-28 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 lg:p-5 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex flex-col lg:pl-2">
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">
                Browse {displayTitle}
              </h1>
              {!loading && (
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1">
                  {filteredProducts.length} Results {selectedBrands.length > 0 && `• ${selectedBrands.length} Brands Selected`}
                </p>
              )}
            </div>
            
            <div className="relative w-full md:w-96 group">
              <input 
                type="text" 
                placeholder={`Search ${displayTitle.toLowerCase()}...`}
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
              <CategorySidebar 
                brands={brands} 
                selectedBrands={selectedBrands}
                onBrandToggle={handleBrandToggle}
                loading={loading} 
              />
            </div>
            
            {/* Product Grid Area */}
            <div className="flex-1">
              {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {[1, 2, 3, 4, 5, 6].map(i => (
                    <div key={i} className="bg-white rounded-2xl border border-slate-100 p-6 h-80 animate-pulse">
                      <div className="bg-slate-50 w-full h-40 rounded-xl mb-4"></div>
                      <div className="h-4 bg-slate-50 rounded w-3/4 mb-2"></div>
                      <div className="h-4 bg-slate-50 rounded w-1/2"></div>
                    </div>
                  ))}
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
