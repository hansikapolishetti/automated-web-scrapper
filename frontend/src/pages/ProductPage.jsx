import React, { useEffect, useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import RetailerLink from '../components/StorePriceList'; 
import { fetchCompareById } from '../lib/api';
import LeftProductCard from '../components/compare/LeftProductCard';
import RightComparisonCard from '../components/compare/RightComparisonCard';
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

const ExpandableSection = ({ title, description, children, count }) => {
  const [expanded, setExpanded] = useState(false);
  const items = React.Children.toArray(children);
  const maxInitial = 3;
  const isExpandable = items.length > maxInitial;
  const displayItems = expanded ? items : items.slice(0, maxInitial);

  if (items.length === 0) return null;

  return (
    <div className="mb-12">
      <div className="mb-6 space-y-1">
        <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-3">
          {title} 
          <span className="flex items-center justify-center bg-slate-100 text-slate-500 text-[10px] font-black rounded-full h-5 px-2">
            {count}
          </span>
        </h2>
        {description && <p className="text-slate-500 font-medium text-sm">{description}</p>}
      </div>
      <div className="flex flex-col gap-4">
        {displayItems}
      </div>
      {isExpandable && !expanded && (
        <button 
          onClick={() => setExpanded(true)}
          className="mt-4 w-full py-3.5 rounded-xl border-2 border-slate-100 text-slate-600 font-bold hover:bg-slate-50 hover:border-slate-200 transition-all flex items-center justify-center gap-2"
        >
          View more (+{items.length - maxInitial})
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
        </button>
      )}
    </div>
  );
};



// --- Page Content ---

export default function ProductPage() {
  const { productId: slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

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

// Tabs removed. Layout uses vertically stacked ExpandableSections.

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
            
            {/* LEFT: Anchor Sidebar */}
            <div className="lg:col-span-6 lg:sticky lg:top-28">
              <LeftProductCard product={product} />
            </div>

            <div className="lg:col-span-6 space-y-8 pb-20 max-h-[calc(100vh-120px)] overflow-y-auto pr-2 custom-scrollbar">
              <div className="flex flex-col gap-6">
                <ExpandableSection 
                  title="Exact Matches" 
                  count={exact_matches?.length || 0}
                >
                  {product && exact_matches?.map((match, idx) => (
                    <RightComparisonCard key={`exact-${idx}`} match={match} anchorProduct={product} />
                  ))}
                </ExpandableSection>

                <ExpandableSection 
                  title="Variants" 
                  count={variant_matches?.length || 0}
                  description="Same underlying model but varying RAM, Storage, or CPU configuration."
                >
                  {product && variant_matches?.map((match, idx) => (
                    <RightComparisonCard key={`var-${idx}`} match={match} anchorProduct={product} />
                  ))}
                </ExpandableSection>

                <ExpandableSection 
                  title="Similar Specs" 
                  count={spec_comparable_matches?.length || 0}
                  description="Different series or models offering equivalent performance."
                >
                  {product && spec_comparable_matches?.map((match, idx) => (
                    <RightComparisonCard key={`sim-${idx}`} match={match} anchorProduct={product} />
                  ))}
                </ExpandableSection>

                {fallback_matches?.length > 0 && (
                  <ExpandableSection 
                    title="Recommended Alternatives" 
                    count={fallback_matches?.length || 0}
                    description="Recommended alternatives based on your selection"
                  >
                    {product && fallback_matches?.map((match, idx) => (
                      <RightComparisonCard key={`fall-${idx}`} match={match} anchorProduct={product} />
                    ))}
                  </ExpandableSection>
                )}
                
                {/* Fallback state when absolutely nothing is found */}
                {(!exact_matches?.length && !variant_matches?.length && !spec_comparable_matches?.length && !fallback_matches?.length) && (
                  <div className="text-center py-20 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                    <p className="text-slate-400 font-bold mb-2">No comparisons available</p>
                    <p className="text-slate-500 text-sm">We couldn't map any direct competitors for this SKU.</p>
                  </div>
                )}
              </div>
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
