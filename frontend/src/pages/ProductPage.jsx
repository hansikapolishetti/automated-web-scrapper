import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import ProductDetails from '../components/ProductDetails';
import StorePriceList from '../components/StorePriceList';
import ComparisonWorkspace from '../components/compare/ComparisonWorkspace';
import { fetchProduct, fetchPrices } from '../lib/api';

export default function ProductPage() {
  const { productId: slug } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.scrollTo(0, 0);
    
    async function loadData() {
      setLoading(true);
      setError(null);
      try {
        const productData = await fetchProduct(slug);
        
        // Also fetch comparison data (prices from other stores/similar products)
        let comparisonData = { exact_matches: [], variant_matches: [], spec_comparable_matches: [] };
        try {
          comparisonData = await fetchPrices(slug);
        } catch (compErr) {
          console.error('Failed to load comparison data:', compErr);
        }

        const enrichedProduct = {
          ...productData,
          exactMatches: comparisonData.exact_matches || [],
          variantMatches: comparisonData.variant_matches || [],
          similarSpecs: comparisonData.spec_comparable_matches || [],
        };

        setProduct(enrichedProduct);
        document.title = `${productData.title} | PriceScout`;
      } catch (err) {
        console.error('Failed to load product:', err);
        setError('Product not found or failed to load.');
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col font-sans bg-slate-50">
        <Navbar forceDarkText />
        <div className="flex-grow flex items-center justify-center">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen flex flex-col font-sans bg-slate-50">
        <Navbar forceDarkText />
        <div className="flex-grow flex flex-col items-center justify-center p-6 text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Oops!</h2>
          <p className="text-slate-600">{error || 'Product not found'}</p>
          <a href="/" className="mt-6 px-6 py-3 bg-cyan-600 text-white rounded-xl font-bold">Back to Home</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-50">
      <Navbar forceDarkText />

      <main className="flex-grow pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
            <div className="flex flex-col gap-8">
              <ProductGallery images={product.images} title={product.title} />
              <div className="border-t border-slate-200 pt-6">
                <ProductDetails product={product} />
              </div>
              <div className="border-t border-slate-200 pt-2">
                <StorePriceList stores={product.stores} />
              </div>
            </div>
            <div className="lg:sticky lg:top-8" style={{ maxHeight: 'calc(100vh - 4rem)' }}>
              <ComparisonWorkspace product={product} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
