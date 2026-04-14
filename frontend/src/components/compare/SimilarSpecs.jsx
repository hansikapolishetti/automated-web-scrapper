import React from 'react';
import CompactProductCard from './CompactProductCard';

export default function SimilarSpecs({ items }) {
  return (
    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8">
      <div className="flex items-end justify-between mb-8">
        <div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Similar Specifications</h2>
          <p className="text-slate-500 font-medium mt-1">Found {items.length} competitor products offering similar hardware.</p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((item, i) => <CompactProductCard key={i} {...item} />)}
      </div>
    </div>
  );
}
