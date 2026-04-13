import React from 'react';
import CategoryCard from './CategoryCard';

const CATEGORIES = [
  { id: "laptops", title: "Laptops", priceRange: "Under ₹34,999", icon: "💻", active: true },
  { id: "mobiles", title: "Smartphones", priceRange: "Starting ₹10,000", icon: "📱", active: false },
  { id: "tvs", title: "Televisions", priceRange: "Under ₹25,000", icon: "📺", active: false },
  { id: "refrigerators", title: "Refrigerators", priceRange: "Under ₹14,999", icon: "🧊", active: false },
  { id: "washers", title: "Washing Machines", priceRange: "Under ₹16,999", icon: "🧺", active: false },
  { id: "ac", title: "Air Conditioners", priceRange: "Under ₹29,999", icon: "❄️", active: false },
];

export default function CategoryGrid() {
  return (
    <section id="categories" className="py-24 bg-slate-50/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-10">
          <h2 className="text-4xl text-slate-900 font-extrabold tracking-tight">Browse Categories</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 xl:gap-10">
          {CATEGORIES.map((cat) => (
            <CategoryCard 
              key={cat.id}
              title={cat.title}
              priceRange={cat.priceRange}
              icon={cat.icon}
              isActive={cat.active}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
