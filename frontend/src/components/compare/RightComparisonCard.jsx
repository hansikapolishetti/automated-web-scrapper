import React from 'react';

// --- Safety Helpers ---
const cleanPrice = (val) => {
  if (val === undefined || val === null) return 0;
  if (typeof val === 'number') return val;
  // Handle strings like "₹43,990"
  const cleaned = String(val).replace(/[₹,\s]/g, "");
  return Number(cleaned) || 0;
};

const formatPrice = (val) => {
  const price = cleanPrice(val);
  if (price === 0) return "N/A";
  return price.toLocaleString('en-IN');
};

const analyzeSpecDiff = (valA, valB, key) => {
  if (!valB) return { status: 'missing', text: 'N/A' };
  if (!valA) return { status: 'diff', text: valB };
  
  const aStr = String(valA).toLowerCase().trim();
  const bStr = String(valB).toLowerCase().trim();
  
  if (aStr === bStr) return { status: 'same', text: valB };
  
  if (['ram', 'storage', 'price', 'processor', 'cpu'].includes(key.toLowerCase())) {
    const getTier = (str) => {
      const s = str.toLowerCase();
      if (s.includes('i9') || s.includes('ryzen 9')) return 9;
      if (s.includes('i7') || s.includes('ryzen 7')) return 7;
      if (s.includes('i5') || s.includes('ryzen 5')) return 5;
      if (s.includes('i3') || s.includes('ryzen 3')) return 3;
      if (s.includes('celeron') || s.includes('athlon')) return 1;
      return 0;
    };

    const numA = cleanPrice(valA) || getTier(aStr);
    const numB = cleanPrice(valB) || getTier(bStr);
    
    if (numA && numB) {
      if (key.toLowerCase() === 'price') {
        if (numB === numA) return { status: 'same', text: valB };
        return numB < numA ? { status: 'better', text: valB, diff: numA - numB } : { status: 'worse', text: valB, diff: numB - numA };
      } else {
        // For processor/RAM: same tier = 'same_tier', not better/worse
        if (numB === numA) return { status: 'same_tier', text: valB };
        return numB > numA ? { status: 'better', text: valB } : { status: 'worse', text: valB };
      }
    }
  }
  
  return { status: 'diff', text: valB };
};

const ComparisonRow = ({ label, value, status, diffLabel, isRight = false }) => {
  return (
    <div className={`flex items-center justify-between h-10 w-full`}>
      {!isRight ? (
        <>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{label}</span>
          <span className="text-slate-600 text-sm font-medium truncate ml-2 text-right">{value || 'N/A'}</span>
        </>
      ) : (
        <>
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-slate-900 text-sm font-bold truncate">{value || 'N/A'}</span>
            {status === 'better' && (
              <span className="text-green-600 text-[9px] bg-green-100 px-1.5 py-0.5 rounded font-black uppercase whitespace-nowrap">
                {diffLabel || 'Better'}
              </span>
            )}
            {status === 'worse' && (
              <span className="text-red-600 text-[9px] bg-red-100 px-1.5 py-0.5 rounded font-black uppercase whitespace-nowrap">
                {diffLabel || 'Worse'}
              </span>
            )}
            {status === 'same_tier' && diffLabel && (
              <span className="text-blue-600 text-[9px] bg-blue-100 px-1.5 py-0.5 rounded font-black uppercase whitespace-nowrap">
                {diffLabel}
              </span>
            )}
            {status === 'same' && diffLabel === 'Same price' && (
              <span className="text-slate-400 text-[9px] bg-slate-100 px-1.5 py-0.5 rounded font-bold uppercase whitespace-nowrap">
                Same
              </span>
            )}
          </div>
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider ml-2">{label}</span>
        </>
      )}
    </div>
  );
};

export default function RightComparisonCard({ match, anchorProduct }) {
  if (!anchorProduct || !match) return null;

  const isPairMatch = !!match.amazon && !!match.flipkart;
  let productB = match;
  if (isPairMatch) {
    const amzSlug = match.amazon?.slug || '';
    const isAmzAnchor = anchorProduct && amzSlug === anchorProduct.slug;
    productB = isAmzAnchor ? match.flipkart : match.amazon;
  }

  if (!productB) return null;

  const specA = anchorProduct?.specifications || {};
  const specB = productB?.specifications || productB?.specs || {};

  const procA = specA.processor || specA.cpu;
  const procB = specB.processor || specB.cpu;
  const ramA = specA.ram;
  const ramB = specB.ram;

  // Extract price correctly
  const priceA = anchorProduct?.price || anchorProduct?.stores?.[0]?.price;
  const priceB = productB?.price || productB?.stores?.[0]?.price;

  // Debug Logs
  console.log("ANCHOR PRODUCT:", anchorProduct?.title || anchorProduct?.name, "| PRICE:", anchorProduct?.price || anchorProduct?.stores?.[0]?.price);
  console.log("RIGHT PRODUCT:", productB?.name || productB?.title, "| PRICE:", productB?.price || productB?.stores?.[0]?.price);

  const procComp = analyzeSpecDiff(procA, procB, 'processor');
  const ramComp = analyzeSpecDiff(ramA, ramB, 'ram');
  const priceComp = analyzeSpecDiff(priceA, priceB, 'price');

  let headerParts = [];
  let headerColor = "text-gray-500";

  if (procComp.status === 'better') { headerParts.push("Better processor"); headerColor = "text-green-600"; }
  else if (procComp.status === 'worse') { headerParts.push("Older processor"); headerColor = "text-red-600"; }
  else if (procComp.status === 'same_tier') { headerParts.push("Same tier processor"); headerColor = "text-blue-600"; }

  if (ramComp.status === 'better') { headerParts.push("More RAM"); headerColor = "text-green-600"; }
  else if (ramComp.status === 'worse') { headerParts.push("Lower RAM"); headerColor = "text-red-600"; }
  else if (ramComp.status === 'same_tier') { headerParts.push("Same RAM"); }

  if (priceComp.status === 'better' && priceComp.diff) { 
    headerParts.push(`₹${(Number(priceComp.diff) || 0).toLocaleString('en-IN')} cheaper`); 
    headerColor = "text-green-600"; 
  }
  else if (priceComp.status === 'worse' && priceComp.diff) { 
    headerParts.push(`₹${(Number(priceComp.diff) || 0).toLocaleString('en-IN')} more`); 
    headerColor = "text-red-600"; 
  }
  else if (priceComp.status === 'same' && cleanPrice(priceB) > 0) { 
    headerParts.push("Same price"); 
  }

  const headerText = headerParts.join(" • ") || "Recommended Alternative";

  return (
    <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden hover:shadow-xl transition-all duration-300">
      <div className={`px-6 py-3 border-b border-slate-100 font-bold text-xs ${headerColor} bg-slate-50/50 uppercase tracking-tighter`}>
        {headerText}
      </div>

      <div className="p-6">
        {/* Top Section: Alternative Info */}
        <div className="flex justify-between items-start mb-8">
           <div className="flex-1 pr-10">
              <p className="text-xs font-black text-slate-900 leading-tight line-clamp-2">
                {productB.name || productB.title}
              </p>
           </div>
           <div className="shrink-0">
              <img 
                src={productB.image || productB.images?.[0]} 
                alt={productB.name} 
                className="w-20 h-20 object-contain" 
              />
           </div>
        </div>

        {/* Comparison Grid */}
        <div className="flex justify-between items-start">
          {/* LEFT SIDE (Anchor) */}
          <div className="flex flex-col gap-3 w-1/2">
            <ComparisonRow label="Processor" value={procA} />
            <ComparisonRow label="RAM" value={ramA} />
            <ComparisonRow label="Storage" value={specA.storage} />
            <ComparisonRow label="Price" value={`₹${formatPrice(priceA)}`} />
          </div>

          {/* DIVIDER */}
          <div className="w-px bg-slate-100 self-stretch mx-6"></div>

          {/* RIGHT SIDE (Alternative) */}
          <div className="flex flex-col gap-3 w-1/2">
            <ComparisonRow 
              isRight 
              label="Processor" 
              value={procB} 
              status={procComp.status} 
              diffLabel={
                procComp.status === 'better' ? 'Better' :
                procComp.status === 'worse'  ? 'Older'  :
                procComp.status === 'same_tier' ? 'Same Tier' : ''
              }
            />
            <ComparisonRow 
              isRight 
              label="RAM" 
              value={ramB} 
              status={ramComp.status} 
              diffLabel={
                ramComp.status === 'better' ? 'More RAM' :
                ramComp.status === 'worse'  ? 'Less RAM' :
                ramComp.status === 'same_tier' ? 'Same' : ''
              }
            />
            <ComparisonRow 
              isRight 
              label="Storage" 
              value={specB.storage} 
            />
            <ComparisonRow 
              isRight 
              label="Price" 
              value={`₹${formatPrice(priceB)}`} 
              status={priceComp.status}
              diffLabel={
                priceComp.status === 'better' && priceComp.diff ? `₹${(Number(priceComp.diff) || 0).toLocaleString('en-IN')} Off` : 
                priceComp.status === 'same' ? 'Same price' : 
                priceComp.status === 'worse' && priceComp.diff ? `+₹${(Number(priceComp.diff) || 0).toLocaleString('en-IN')}` : 
                ''
              }
            />
          </div>
        </div>

        {/* Action Button */}
        <div className="mt-8 flex justify-end">
          <button
            onClick={() => window.open(productB.link || productB.buyLink, "_blank")}
            className="bg-slate-900 text-white px-8 py-3 rounded-2xl text-xs font-black hover:bg-black transition-all shadow-sm active:scale-95 uppercase tracking-widest"
          >
            Get Deal on {productB.website || 'Store'}
          </button>
        </div>
      </div>
    </div>
  );
}
