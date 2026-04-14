import React, { useState } from 'react';
import CompactProductCard from './CompactProductCard';

export default function ComparisonWorkspace({ product }) {
  const [activeTab, setActiveTab] = useState('all');

  const exact = product.exactMatches || [];
  const variants = product.variantMatches || [];
  const similar = product.similarSpecs || [];
  
  const allComparable = [...exact, ...variants, ...similar];

  const getActiveList = () => {
    if (activeTab === 'exact') return exact;
    if (activeTab === 'variants') return variants;
    if (activeTab === 'similar') return similar;
    return allComparable;
  };

  const currentList = getActiveList();

  const tabs = [
    { id: 'all', label: 'All Comparable' },
    { id: 'exact', label: 'Exact Match' },
    { id: 'variants', label: 'Variant Match' },
    { id: 'similar', label: 'Similar Specs' }
  ];

  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 lg:p-8 flex flex-col max-h-[calc(100vh-4rem)] h-full">
      
      {/* Pill Tab Navigation */}
      <div className="flex items-center gap-1 mb-6 overflow-x-auto pb-2 scrollbar-hide border-b border-slate-100">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
              activeTab === tab.id 
                ? 'bg-slate-50 border border-slate-200 text-slate-800' 
                : 'text-slate-400 hover:text-slate-700 bg-transparent border border-transparent'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-bold text-slate-500 tracking-tight">Best Deals</h3>
        <span className="text-xs font-bold text-slate-400 bg-slate-50 px-2 py-1 rounded-md">{currentList.length} items</span>
      </div>
      
      {/* Scrollable Container */}
      <div className="flex-1 overflow-y-auto pr-2 -mr-2 space-y-4">
        {currentList.length === 0 ? (
          <div className="text-center py-12 text-slate-500 font-medium">No components match this filter.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-4">
            {currentList.map((item, i) => <CompactProductCard key={i} {...item} />)}
          </div>
        )}
      </div>

    </div>
  );
}
