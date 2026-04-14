import React from 'react';

const CATEGORIES = [
  "Electronics",
  "Computers & Accessories",
  "Cameras & Photography",
  "Headphones / Earbuds",
  "Mobiles & Accessories"
];

export default function CategorySidebar() {
  return (
    <div className="w-full h-full bg-white border border-slate-200 rounded-2xl p-6 shadow-sm sticky top-28">
      <h3 className="font-bold text-lg text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center justify-between">
        Filters
        <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-1 rounded cursor-pointer hover:bg-blue-100 transition-colors">Clear all</span>
      </h3>
      
      <div className="space-y-6">
        <div>
          <h4 className="font-semibold text-slate-800 mb-4 text-sm uppercase tracking-wider">Categories</h4>
          <div className="space-y-3">
            {CATEGORIES.map((cat, index) => (
              <label key={cat} className="flex items-center gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center">
                  <input 
                    type="checkbox" 
                    defaultChecked={index === 0 || index === 4}
                    className="w-5 h-5 rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer appearance-none checked:bg-blue-600 checked:border-blue-600 transition-all" 
                  />
                  <svg className="w-3.5 h-3.5 text-white absolute pointer-events-none opacity-0 peer-checked:opacity-100" style={{opacity: (index === 0 || index === 4) ? 1 : 0}} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">{cat}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="pt-6 border-t border-slate-100">
           <h4 className="font-semibold text-slate-800 mb-4 text-sm uppercase tracking-wider">Price Range</h4>
           <div className="flex items-center gap-2">
             <input type="number" placeholder="Min" className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:border-blue-400 focus:ring-1 focus:ring-blue-400 outline-none" />
             <span className="text-slate-400">-</span>
             <input type="number" placeholder="Max" className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:border-blue-400 focus:ring-1 focus:ring-blue-400 outline-none" />
           </div>
           <button className="mt-3 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm rounded-lg transition-colors">
             Apply
           </button>
        </div>
      </div>
    </div>
  );
}
