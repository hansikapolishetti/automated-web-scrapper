import React from 'react';

export default function LeftProductCard({ product }) {
  if (!product) return null;

  // Title splitting logic as per mandatory instructions
  const fullName = product.title || product.name || '';
  const parts = fullName.split(" - ");
  const name = parts[0];
  const subtitle = parts[1] || "";

  // Get price from the first available store or fallback
  const primaryStore = product.stores?.[0] || {};
  const price = primaryStore.price ? `₹${primaryStore.price.toLocaleString('en-IN')}` : 'Price unavailable';
  const buyLink = primaryStore.link || '#';
  const platform = primaryStore.name || product.website || 'Marketplace';

  // Platform Icons mapping
  const platformIcons = {
    'Amazon': '/logos/amazon.svg',
    'Flipkart': '/logos/flipkart.svg',
    'Croma': '/logos/croma.svg',
    'Reliance': '/logos/reliance.svg'
  };
  const iconSrc = platformIcons[platform] || null;

  // Specs mapping (Only Processor, RAM, Storage, Display)
  const specs = [
    { label: 'Processor', value: product.specifications?.processor || product.specifications?.cpu || 'N/A' },
    { label: 'RAM', value: product.specifications?.ram || 'N/A' },
    { label: 'Storage', value: product.specifications?.storage || 'N/A' },
    { label: 'Display', value: product.specifications?.display_size || product.specifications?.screen_size || 'N/A' }
  ];

  return (
    <div 
      onClick={() => window.open(buyLink, "_blank")}
      className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm cursor-pointer hover:shadow-lg hover:scale-[1.01] transition-all duration-200 group"
    >
      {/* 1. Product Image (centered) */}
      <div className="flex justify-center mb-8">
        <div className="w-full max-w-[300px] aspect-square flex items-center justify-center p-6 bg-slate-50 rounded-2xl">
          {product.images?.[0] ? (
            <img 
              src={product.images[0]} 
              alt={name} 
              className="max-w-full max-h-full object-contain mix-blend-multiply group-hover:scale-105 transition-transform duration-500" 
            />
          ) : (
            <div className="text-slate-300">
               <svg className="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
            </div>
          )}
        </div>
      </div>

      {/* 2. Product Name (BLACK, bold) */}
      <h1 className="text-black font-semibold text-lg line-clamp-2 leading-tight">
        {name}
      </h1>

      {/* 3. Subtitle (GREY, smaller) */}
      {subtitle && (
        <p className="text-gray-500 text-sm mt-1 leading-snug">
          {subtitle}
        </p>
      )}

      {/* 4. Price (BIG, bold, black) */}
      <div className="text-2xl font-bold text-black mt-3">
        {price}
      </div>

      {/* 5. Availability (icon + platform name) */}
      <div className="flex items-center gap-2 mt-4">
        {iconSrc && (
          <div className="w-5 h-5 flex items-center justify-center bg-slate-100 rounded-md p-0.5">
            <img src={iconSrc} alt={platform} className="w-full h-full object-contain" />
          </div>
        )}
        <span className="text-sm text-gray-500">
          Available on <span className="text-blue-600 font-semibold">{platform}</span>
        </span>
      </div>

      {/* 6. Specs Grid (2x2 ONLY) */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        {specs.map((spec, i) => (
          <div key={i} className="bg-gray-100 p-2 rounded-lg flex flex-col gap-0.5">
            <span className="text-gray-400 text-xs uppercase tracking-wider">{spec.label}</span>
            <span className="font-medium text-sm text-slate-900 truncate" title={spec.value}>
              {spec.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
