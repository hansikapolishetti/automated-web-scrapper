import React from 'react';
import { useNavigate } from 'react-router-dom';

const StarRating = ({ rating }) => {
  const filled = Math.round(parseFloat(rating) || 4.5);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(i => (
        <svg
          key={i}
          className={`w-3.5 h-3.5 fill-current ${i <= filled ? 'text-amber-400' : 'text-slate-200'}`}
          viewBox="0 0 20 20"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
      <span className="text-[10px] font-semibold text-slate-400 ml-1">
        {parseFloat(rating) || 4.5}
      </span>
    </div>
  );
};

export default function CompactProductCard({ title, price, image, rating, discount }) {
  const navigate = useNavigate();
  const slug = encodeURIComponent(title.toLowerCase().replace(/\s+/g, '-'));

  return (
    <div
      onClick={() => navigate(`/product/${slug}`)}
      className="group flex flex-col bg-white rounded-2xl border border-slate-200
                 shadow-sm cursor-pointer overflow-hidden
                 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-100/40
                 hover:scale-[1.02] hover:-translate-y-1
                 transition-all duration-300"
    >
      {/* ── Image ── */}
      <div
        className="relative w-full flex items-center justify-center overflow-hidden"
        style={{
          height: '160px',
          background: 'linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%)',
        }}
      >
        {discount && (
          <span className="absolute top-2.5 left-2.5 z-10
                           bg-gradient-to-r from-emerald-500 to-green-500
                           text-white text-[9px] font-black
                           px-2 py-0.5 rounded-full shadow-sm">
            {discount}
          </span>
        )}
        <img
          src={image}
          alt={title}
          className="h-full w-full object-contain mix-blend-multiply p-4
                     group-hover:scale-110 transition-transform duration-500"
        />
      </div>

      {/* ── Content ── */}
      <div className="flex flex-col flex-grow p-4 gap-2 border-t border-slate-100">
        {/* Name */}
        <h4 className="text-sm font-semibold text-slate-800 line-clamp-2 leading-snug
                       group-hover:text-indigo-700 transition-colors duration-200">
          {title}
        </h4>

        {/* Rating */}
        <StarRating rating={rating} />

        {/* Price + button */}
        <div className="flex items-center justify-between mt-auto pt-2">
          <span className="text-base font-extrabold text-slate-900 tracking-tight">
            {price}
          </span>
          <button
            onClick={e => { e.stopPropagation(); navigate(`/product/${slug}`); }}
            className="text-xs font-bold text-indigo-600
                       border border-indigo-200 bg-indigo-50
                       hover:bg-indigo-600 hover:text-white hover:border-indigo-600
                       hover:shadow-md hover:shadow-indigo-200
                       px-4 py-1.5 rounded-full
                       transition-all duration-200 whitespace-nowrap"
          >
            Compare
          </button>
        </div>
      </div>
    </div>
  );
}
