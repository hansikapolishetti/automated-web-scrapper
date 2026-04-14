import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import ProductGallery from '../components/ProductGallery';
import ProductDetails from '../components/ProductDetails';
import StorePriceList from '../components/StorePriceList';
import ComparisonWorkspace from '../components/compare/ComparisonWorkspace';
import { mockProductDetail } from '../data/productMockData';

export default function ProductPage() {
  const { productId } = useParams();
  const product = mockProductDetail;

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [productId]);

  return (
    <div className="min-h-screen flex flex-col font-sans bg-slate-50">
      <Navbar forceDarkText />

      <main className="flex-grow pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-6">


          {/* Two-column layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">

            {/* ── LEFT: Product Info ── */}
            <div className="flex flex-col gap-8">

              {/* Gallery — keep its own visual treatment */}
              <ProductGallery images={product.images} title={product.title} />

              {/* Details */}
              <div className="border-t border-slate-200 pt-6">
                <ProductDetails product={product} />
              </div>

              {/* Store Prices */}
              <div className="border-t border-slate-200 pt-2">
                <StorePriceList stores={product.stores} />
              </div>

            </div>

            {/* ── RIGHT: Comparison — sticky ── */}
            <div className="lg:sticky lg:top-8" style={{ maxHeight: 'calc(100vh - 4rem)' }}>
              <ComparisonWorkspace product={product} />
            </div>

          </div>

        </div>
      </main>
    </div>
  );
}
