import React from 'react';
import ComparisonTable from './ComparisonTable';

export default function ProductCard({ product }) {
  return (
    <div className="bg-white rounded-[2rem] border border-slate-200 shadow-xl shadow-slate-200/40 p-6 sm:p-8 hover:shadow-2xl hover:shadow-slate-200/60 transition-all duration-300">
      <div className="flex flex-col lg:flex-row gap-8">
        
        {/* Product Image */}
        <div className="w-full lg:w-1/3 xl:w-2/5 flex-shrink-0 flex flex-col items-center justify-center p-6 sm:p-10 bg-slate-50 rounded-3xl border border-slate-100 relative group overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-100/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <img src={product.image} alt={product.name} className="w-full max-w-[220px] h-auto object-contain mix-blend-multiply drop-shadow-lg group-hover:scale-105 transition-transform duration-500" />
        </div>
        
        {/* Product Details & Specs */}
        <div className="w-full lg:w-2/3 xl:w-3/5 flex flex-col">
          <h3 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight leading-tight mb-5">
            {product.name}
          </h3>
          
          {/* Specification Pills */}
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.entries(product.specs).map(([key, value]) => (
              <div key={key} className="bg-blue-50 border border-blue-100 text-blue-800 px-3 py-1.5 rounded-lg text-sm font-bold capitalize">
                <span className="opacity-60 mr-1">{key}:</span> {value}
              </div>
            ))}
          </div>
          
          <div className="mt-auto">
            <ComparisonTable stores={product.stores} />
          </div>
        </div>
      </div>
    </div>
  );
}
