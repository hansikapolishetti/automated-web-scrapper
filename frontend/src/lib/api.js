const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.detail || payload.error || 'Request failed');
  }

  return payload;
}

export function fetchProducts({ query = '', category = 'laptops', brands = [], limit = 24 } = {}) {
  const searchParams = new URLSearchParams();
  if (query) searchParams.set('query', query);
  if (category) searchParams.set('category', category);
  if (brands && brands.length > 0) {
    searchParams.set('brands', brands.join(','));
  }
  searchParams.set('limit', String(limit));

  return fetchJson(`/products?${searchParams.toString()}`);
}

export function fetchCategories() {
  return fetchJson('/categories');
}

export function fetchBrands(category = 'laptops') {
  return fetchJson(`/brands?category=${category}`);
}

export function fetchProduct(slug) {
  return fetchJson(`/products/${encodeURIComponent(slug)}`);
}

export function fetchPrices(slug) {
  return fetchJson(`/products/${encodeURIComponent(slug)}/prices`);
}

export function fetchCompareById(slug) {
  return fetchJson(`/compare?id=${encodeURIComponent(slug)}`);
}

export function fetchSimilar(slug, category = 'laptops') {
  return fetchJson(`/products/${encodeURIComponent(slug)}/similar?category=${category}`);
}

export function fetchSearch(query, category = 'laptops') {
  const searchParams = new URLSearchParams();
  searchParams.set('q', query);
  searchParams.set('category', category);
  return fetchJson(`/search?${searchParams.toString()}`);
}

// Compatibility layer for older pages if needed
export function fetchCompare({ query = '', category = 'laptops', limit = 12 } = {}) {
  const searchParams = new URLSearchParams();
  if (query) searchParams.set('q', query);
  if (category) searchParams.set('category', category);
  searchParams.set('limit', String(limit));

  return fetchJson(`/search?${searchParams.toString()}`);
}
