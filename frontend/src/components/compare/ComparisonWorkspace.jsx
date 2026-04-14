import React, { useState } from 'react';
import CompactProductCard from './CompactProductCard';

const TABS = [
  { id: 'all',      label: 'All'         },
  { id: 'exact',    label: 'Exact Match' },
  { id: 'variants', label: 'Variants'    },
  { id: 'similar',  label: 'Similar'     },
];

export default function ComparisonWorkspace({ product }) {
  const [activeTab, setActiveTab] = useState('all');

  const exact         = product.exactMatches   || [];
  const variants      = product.variantMatches || [];
  const similar       = product.similarSpecs   || [];
  const allComparable = [...exact, ...variants, ...similar];

  const listMap    = { all: allComparable, exact, variants, similar };
  const currentList = listMap[activeTab] ?? allComparable;

  const counts = {
    all:      allComparable.length,
    exact:    exact.length,
    variants: variants.length,
    similar:  similar.length,
  };

  return (
    <div className="flex flex-col max-h-[calc(100vh-4rem)] h-full overflow-hidden">

      {/* ── Section Header ── */}
      <div className="pb-5 border-b border-slate-200">

        {/* Title row */}
        <div className="flex items-start justify-between gap-4 mb-5">
          <div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight leading-tight">
              Compare Similar Products
            </h2>
            <p className="text-xs text-slate-400 font-medium mt-1">
              Best alternatives across all Indian stores
            </p>
          </div>

          {/* Live count pill */}
          <span className="flex-shrink-0 flex items-center gap-1.5
                           text-xs font-bold text-indigo-600
                           bg-gradient-to-r from-indigo-50 to-violet-50
                           border border-indigo-200 px-3 py-1.5 rounded-full mt-0.5
                           shadow-sm shadow-indigo-100">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse inline-block" />
            {allComparable.length} products
          </span>
        </div>

        {/* ── Pill Tab Bar ── */}
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
          {TABS.map(({ id, label }) => {
            const isActive = activeTab === id;
            return (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`
                  flex-shrink-0 inline-flex items-center gap-2
                  px-4 py-1.5 rounded-full text-sm font-semibold
                  border transition-all duration-250
                  ${isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white border-transparent shadow-md shadow-indigo-300/40 scale-[1.03]'
                    : 'bg-white text-slate-500 border-slate-200 hover:border-indigo-300 hover:text-indigo-700 hover:bg-indigo-50'}
                `}
              >
                {label}
                <span
                  className={`
                    inline-flex items-center justify-center
                    min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-bold
                    transition-colors duration-200
                    ${isActive ? 'bg-white/25 text-white' : 'bg-slate-100 text-slate-500'}
                  `}
                >
                  {counts[id]}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Scrollable Card Grid ── */}
      <div className="flex-1 overflow-y-auto py-5">
        {currentList.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
            <div className="w-14 h-14 bg-slate-100 rounded-2xl flex items-center justify-center">
              <svg className="w-6 h-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
              </svg>
            </div>
            <div>
              <p className="text-slate-600 font-semibold text-sm">No products match this filter</p>
              <p className="text-slate-400 text-xs mt-0.5">Try selecting a different tab above</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pb-6">
            {currentList.map((item, i) => (
              <CompactProductCard key={i} {...item} />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
