import React from 'react';

export default function CategorySidebar({ brands = [], selectedBrands = [], onBrandToggle, loading = false }) {
  return (
    <div className="w-full h-full bg-white border border-slate-200 rounded-2xl p-6 shadow-sm sticky top-28">
      <h3 className="font-bold text-lg text-slate-900 mb-6 pb-4 border-b border-slate-100 flex items-center justify-between">
        Available Brands
      </h3>
      
      <div className="space-y-6">
        <div>
          <div className="space-y-3">
            {loading ? (
              <div className="animate-pulse space-y-2">
                {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-4 bg-slate-100 rounded w-full"></div>)}
              </div>
            ) : brands.length > 0 ? (
              brands.map((brand) => (
                <label key={brand} className="flex items-center gap-3 cursor-pointer group">
                  <div className="relative flex items-center justify-center">
                    <input 
                      type="checkbox" 
                      checked={selectedBrands.includes(brand)}
                      onChange={() => onBrandToggle(brand)}
                      className="w-5 h-5 rounded border-2 border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer appearance-none checked:bg-blue-600 checked:border-blue-600 transition-all" 
                    />
                    <svg className={`w-3.5 h-3.5 text-white absolute pointer-events-none transition-opacity ${selectedBrands.includes(brand) ? 'opacity-100' : 'opacity-0'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="flex items-center justify-between w-full">
                    <span className="text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors uppercase">{brand}</span>
                  </div>
                </label>
              ))
            ) : (
              <p className="text-slate-400 text-xs italic">No brands found</p>
            )}
          </div>
        </div>

        <div className="pt-6 border-t border-slate-100 italic text-[10px] text-slate-400 font-medium">
          Note: These brands are currently available in our research database for the selected category.
        </div>
      </div>
    </div>
  );
}
