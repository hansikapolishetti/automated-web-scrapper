import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import ProductDetails from '../components/ProductDetails';
import StorePriceList from '../components/StorePriceList';
import ComparisonWorkspace from '../components/compare/ComparisonWorkspace';
import { mockProductDetail } from '../data/productMockData';

export default function ProductPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const product = mockProductDetail;

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [productId]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar />
      
      <main className="flex-grow py-8">
        <div className="max-w-7xl mx-auto px-6">
          
          <button onClick={() => navigate(-1)} className="mb-6 flex items-center text-sm font-bold text-slate-500 hover:text-slate-900 transition-colors">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7" /></svg>
            Back to results
          </button>

          {/* Master Layout Container: Bulletproof Flexbox Split */}
          <div className="flex flex-col lg:flex-row gap-10 items-start">
            
            {/* LEFT COLUMN: Single Unified Product Card (7/12 Width) */}
            <div className="w-full lg:w-7/12">
              <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 lg:p-8 space-y-6">
                <ProductGallery images={product.images} title={product.title} />
                <ProductDetails product={product} />
                <div className="border-t border-slate-100 pt-4">
                  <StorePriceList stores={product.stores} />
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN: Comparison Workspace Tabs (5/12 Width + Sticky) */}
            <div className="w-full lg:w-5/12 flex flex-col gap-10 lg:sticky lg:top-8">
              <ComparisonWorkspace product={product} />
            </div>

          </div>

        </div>
      </main>
    </div>
  );
}
