import React, { useState, useEffect } from 'react';
import CategoryCard from './CategoryCard';
import { fetchCategories } from '../lib/api';

const INITIAL_CATEGORIES = [
  { 
    id: "laptops", 
    title: "Laptops", 
    description: "Loading...", 
    icon: "💻",
    image: "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-blue-50 to-indigo-50"
  },
  { 
    id: "mobiles", 
    title: "Smartphones", 
    description: "Loading...", 
    icon: "📱",
    image: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-purple-50 to-fuchsia-50"
  },
  { 
    id: "tvs", 
    title: "Televisions", 
    description: "Loading...", 
    icon: "📺",
    image: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-rose-50 to-orange-50"
  },
  { 
    id: "audio", 
    title: "Audio & Audio Devices", 
    description: "Loading...", 
    icon: "🎧",
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-cyan-50 to-teal-50"
  },
  { 
    id: "refrigerators", 
    title: "Refrigerators", 
    description: "Coming Soon", 
    icon: "🧊",
    image: "https://images.unsplash.com/photo-1584568694244-14fbdf83bd30?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-cyan-50 to-teal-50"
  },
  { 
    id: "washers", 
    title: "Washing Machines", 
    description: "Coming Soon", 
    icon: "🧺",
    image: "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
    gradient: "from-yellow-50 to-amber-50"
  },
  { 
    id: "ac", 
    title: "Air Conditioners", 
    description: "Coming Soon", 
    icon: "❄️",
    image: "/images/categories/air-conditioner.jpg",
    gradient: "from-green-50 to-emerald-50"
  },
];

export default function CategoryGrid() {
  const [categories, setCategories] = useState(INITIAL_CATEGORIES);

  useEffect(() => {
    async function updateCounts() {
      try {
        const liveData = await fetchCategories();
        setCategories(prev => prev.map(cat => {
          const liveCat = liveData.find(ld => ld.id === cat.id);
          if (liveCat) {
            return {
              ...cat,
              description: `${liveCat.count.toLocaleString()}+`
            };
          }
          return cat;
        }));
      } catch (err) {
        console.error("Failed to update category counts:", err);
      }
    }
    updateCounts();
  }, []);

  return (
    <section id="categories" className="py-16 bg-slate-50/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl mx-auto mb-12 relative">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-1 bg-gradient-to-r from-transparent via-indigo-500 to-transparent opacity-50 rounded-full mb-6"></div>
          <h2 className="text-3xl md:text-4xl text-slate-900 font-extrabold tracking-tight mb-4 mt-6">
            Shop by <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-blue-500">Category</span>
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto font-medium">
            Discover the best prices and deep comparisons across our most popular product categories.
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {categories.slice(0, 4).map((cat) => (
            <CategoryCard 
              key={cat.id}
              categoryId={cat.id}
              title={cat.title}
              description={cat.description}
              icon={cat.icon}
              image={cat.image}
              gradient={cat.gradient}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
