const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(payload.detail || payload.error || 'Request failed');
  }

  return payload;
}

export function fetchProducts({ query = '', category = 'all', limit = 24 } = {}) {
  const searchParams = new URLSearchParams();
  if (query) searchParams.set('query', query);
  if (category) searchParams.set('category', category);
  searchParams.set('limit', String(limit));

  return fetchJson(`/products?${searchParams.toString()}`);
}

export function fetchCategoryCounts(categories = []) {
  return Promise.all(
    categories.map((category) =>
      fetchProducts({ category, limit: 1 }).then((response) => ({
        category,
        total: response.total ?? 0,
      })),
    ),
  );
}

export function fetchProduct(productId) {
  return fetchJson(`/products/${encodeURIComponent(productId)}`);
}

export function fetchCompare({ query = '', category = 'laptops', limit = 12 } = {}) {
  const searchParams = new URLSearchParams();
  if (query) searchParams.set('query', query);
  if (category) searchParams.set('category', category);
  searchParams.set('limit', String(limit));

  return fetchJson(`/compare?${searchParams.toString()}`);
}
