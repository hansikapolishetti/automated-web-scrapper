import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import RetailerLink from '../components/StorePriceList'; 
import { fetchCompareById } from '../lib/api';
import './ProductComparison.css';

// --- Sub-Components ---

const SpecBadge = ({ label, value }) => (
  <div className="flex flex-col p-3 rounded-xl bg-white/50 border border-slate-100 hover:border-blue-200 transition-colors">
    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">{label}</span>
    <span className="text-sm font-bold text-slate-800 truncate">{value || 'N/A'}</span>
  </div>
);

const ComparisonCard = ({ match, isCheaper, isFallback }) => {
  const { productId: anchorSlug } = useParams();
  
  const isMatch = !!match.amazon && !!match.flipkart;
  
  let displayProduct = match;
  if (isMatch) {
    const amzSlug = match.amazon?.slug || '';
    const fkSlug = match.flipkart?.slug || '';
    
    // Display the counterpart. Default to flipkart, unless flipkart IS the anchor
    displayProduct = match.flipkart;
    if (fkSlug === anchorSlug && amzSlug !== anchorSlug) {
      displayProduct = match.amazon;
    }
  }

  return (
    <div className={`glass-card rounded-2xl p-4 relative group animate-fade-in`}>
      {isCheaper && (
        <div className="cheaper-overlay">
          Best Price
        </div>
      )}
      
      <div className="aspect-square rounded-xl bg-slate-50 mb-4 overflow-hidden flex items-center justify-center p-4">
        <img 
          src={displayProduct.image} 
          alt={displayProduct.name} 
          className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-500"
        />
      </div>

      <div className="space-y-3">
        <h4 className="text-sm font-bold text-slate-800 line-clamp-2 min-h-[40px]">
          {displayProduct.name}
        </h4>

        <div className="flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-lg font-black text-slate-900">₹{displayProduct.price?.toLocaleString()}</span>
            {!isFallback && isMatch && match.price_difference > 0 && (
               <span className="text-[10px] font-bold text-emerald-600">
                 Save ₹{match.price_difference.toLocaleString()}
               </span>
            )}
          </div>
          <a 
            href={displayProduct.link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="px-4 py-2 bg-slate-900 text-white text-xs font-bold rounded-lg hover:bg-blue-600 transition-colors shadow-lg shadow-slate-200"
          >
            Visit Store
          </a>
        </div>

        {!isFallback && isMatch && match.differences && (
          <div className="pt-3 border-t border-slate-100 space-y-1.5 mt-2">
            {Object.entries(match.differences).slice(0, 3).map(([key, diff]) => (
              <div key={key} className="spec-diff-item">
                <span className="text-[10px] font-medium text-slate-400 capitalize">{key}</span>
                <span className={`text-[10px] font-bold ${diff.status === 'different' ? 'text-blue-600' : 'text-slate-600'}`}>
                  {diff.flipkart || diff.amazon}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// --- Main Page Component ---

export default function ProductPage() {
  const { productId: slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('All');

  useEffect(() => {
    window.scrollTo(0, 0);
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetchCompareById(slug);
        setData(res);
      } catch (err) {
        console.error('API Error:', err);
        setError('Something went wrong. Please try again.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [slug]);

  const { product, exact_matches, variant_matches, spec_comparable_matches, fallback_matches } = data || {};

  const hasComparison = useMemo(() => {
    return (exact_matches?.length > 0 || variant_matches?.length > 0 || spec_comparable_matches?.length > 0);
  }, [exact_matches, variant_matches, spec_comparable_matches]);

  const hasFallback = useMemo(() => fallback_matches?.length > 0, [fallback_matches]);
  const productNotFound = !product;

  const tabs = [
    { id: 'All', count: (exact_matches?.length || 0) + (variant_matches?.length || 0) + (spec_comparable_matches?.length || 0) },
    { id: 'Exact Match', count: exact_matches?.length || 0, data: exact_matches },
    { id: 'Variants', count: variant_matches?.length || 0, data: variant_matches },
    { id: 'Similar', count: spec_comparable_matches?.length || 0, data: spec_comparable_matches },
  ];

  const filteredMatches = useMemo(() => {
    if (activeTab === 'All') return [...(exact_matches || []), ...(variant_matches || []), ...(spec_comparable_matches || [])];
    return tabs.find(t => t.id === activeTab)?.data || [];
  }, [activeTab, exact_matches, variant_matches, spec_comparable_matches]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-50">
        <Navbar forceDarkText />
        <div className="flex-grow flex flex-col items-center justify-center">
          <div className="w-16 h-16 border-4 border-slate-900 border-t-transparent rounded-full animate-spin"></div>
          <p className="mt-4 text-slate-500 font-bold animate-pulse">Analyzing matches...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-50">
        <Navbar forceDarkText />
        <div className="flex-grow flex flex-col items-center justify-center text-center p-6">
          <div className="w-20 h-20 bg-red-50 text-red-500 rounded-full flex items-center justify-center mb-6 text-3xl">!</div>
          <h2 className="text-2xl font-black text-slate-900 mb-2">Oops!</h2>
          <p className="text-slate-600 font-medium mb-8">{error}</p>
          <button onClick={() => window.location.reload()} className="px-8 py-4 bg-slate-900 text-white rounded-2xl font-bold shadow-xl shadow-slate-200 hover:-translate-y-1 transition-all">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans antialiased text-slate-900">
      <Navbar forceDarkText />

      <main className={`flex-grow pt-24 pb-20 ${productNotFound ? 'max-w-7xl mx-auto px-6' : ''}`}>
        {!productNotFound ? (
          /* Case 1 & 2: Dual Panel Layout */
          <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* LEFT PANEL: Product Specs */}
            <div className="lg:col-span-4 lg:sticky lg:top-24 space-y-6">
              <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
                <div className="aspect-square rounded-2xl bg-slate-50 mb-6 p-4 flex items-center justify-center">
                  <img src={product.images?.[0]} alt={product.title} className="max-w-full max-h-full object-contain" />
                </div>
                
                <div className="space-y-4">
                  <h1 className="text-xl font-black text-slate-900 leading-tight">
                    {product.title}
                  </h1>
                  
                  <div className="flex items-center gap-3">
                    <span className="text-3xl font-black text-slate-900">₹{product.stores?.[0]?.price?.toLocaleString()}</span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
                    <SpecBadge label="RAM" value={product.specifications?.ram} />
                    <SpecBadge label="Storage" value={product.specifications?.storage} />
                    <SpecBadge label="Processor" value={product.specifications?.processor} />
                    <SpecBadge label="Display" value={product.specifications?.screen_size || product.specifications?.display_size} />
                  </div>

                  <div className="space-y-3 pt-6 border-t border-slate-100">
                    <p className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest">Available At</p>
                    <div className="flex flex-col gap-2">
                      {product.stores?.map((store, idx) => (
                        <a 
                          key={idx}
                          href={store.link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center justify-between p-3 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <span className="w-8 h-8 rounded-lg bg-white p-1.5 shadow-sm">
                              <img src={store.logo} alt={store.name} className="w-full h-full object-contain" />
                            </span>
                            <span className="text-xs font-bold">{store.name}</span>
                          </div>
                          <span className="text-sm font-black italic">₹{store.price?.toLocaleString()}</span>
                        </a>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT PANEL: Dynamic Content */}
            <div className="lg:col-span-8 space-y-8">
              {hasComparison ? (
                /* CASE 1: Comparison State */
                <div className="space-y-6">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <h2 className="text-2xl font-black text-slate-900 tracking-tight">Compare Similar Products</h2>
                      <p className="text-sm text-slate-500 font-medium">Best alternatives across all Indian stores</p>
                    </div>
                    <div className="inline-flex p-1.5 bg-white border border-slate-100 rounded-2xl shadow-sm">
                      {tabs.map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-300 ${
                            activeTab === tab.id 
                              ? 'bg-slate-900 text-white shadow-lg' 
                              : 'text-slate-500 hover:text-slate-900'
                          }`}
                        >
                          {tab.id} {tab.count > 0 && <span className="ml-1 opacity-60 italic">{tab.count}</span>}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 premium-scroll max-h-[1200px] overflow-y-auto pr-2 pb-8">
                    {filteredMatches.map((match, idx) => (
                      <ComparisonCard 
                        key={idx} 
                        match={match} 
                        isCheaper={match.cheaper_site === 'flipkart' || match.cheaper_site === 'amazon'}
                      />
                    ))}
                  </div>
                </div>
              ) : hasFallback ? (
                /* CASE 2: Fallback State */
                <div className="space-y-6">
                   <div className="space-y-1">
                      <h2 className="text-2xl font-black text-slate-900 tracking-tight">Recommended Alternatives</h2>
                      <p className="text-sm text-slate-500 font-medium font-semibold italic">We couldn't find an exact match. Here are similar options.</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {fallback_matches.slice(0, 5).map((m, idx) => (
                        <ComparisonCard key={idx} match={m} isFallback />
                      ))}
                    </div>
                </div>
              ) : (
                /* Safety Case: Just in case nothing is found but it didn't trigger productNotFound */
                <div className="h-64 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-3xl">
                  <p className="text-slate-400 font-bold">No alternatives found.</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* CASE 3: PRODUCT NOT FOUND (Full-width) */
          <div className="space-y-12 py-10">
            <div className="text-center space-y-3 max-w-2xl mx-auto">
              <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mx-auto text-2xl font-black mb-4">?</div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tighter">Recommended Alternatives</h1>
              <p className="text-lg text-slate-500 font-medium">Product not found. Showing similar products from our database.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
              {fallback_matches?.map((m, idx) => (
                <ComparisonCard key={idx} match={m} isFallback />
              ))}
            </div>

            <div className="flex justify-center pt-8">
               <Link to="/" className="px-10 py-4 bg-slate-900 text-white rounded-2xl font-black hover:-translate-y-1 transition-all shadow-2xl shadow-slate-200">
                  Browse All Categories
               </Link>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
