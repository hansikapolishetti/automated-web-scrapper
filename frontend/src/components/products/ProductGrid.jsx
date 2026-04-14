import React from 'react';
import ProductCard from './ProductCard';

export default function ProductGrid({ products }) {
  if (!products || products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-slate-200">
        <div className="text-4xl mb-4 opacity-50">🔍</div>
        <h3 className="text-lg font-bold text-slate-900 mb-2">No products found</h3>
        <p className="text-slate-500 text-center">We couldn't find any products matching your current filters.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
      {products.map((p, idx) => (
        <ProductCard key={idx} {...p} />
      ))}
    </div>
  );
}
