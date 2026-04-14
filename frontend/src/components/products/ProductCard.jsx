import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProductCard({ title, price, rating, image, store, tag, oldPrice }) {
  const navigate = useNavigate();

  const storeColors = {
    'Amazon': 'text-orange-600 bg-orange-50 border-orange-200',
    'Flipkart': 'text-blue-600 bg-blue-50 border-blue-200'
  };

  const tagColors = {
    'Lowest Ever': 'bg-green-100 text-green-700 border-green-200',
    'Great Deal': 'bg-teal-100 text-teal-700 border-teal-200',
    'Above Average': 'bg-yellow-100 text-yellow-700 border-yellow-200',
  };

  const tagClass = tagColors[tag] || 'bg-slate-100 text-slate-600 border-slate-200';
  const badgeClass = storeColors[store] || 'text-slate-600 bg-slate-50 border-slate-200';

  const productSlug = encodeURIComponent(title.toLowerCase().replace(/\s+/g, '-'));

  return (
    <div 
      onClick={() => navigate(`/product/${productSlug}`)}
      className="group flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:border-blue-300 transition-all duration-300 overflow-hidden cursor-pointer h-full"
    >
      <div className="relative aspect-square w-full p-6 bg-slate-50/50 flex items-center justify-center overflow-hidden">
        <img src={image} alt={title} className="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-500" />
        
        {tag && (
          <div className="absolute top-4 right-4">
            <span className={`px-2.5 py-1 text-[0.7rem] uppercase tracking-wider font-bold rounded-full border ${tagClass}`}>
              {tag}
            </span>
          </div>
        )}
      </div>

      <div className="p-5 flex flex-col flex-grow">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-bold text-slate-900 leading-tight line-clamp-2 text-sm">{title}</h3>
        </div>

        <div className="flex items-center gap-1.5 mb-4">
          <div className="flex items-center text-yellow-400">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-700">{rating}</span>
        </div>

        <div className="mt-auto flex items-end justify-between">
          <div>
            <div className="text-lg md:text-xl font-black text-slate-900 tracking-tight">{price}</div>
            {oldPrice && <div className="text-xs font-medium text-slate-400 line-through mt-0.5">{oldPrice}</div>}
          </div>
          
          <div className={`px-2.5 py-1 text-xs font-bold rounded-md border ${badgeClass}`}>
            {store}
          </div>
        </div>
      </div>
    </div>
  );
}
