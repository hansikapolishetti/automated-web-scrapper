import React from 'react';
import ProductCard from './ProductCard';

export default function MatchSection({ title, description, level, products }) {
  if (!products || products.length === 0) return null;

  // Level specific styling mapping
  const levelStyles = {
    1: { bg: "bg-gradient-to-br from-blue-600 to-cyan-500 shadow-blue-500/30", icon: "✨" },
    2: { bg: "bg-slate-800 shadow-slate-500/30", icon: "⚡" },
    3: { bg: "bg-slate-400 shadow-slate-300/30", icon: "🔍" }
  };

  const style = levelStyles[level] || levelStyles[3];

  return (
    <section className="mb-20 animate-fade-in-up">
      <div className="flex items-center gap-5 mb-5">
        <div className={`flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-2xl shadow-xl ${style.bg} text-white`}>
          {style.icon}
        </div>
        <div>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs mb-1">Level {level} Match</p>
          <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            {title}
          </h2>
        </div>
      </div>
      <p className="text-slate-600 text-lg font-medium mb-10 max-w-3xl leading-relaxed">
        {description}
      </p>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 lg:gap-10">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
