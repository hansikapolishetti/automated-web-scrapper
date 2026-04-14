import React from 'react';

export default function StorePriceList({ stores }) {
  return (
    <div>
      <h3 className="text-base font-extrabold text-slate-900 mb-4">Compare Available Prices</h3>
      <div className="flex flex-col gap-3">
        {stores.map((store, idx) => (
          <div key={idx} className={`flex items-center justify-between p-3 sm:p-4 rounded-xl border ${store.inStock ? 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-md' : 'bg-slate-50 border-slate-100 opacity-60'} transition-all cursor-pointer`}>
            
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-slate-100 rounded-full flex items-center justify-center font-black text-slate-400 text-base">
                {store.logo}
              </div>
              <div>
                <span className="block font-bold text-slate-900 text-sm">{store.name}</span>
                <span className={`text-xs font-medium ${store.inStock ? 'text-green-600' : 'text-red-500'}`}>{store.delivery}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <span className="block font-black text-base text-slate-900">{store.price}</span>
              </div>
              <button disabled={!store.inStock} className={`px-4 py-2 rounded-lg font-bold text-xs transition-colors ${store.inStock ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md hover:shadow-lg' : 'bg-slate-200 text-slate-400 cursor-not-allowed'}`}>
                {store.inStock ? 'Visit Store' : 'Out of Stock'}
              </button>
            </div>
            
          </div>
        ))}
      </div>
    </div>
  );
}
