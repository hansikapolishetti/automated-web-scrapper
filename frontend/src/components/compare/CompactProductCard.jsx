import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function CompactProductCard({ title, price, image, rating }) {
  const navigate = useNavigate();
  const slug = encodeURIComponent(title.toLowerCase().replace(/\s+/g, '-'));

  return (
    <div 
      onClick={() => navigate(`/product/${slug}`)}
      className="group flex flex-col bg-white rounded-2xl border border-slate-200 p-4 hover:border-indigo-300 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer h-full"
    >
      <div className="w-full aspect-[4/3] bg-slate-50 rounded-xl mb-4 overflow-hidden flex items-center justify-center p-4">
        <img src={image} className="max-h-full mix-blend-multiply group-hover:scale-110 transition-transform duration-500" alt={title} />
      </div>
      <div className="flex flex-col flex-grow">
        <h4 className="font-bold text-slate-900 text-sm line-clamp-2 leading-snug mb-2 group-hover:text-indigo-600 transition-colors">
          {title}
        </h4>
        <div className="flex items-center gap-1 text-yellow-400 mb-3">
          <svg className="w-3 h-3 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          <span className="text-xs font-bold text-slate-600">{rating || "4.5"}</span>
        </div>
        <div className="mt-auto">
          <span className="text-lg font-black text-slate-900">{price}</span>
        </div>
      </div>
    </div>
  );
}
