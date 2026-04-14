import React from 'react';

export default function ComparisonTable({ stores }) {
  // Sort stores dynamically so lowest price is top
  const sortedStores = [...stores].sort((a, b) => a.price - b.price);

  return (
    <div className="mt-8 flex flex-col gap-3">
      {sortedStores.map((store, index) => (
        <a 
          key={store.storeName}
          href={store.link}
          target="_blank"
          rel="noopener noreferrer"
          className={`group flex items-center justify-between p-4 sm:p-5 rounded-2xl border transition-all ${
            index === 0 
              ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200 hover:border-emerald-300 hover:shadow-lg hover:shadow-emerald-100' 
              : 'bg-slate-50 border-slate-100 hover:bg-white hover:border-slate-200 hover:shadow-md hover:shadow-slate-100'
          }`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
            <div className={`font-black text-lg ${index === 0 ? 'text-emerald-800' : 'text-slate-700'}`}>
              {store.storeName}
            </div>
            {index === 0 && (
              <span className="bg-emerald-100 text-emerald-700 text-[11px] font-black px-2.5 py-1 rounded w-fit uppercase tracking-wider">
                Best Deal
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-4">
            <span className={`text-xl sm:text-2xl font-black tracking-tight ${index === 0 ? 'text-emerald-600' : 'text-slate-900'}`}>
              ₹{store.price.toLocaleString('en-IN')}
            </span>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${index === 0 ? 'bg-emerald-200 group-hover:bg-emerald-500' : 'bg-slate-200 group-hover:bg-blue-600'}`}>
              <svg className={`w-4 h-4 transition-transform group-hover:translate-x-0.5 ${index === 0 ? 'text-emerald-800 group-hover:text-white' : 'text-slate-600 group-hover:text-white'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}
