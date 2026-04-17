import React from 'react';

const STORE_LOGOS = {
  amazon: '/logos/amazon.svg',
  flipkart: '/logos/flipkart.svg',
  croma: '/logos/croma.svg',
  reliance: '/logos/reliance.svg',
};

const STORE_COLORS = {
  amazon: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700' },
  flipkart: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
  croma: { bg: 'bg-slate-900', border: 'border-slate-700', text: 'text-white' },
  reliance: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' },
};

const DEFAULT_THEME = { bg: 'bg-slate-100', border: 'border-slate-200', text: 'text-slate-600' };

function getStoreMeta(name) {
  const key = Object.keys(STORE_LOGOS).find((storeKey) => name.toLowerCase().includes(storeKey));
  return {
    logo: key ? STORE_LOGOS[key] : null,
    theme: key ? STORE_COLORS[key] : DEFAULT_THEME,
    initial: name.charAt(0).toUpperCase(),
  };
}

function StoreLogo({ name }) {
  const { logo, theme, initial } = getStoreMeta(name);
  const [failed, setFailed] = React.useState(false);

  if (logo && !failed) {
    return (
      <div className={`w-12 h-12 rounded-xl border ${theme.border} bg-white flex items-center justify-center overflow-hidden flex-shrink-0 p-1.5`}>
        <img
          src={logo}
          alt={name}
          className="w-full h-full object-contain"
          onError={() => setFailed(true)}
        />
      </div>
    );
  }

  return (
    <div className={`w-12 h-12 rounded-xl border ${theme.border} ${theme.bg} flex items-center justify-center font-black text-lg ${theme.text} flex-shrink-0`}>
      {initial}
    </div>
  );
}

export default function StorePriceListDynamic({ stores }) {
  return (
    <div>
      <div className="flex items-center gap-3 mb-5">
        <div className="flex-1 h-px bg-slate-100" />
        <h3 className="text-sm font-extrabold text-slate-500 uppercase tracking-widest whitespace-nowrap px-2">
          Compare Prices
        </h3>
        <div className="flex-1 h-px bg-slate-100" />
      </div>

      <div className="flex flex-col gap-3">
        {stores.map((store, idx) => (
          <a
            key={idx}
            href={store.link}
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-center justify-between px-4 py-3.5 rounded-2xl border transition-all duration-200 ${
              store.inStock
                ? 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-md hover:-translate-y-px cursor-pointer'
                : 'bg-slate-50 border-slate-100 opacity-55 cursor-not-allowed'
            }`}
          >
            <div className="flex items-center gap-3">
              <StoreLogo name={store.name} />
              <div>
                <span className="block font-bold text-slate-900 text-sm leading-tight">{store.name}</span>
                <span className={`text-xs font-semibold mt-0.5 flex items-center gap-1.5 ${store.inStock ? 'text-emerald-600' : 'text-red-500'}`}>
                  <span className={`inline-block w-1.5 h-1.5 rounded-full flex-shrink-0 ${store.inStock ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  {store.delivery}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <span className="block font-black text-lg text-slate-900 tracking-tight">{store.price}</span>
              </div>
              <span
                className={`px-4 py-2 rounded-xl font-bold text-xs transition-all duration-200 whitespace-nowrap ${
                  store.inStock
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md shadow-indigo-200 hover:shadow-lg hover:shadow-indigo-300'
                    : 'bg-slate-200 text-slate-400'
                }`}
              >
                {store.inStock ? 'Visit Store' : 'Out of Stock'}
              </span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
