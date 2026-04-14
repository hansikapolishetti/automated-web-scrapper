import React from 'react';

const CATEGORIES = [
  "Electronics",
  "Computers & Accessories",
  "Cameras & Photography",
  "Headphones / Earbuds",
  "Mobiles & Accessories"
];

const BRANDS = [
  "Apple",
  "Samsung",
  "Sony",
  "Dell",
  "HP",
  "Lenovo"
];

export default function FilterSidebar() {
  return (
    <div className="w-full h-full bg-white border border-slate-200 rounded-2xl p-6 shadow-sm sticky top-28">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <h3 className="font-bold text-lg text-slate-900">Filters</h3>
        <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md cursor-pointer hover:bg-blue-100 transition-colors">Clear all</span>
      </div>
      
      <div className="space-y-7">
        
        {/* Categories */}
        <section>
          <h4 className="font-semibold text-slate-800 mb-4 text-xs uppercase tracking-widest">Categories</h4>
          <div className="space-y-3">
            {CATEGORIES.map((cat, index) => (
              <label key={cat} className="flex items-center gap-3 cursor-pointer group">
                <div className="relative flex items-center justify-center flex-shrink-0">
                  <input 
                    type="checkbox" 
                    className="w-4.5 h-4.5 aspect-square rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer appearance-none checked:bg-blue-600 checked:border-blue-600 transition-all peer" 
                  />
                  <svg className="w-3.5 h-3.5 text-white absolute pointer-events-none opacity-0 peer-checked:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors leading-tight">{cat}</span>
              </label>
            ))}
          </div>
        </section>

        {/* Brands */}
        <section className="pt-6 border-t border-slate-100">
          <h4 className="font-semibold text-slate-800 mb-4 text-xs uppercase tracking-widest">Brands</h4>
          <div className="space-y-3 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
            {BRANDS.map((brand) => (
              <label key={brand} className="flex items-center justify-between cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="relative flex items-center justify-center flex-shrink-0">
                    <input 
                      type="checkbox" 
                      className="w-4.5 h-4.5 aspect-square rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer appearance-none checked:bg-blue-600 checked:border-blue-600 transition-all peer" 
                    />
                    <svg className="w-3.5 h-3.5 text-white absolute pointer-events-none opacity-0 peer-checked:opacity-100" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">{brand}</span>
                </div>
              </label>
            ))}
          </div>
        </section>

        {/* Price Range */}
        <section className="pt-6 border-t border-slate-100">
           <h4 className="font-semibold text-slate-800 mb-4 text-xs uppercase tracking-widest">Price Range</h4>
           <div className="flex items-center gap-2 mb-4">
             <div className="relative">
               <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">₹</span>
               <input type="number" placeholder="Min" className="w-full pl-7 pr-3 py-2 rounded-lg border border-slate-200 text-sm focus:border-blue-400 focus:ring-1 focus:ring-blue-400 outline-none transition-all" />
             </div>
             <span className="text-slate-400 text-sm">-</span>
             <div className="relative">
               <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">₹</span>
               <input type="number" placeholder="Max" className="w-full pl-7 pr-3 py-2 rounded-lg border border-slate-200 text-sm focus:border-blue-400 focus:ring-1 focus:ring-blue-400 outline-none transition-all" />
             </div>
           </div>
           <button className="w-full py-2 bg-slate-50 hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 hover:border-blue-200 font-semibold text-sm rounded-lg transition-all">
             Apply Price Filter
           </button>
        </section>
        
      </div>
    </div>
  );
}
