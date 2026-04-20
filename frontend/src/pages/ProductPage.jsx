import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import RetailerLink from '../components/StorePriceList'; 
import { fetchCompareById } from '../lib/api';
import './ProductComparison.css';

// --- Sub-Components ---

const formatSpecValue = (key, value) => {
  if (!value) return 'N/A';
  if (['price', 'original_price'].includes(key)) {
    return `₹${Number(value).toLocaleString()}`;
  }
  return value;
};

const SpecBadgeV2 = ({ label, value }) => (
  <div className="flex items-center justify-between p-5 rounded-2xl bg-slate-50/80 border border-slate-100 hover:bg-white hover:shadow-sm transition-all">
    <span className="text-[11px] font-black text-slate-400 uppercase tracking-widest">{label}</span>
    <span className="text-sm font-black text-slate-900">{value || 'N/A'}</span>
  </div>
);

const ComparisonCardV2 = ({ match, isCheaper, index }) => {
  const { productId: anchorSlug } = useParams();
  
  const isMatch = !!match.amazon && !!match.flipkart;
  let displayProduct = match;
  let matchStoreKey = 'amazon'; 

  if (isMatch) {
    const amzSlug = match.amazon?.slug || '';
    const fkSlug = match.flipkart?.slug || '';
    const isAmzAnchor = amzSlug === anchorSlug;
    
    displayProduct = isAmzAnchor ? match.flipkart : match.amazon;
    matchStoreKey = isAmzAnchor ? 'flipkart' : 'amazon';
  }

  const filteredDifferences = useMemo(() => {
    if (!match.differences) return [];
    return Object.entries(match.differences)
      .filter(([key, diff]) => {
         if (['model_code', 'slug', 'id', 'rating', 'review_count', 'discount_percent'].includes(key)) return false;
         if (diff.status === 'unknown') return false;
         return true;
      })
      .map(([key, diff]) => {
        const isUpgrade = diff.status === 'different' && key !== 'price';
        return { key, value: diff[matchStoreKey], isUpgrade };
      });
  }, [match.differences, matchStoreKey]);

  return (
    <div 
      className={`premium-card relative group animate-entrance ${isCheaper ? 'best-deal-glow' : ''}`}
      style={{ animationDelay: `${index * 120}ms` }}
    >
      {isCheaper && (
        <div className="best-price-badge">Best Deal</div>
      )}
      
      <div className="aspect-square rounded-[20px] bg-slate-50 mb-4 flex items-center justify-center p-5 group-hover:bg-white transition-colors duration-500 overflow-hidden">
        <img 
          src={displayProduct.image} 
          alt={displayProduct.name} 
          className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-700"
        />
      </div>

      <div className="space-y-4">
        <div className="space-y-1">
          <h4 className="text-sm font-black text-slate-900 line-clamp-2 leading-tight">
            {displayProduct.name}
          </h4>
          <div className="flex items-center gap-2">
             <div className="h-1.5 w-1.5 rounded-full bg-emerald-500"></div>
             <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{displayProduct.website} verified</span>
          </div>
        </div>

        <div className="flex items-end justify-between py-2">
          <div className="flex flex-col">
            <span className="text-2xl font-black text-slate-900 tracking-tighter italic">
              {formatSpecValue('price', displayProduct.price)}
            </span>
            {isCheaper && match.price_difference > 0 && (
               <div className="savings-banner mt-1">
                 <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                 Save {formatSpecValue('price', match.price_difference)}
               </div>
            )}
          </div>
          <a 
            href={displayProduct.link} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="h-12 w-12 rounded-2xl bg-slate-900 text-white flex items-center justify-center hover:bg-indigo-600 hover:scale-110 transition-all shadow-xl shadow-slate-200"
          >
             <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
          </a>
        </div>

        {filteredDifferences.length > 0 && (
          <div className="pt-6 border-t border-slate-100 space-y-4">
             <div className="bold-spec-grid">
               {filteredDifferences.map(({ key, value, isUpgrade }) => (
                 <div key={key} className="bold-spec-item">
                    <span className="spec-label">{key.replace('_', ' ')}</span>
                    <span className="spec-value truncate" title={formatSpecValue(key, value)}>
                      {formatSpecValue(key, value)}
                    </span>
                    {isUpgrade && <span className="upgrade-tag">Upgrade</span>}
                 </div>
               ))}
             </div>
          </div>
        )}
      </div>
    </div>
  );
};

// --- Page Content ---

export default function ProductPage() {
  const { productId: slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('All');

  useEffect(() => {
    window.scrollTo(0, 0);
    async function loadData() {
      setLoading(true);
      try {
        const res = await fetchCompareById(slug);
        setData(res);
      } catch (err) {
        console.error('API Error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [slug]);

  const { product, exact_matches, variant_matches, spec_comparable_matches, fallback_matches } = data || {};

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

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  return (
    <div className="clean-bg min-h-screen flex flex-col font-sans antialiased overflow-hidden">
      <div className="bg-blob blob-indigo" />
      <div className="bg-blob blob-emerald" />
      
      <Navbar forceDarkText />

      <main className="relative z-10 flex-grow pt-24 pb-24 px-8">
        {product ? (
          <div className="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
            
            {/* LEFT: Anchor Sidebar - "Executive Command Center" */}
            <div className="lg:col-span-6 lg:sticky lg:top-28">
              <div className="sidebar-tint p-10 space-y-12 relative">
                <a 
                  href={product.stores?.[0]?.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex flex-col gap-6 relative z-10 group cursor-pointer block"
                >
                  <div className="max-h-[420px] aspect-square rounded-[32px] bg-white p-10 flex items-center justify-center border border-slate-50 shadow-sm overflow-hidden group-hover:border-indigo-100 transition-colors">
                    {product.images?.[0] ? (
                      <img 
                        src={product.images[0]} 
                        alt={product.title || 'Product'} 
                        className="max-w-full max-h-[400px] object-contain group-hover:scale-105 transition-transform duration-500" 
                      />
                    ) : (
                      <div className="flex flex-col items-center justify-center text-slate-300">
                         <svg className="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                         <span className="text-[10px] font-black uppercase mt-4">Preview Unavailable</span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="market-badge">
                         <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></div>
                         Verified Performance SKU
                      </div>
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{product.website || 'Official'} Source</span>
                    </div>

                    <div className="space-y-1">
                      <h1 className="text-xl font-black text-slate-900 leading-snug tracking-tight group-hover:text-indigo-600 transition-colors line-clamp-2">
                        {product.title || product.name || 'Unknown Device'}
                      </h1>
                      <p className="text-3xl font-black text-slate-900 tracking-tighter italic">
                        ₹{product.stores?.[0]?.price?.toLocaleString() || 'N/A'}
                      </p>
                    </div>

                    {/* Main Performance Grid (2 Columns to fill space) */}
                    <div className="grid grid-cols-2 gap-4 pt-4">
                       <SpecBadgeV2 label="RAM" value={product.specifications?.ram} />
                       <SpecBadgeV2 label="STORAGE" value={product.specifications?.storage} />
                       <SpecBadgeV2 label="CHIPSET" value={product.specifications?.processor || product.specifications?.cpu} />
                       <SpecBadgeV2 label="SCREEN" value={product.specifications?.display_size || product.specifications?.screen_size || 'N/A'} />
                    </div>
                  </div>
                </a>

                {/* Technical Specifications Section */}
                <div className="space-y-4 pt-8 border-t border-slate-100 relative z-10">
                   <h3 className="text-[10px] font-black text-slate-900 uppercase tracking-widest opacity-50">Hardware Identity</h3>
                   <div className="grid grid-cols-2 gap-2">
                      {[
                        { label: 'OS', value: product.specifications?.os || product.specifications?.operating_system || product.specifications?.['Operating System'] },
                        { label: 'GPU', value: product.specifications?.gpu || product.specifications?.graphics || product.specifications?.['Graphics'] },
                        { label: 'Series', value: product.specifications?.model_series || product.specifications?.series || product.specifications?.['Model Name'] },
                        { label: 'Weight', value: product.specifications?.weight || product.specifications?.item_weight || product.specifications?.['Weight'] },
                        { label: 'Speed', value: product.specifications?.clock_speed || product.specifications?.['Processor Speed'] }
                      ].filter(s => s.value && s.value !== 'Unknown').length > 0 ? (
                        [
                          { label: 'OS', value: product.specifications?.os || product.specifications?.operating_system || product.specifications?.['Operating System'] },
                          { label: 'GPU', value: product.specifications?.gpu || product.specifications?.graphics || product.specifications?.['Graphics'] },
                          { label: 'Series', value: product.specifications?.model_series || product.specifications?.series || product.specifications?.['Model Name'] },
                          { label: 'Weight', value: product.specifications?.weight || product.specifications?.item_weight || product.specifications?.['Weight'] },
                          { label: 'Speed', value: product.specifications?.clock_speed || product.specifications?.['Processor Speed'] }
                        ].filter(s => s.value && s.value !== 'Unknown').map((spec, i) => (
                          <div key={i} className="flex flex-col py-2 px-3 rounded-xl bg-slate-50/50">
                             <span className="text-[8px] font-bold text-slate-400 capitalize tracking-wider">{spec.label}</span>
                             <span className="text-[10px] font-black text-slate-800 truncate">{spec.value}</span>
                          </div>
                        ))
                      ) : (
                        <div className="col-span-2 text-[10px] text-slate-400 py-2 italic font-medium">Drafting technical profile...</div>
                      )}
                   </div>
                </div>

                {/* Compare Prices Section */}
                <div className="space-y-6 pt-10 border-t border-slate-100 relative z-10">
                  <h3 className="text-xs font-black text-slate-900 uppercase tracking-widest">Live Marketplace context</h3>
                  <div className="space-y-3">
                    {product.stores?.map((store, idx) => {
                      const logoUrl = store.logo?.startsWith('http') 
                        ? store.logo 
                        : store.logo?.startsWith('/') 
                          ? store.logo 
                          : `/${store.logo}`;
                      
                      return (
                        <div key={idx} className="flex items-center justify-between p-5 rounded-2xl bg-white border border-slate-100 shadow-sm">
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center p-1 border border-slate-100">
                              {store.logo ? (
                                <img 
                                  src={logoUrl} 
                                  alt={store.name} 
                                  className="w-full h-full object-contain" 
                                  onError={(e) => {
                                    e.target.onerror = null; 
                                    e.target.src=`https://ui-avatars.com/api/?name=${store.name}&background=f1f5f9&color=64748b&bold=true`;
                                  }}
                                />
                              ) : (
                                <span className="text-lg font-black text-slate-200">{store.name?.charAt(0)}</span>
                              )}
                            </div>
                            <span className="text-xs font-black">{store.name}</span>
                          </div>
                          <span className="text-sm font-black italic text-slate-900 font-mono tracking-tighter">₹{store.price?.toLocaleString()}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT: Comparison Engine */}
            <div className="lg:col-span-6 space-y-10">
              {filteredMatches.length > 0 || exact_matches?.length > 0 ? (
                <div className="space-y-12">
                  <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
                    <div className="space-y-2">
                      <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Market Counterparts</h2>
                      <p className="text-slate-500 font-medium text-base">Verified configurations from other major retailers</p>
                    </div>
                    <div className="tab-island-container">
                      {tabs.map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`tab-btn ${activeTab === tab.id ? 'tab-btn-active' : ''}`}
                        >
                          {tab.id} <span className="count-badge">{tab.count}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6 premium-scroll max-h-[1400px] overflow-y-auto pr-2 pb-20">
                    {filteredMatches.map((match, idx) => (
                      <ComparisonCardV2 
                        key={idx} 
                        index={idx}
                        match={match} 
                        isCheaper={match.cheaper_site !== 'same'}
                      />
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-12">
                   <div className="space-y-2">
                      <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Recommended Alternatives</h2>
                      <p className="text-slate-500 font-medium text-base">We found no exact matches. These are similar machines stacking vertically.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                      {fallback_matches?.map((m, idx) => (
                        <ComparisonCardV2 key={idx} index={idx} match={m} isFallback />
                      ))}
                    </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto py-32 text-center space-y-8">
             <h1 className="text-6xl font-black text-slate-900 tracking-tighter">Scanning...</h1>
             <p className="text-xl text-slate-500 font-medium">Looking for similarities for this specific SKU.</p>
          </div>
        )}
      </main>
    </div>
  );
}
