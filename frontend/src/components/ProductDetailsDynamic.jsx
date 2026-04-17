import React from 'react';

const StarIcon = ({ filled = true }) => (
  <svg
    className={`w-4 h-4 fill-current transition-colors ${filled ? 'text-amber-400' : 'text-slate-200'}`}
    viewBox="0 0 20 20"
  >
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
  </svg>
);

const RatingStars = ({ rating }) => {
  const filled = Math.round(rating);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((index) => <StarIcon key={index} filled={index <= filled} />)}
    </div>
  );
};

export default function ProductDetailsDynamic({ product }) {
  const bestDealLink = product.primaryStoreLink || product.stores?.[0]?.link || '#';

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2.5 flex-wrap">
        <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-xs font-bold uppercase tracking-wider rounded-full shadow-md shadow-indigo-300/40 transition-transform hover:scale-105 duration-200">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          Top Choice
        </span>

        <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-gradient-to-r from-amber-50 to-orange-50 text-amber-700 text-xs font-bold border border-amber-200 rounded-full shadow-sm shadow-amber-100 transition-transform hover:scale-105 duration-200">
          Best Seller
        </span>

        <div className="flex items-center gap-2 ml-1">
          <RatingStars rating={product.rating} />
          <span className="text-sm font-extrabold text-slate-800">{product.rating}</span>
          <span className="text-sm text-slate-400 font-medium">
            ({product.reviewsCount?.toLocaleString()} reviews)
          </span>
        </div>
      </div>

      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 leading-tight tracking-tight">
        {product.title}
      </h1>

      <p className="text-slate-500 text-sm leading-relaxed">
        {product.description}
      </p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {Object.entries(product.specs).map(([key, value]) => (
          <div
            key={key}
            className="relative bg-slate-50 hover:bg-gradient-to-br hover:from-indigo-50 hover:to-violet-50 p-3.5 rounded-xl border border-slate-100 hover:border-indigo-200 text-center transition-all duration-250 cursor-default group hover:shadow-sm hover:shadow-indigo-100"
          >
            <span className="block text-[9px] font-bold text-slate-400 group-hover:text-indigo-500 uppercase tracking-widest mb-1 transition-colors">
              {key}
            </span>
            <span className="block text-xs font-bold text-slate-800 group-hover:text-slate-900">
              {value}
            </span>
          </div>
        ))}
      </div>

      <div className="border-t border-slate-100 pt-5 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-5">
        <div>
          <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Best Price Available
          </span>
          <div className="flex items-end gap-3">
            <span className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tighter">
              {product.price}
            </span>
            {product.oldPrice ? (
              <span className="text-sm font-medium text-slate-400 line-through mb-1">
                {product.oldPrice}
              </span>
            ) : null}
            {product.discount ? (
              <span className="text-xs font-bold text-emerald-700 bg-gradient-to-r from-emerald-50 to-green-50 border border-emerald-200 px-2.5 py-1 rounded-full mb-1 shadow-sm shadow-emerald-100">
                {product.discount}
              </span>
            ) : null}
          </div>
        </div>

        <div className="flex gap-2.5">
          <a
            href={bestDealLink}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2.5 bg-indigo-600 border border-indigo-600 text-white font-bold text-sm rounded-xl shadow-sm hover:bg-indigo-700 hover:border-indigo-700 hover:shadow-md hover:-translate-y-px transition-all duration-200"
          >
            <span className="text-base leading-none">↗</span>
            Visit Best Deal
          </a>
        </div>
      </div>
    </div>
  );
}
