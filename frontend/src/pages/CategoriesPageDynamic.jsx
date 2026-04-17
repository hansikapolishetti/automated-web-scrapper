import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import CategorySidebar from '../components/filters/CategorySidebar';
import ProductGrid from '../components/products/ProductGrid';
import { fetchProducts } from '../lib/api';
import { formatCountLabel, normalizeProductsForGrid } from '../lib/productAdapters';

export default function CategoriesPageDynamic() {
  const [searchQuery, setSearchQuery] = useState('');
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    let isActive = true;

    const loadProducts = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await fetchProducts({ query: searchQuery, category: 'all', limit: 24 });
        if (isActive) {
          setProducts(normalizeProductsForGrid(response.items));
          setTotal(response.total ?? response.items.length);
        }
      } catch (fetchError) {
        if (isActive) {
          setProducts([]);
          setTotal(0);
          setError(fetchError.message || 'Failed to load marketplace products');
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    loadProducts();

    return () => {
      isActive = false;
    };
  }, [searchQuery]);

  return (
    <div className="min-h-screen bg-slate-50 font-sans antialiased text-slate-900">
      <Navbar forceDarkText />
      <main className="pt-28 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 lg:p-5 rounded-2xl shadow-sm border border-slate-200">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight lg:pl-2">Marketplace Deals</h1>
              <p className="mt-1 text-sm font-medium text-slate-500 lg:pl-2">
                {loading ? 'Loading live catalog...' : `${formatCountLabel(total)} products available`}
              </p>
            </div>

            <div className="relative w-full md:w-96 group">
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="w-full pl-11 pr-4 py-3 rounded-xl border-2 border-slate-100 bg-slate-50 focus:bg-white focus:ring-4 focus:ring-blue-100/50 focus:border-blue-400 outline-none transition-all font-semibold text-slate-700 placeholder-slate-400 shadow-inner group-hover:border-slate-200"
              />
              <svg className="w-5 h-5 text-slate-400 absolute left-4 top-3.5 group-hover:text-blue-500 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <div className="flex flex-col lg:flex-row gap-8">
            <div className="w-full lg:w-[280px] flex-shrink-0">
              <CategorySidebar />
            </div>

            <div className="flex-1">
              {error ? (
                <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
                  {error}
                </div>
              ) : loading ? (
                <div className="rounded-2xl border border-slate-200 bg-white px-6 py-12 text-center text-slate-500">
                  Loading marketplace products from the database...
                </div>
              ) : (
                <ProductGrid products={products} />
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
