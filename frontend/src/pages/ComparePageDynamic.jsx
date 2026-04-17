import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import SearchResultsHeaderDynamic from '../components/compare/SearchResultsHeaderDynamic';
import MatchSectionDynamic from '../components/compare/MatchSectionDynamic';
import { fetchCompare } from '../lib/api';
import { normalizeCompareSection } from '../lib/productAdapters';

export default function ComparePageDynamic() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const category = searchParams.get('category') || 'laptops';

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    window.scrollTo(0, 0);
    document.title = `Compare ${query} | PriceScout`;

    let isActive = true;

    const loadCompareData = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await fetchCompare({ query, category, limit: 12 });
        if (isActive) {
          setData({
            total: response.all_comparable_total ?? 0,
            highConfidence: normalizeCompareSection(response.exact_matches || []),
            variants: normalizeCompareSection(response.variant_matches || []),
            similarSpecs: normalizeCompareSection(response.spec_comparable_matches || []),
            possibleMatches: normalizeCompareSection(response.possible_matches || []),
          });
        }
      } catch (fetchError) {
        if (isActive) {
          setData(null);
          setError(fetchError.message || 'Failed to load comparisons');
        }
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    loadCompareData();

    return () => {
      isActive = false;
    };
  }, [category, query]);

  return (
    <div className="min-h-screen bg-slate-50/50 font-sans text-slate-900 antialiased flex flex-col">
      <Navbar forceDarkText />
      <SearchResultsHeaderDynamic query={query} total={data?.total || 0} category={category} />

      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 opacity-70 animate-fade-in-up">
            <div className="w-16 h-16 border-[5px] border-slate-200 border-t-cyan-500 rounded-full animate-spin mb-6" />
            <h2 className="text-2xl font-black text-slate-400">Scanning verified stores...</h2>
            <p className="text-slate-400 font-medium mt-2 tracking-widest text-sm uppercase">Matching Specifications</p>
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
            {error}
          </div>
        ) : data ? (
          <div className="space-y-16">
            <section className="rounded-3xl border border-slate-200 bg-white p-6 sm:p-8 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="max-w-3xl">
                  <p className="text-xs font-bold uppercase tracking-[0.25em] text-cyan-600">How To Read These Results</p>
                  <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-900">We group comparisons by buyer confidence</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    Exact matches are safest for direct price checks. Variant matches stay in the same product family but may change RAM,
                    storage, or bundled features. Similar specs are strong alternatives when the exact model is not available.
                  </p>
                </div>
                <div className="grid gap-3 text-sm text-slate-600 sm:grid-cols-3 lg:max-w-xl">
                  <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3">
                    <p className="font-bold text-emerald-800">Exact</p>
                    <p className="mt-1">Same model. Compare price with confidence.</p>
                  </div>
                  <div className="rounded-2xl border border-indigo-200 bg-indigo-50 px-4 py-3">
                    <p className="font-bold text-indigo-800">Variant</p>
                    <p className="mt-1">Same family. Check changed specs before buying.</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                    <p className="font-bold text-slate-800">Alternative</p>
                    <p className="mt-1">Different model, but close features and value.</p>
                  </div>
                </div>
              </div>
            </section>

            <MatchSectionDynamic
              level={1}
              title="Exact Matches"
              description="Same model and same core product. This is the best section for direct price comparison across stores."
              products={data.highConfidence}
            />

            <div className="border-t border-slate-200" />

            <MatchSectionDynamic
              level={2}
              title="Variant Matches"
              description="Same product family, but one or more configurations differ. Compare carefully before treating these as the same item."
              products={data.variants}
            />

            <div className="border-t border-slate-200" />

            <MatchSectionDynamic
              level={3}
              title="Similar Specs"
              description="Not the same model, but close enough on core specs to be useful as a buying alternative."
              products={data.similarSpecs}
            />

            <div className="border-t border-slate-200" />

            <MatchSectionDynamic
              level={4}
              title="Possible Matches & Alternatives"
              description="Looser matches such as nearby generations or comparable alternatives. Good for broader budget and value discovery."
              products={data.possibleMatches}
            />
          </div>
        ) : null}
      </main>

      <footer className="py-12 bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 text-center text-slate-500 text-sm font-medium flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-xl mb-4">P</div>
          <p>&copy; {new Date().getFullYear()} PriceScout. Assisting your market research.</p>
        </div>
      </footer>
    </div>
  );
}
