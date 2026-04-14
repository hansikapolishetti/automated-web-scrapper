import React from 'react';

export default function ProductDetails({ product }) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <span className="px-3 py-1 bg-indigo-50 text-indigo-700 text-xs font-bold uppercase tracking-wider rounded-full border border-indigo-100">Top Choice</span>
        <div className="flex items-center gap-1 text-yellow-400">
          <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <span className="text-sm font-bold text-slate-700 ml-1">{product.rating} <span className="font-medium text-slate-400">({product.reviewsCount} reviews)</span></span>
        </div>
      </div>
      
      <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 leading-tight mb-4 tracking-tight">
        {product.title}
      </h1>
      
      <p className="text-slate-600 text-sm mb-5 leading-relaxed">
        {product.description}
      </p>
      
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-5">
        {Object.entries(product.specs).map(([key, val]) => (
          <div key={key} className="bg-slate-50 p-3 rounded-lg border border-slate-100 text-center">
            <span className="block text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">{key}</span>
            <span className="block text-xs font-semibold text-slate-800">{val}</span>
          </div>
        ))}
      </div>
      
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-6">
        <div>
          <span className="block text-xs font-bold text-slate-500 mb-1">Best Price Available</span>
          <div className="flex items-end gap-2">
            <span className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tighter">{product.price}</span>
            <span className="text-sm font-medium text-slate-400 line-through mb-1">{product.oldPrice}</span>
            <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded-md mb-1">{product.discount}</span>
          </div>
        </div>
        
        <div className="flex gap-2">
          {['Share', 'Save'].map((action, i) => (
            <button key={i} className="px-4 py-2 bg-white border border-slate-200 text-slate-700 font-bold rounded-lg shadow-sm hover:bg-slate-50 transition-colors">
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
