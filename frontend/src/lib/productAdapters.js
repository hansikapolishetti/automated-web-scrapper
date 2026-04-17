const CATEGORY_LABELS = {
  laptops: 'Laptops',
  mobiles: 'Mobiles',
  tvs: 'TVs',
  audio: 'Audio',
  all: 'Marketplace Deals',
};
const CATEGORY_ALIASES = {
  laptop: 'laptops',
  laptops: 'laptops',
  mobile: 'mobiles',
  mobiles: 'mobiles',
  tv: 'tvs',
  tvs: 'tvs',
  audio: 'audio',
  all: 'all',
};

const FALLBACK_IMAGE = 'https://placehold.co/600x600?text=No+Image';
const FIELD_LABELS = {
  model_code: 'Model',
  screen_size: 'Screen',
  gpu: 'GPU',
  price: 'Price',
  original_price: 'MRP',
  discount_percent: 'Discount',
  rating: 'Rating',
  review_count: 'Reviews',
  processor: 'Processor',
  ram: 'RAM',
  storage: 'Storage',
  display_size: 'Display',
  battery: 'Battery',
  camera: 'Camera',
  network: 'Network',
  resolution: 'Resolution',
  display_type: 'Panel',
  smart_tv: 'Smart TV',
  refresh_rate: 'Refresh Rate',
  audio_output: 'Audio',
  operating_system: 'OS',
};

export function normalizeCategoryKey(category) {
  const normalizedCategory = String(category || '').trim().toLowerCase();
  return CATEGORY_ALIASES[normalizedCategory] || normalizedCategory || 'all';
}

export function getCategoryLabel(category) {
  const normalizedCategory = normalizeCategoryKey(category);
  return CATEGORY_LABELS[normalizedCategory] || category?.replace(/-/g, ' ') || 'Products';
}

export function formatPrice(value, fallback = 'Price unavailable') {
  if (value === null || value === undefined || value === '') {
    return fallback;
  }

  if (typeof value === 'string') {
    return value;
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
}

export function normalizeProductsForGrid(items = []) {
  return items.map((item) => ({
    id: item.id,
    title: item.title,
    price: item.formatted_price || formatPrice(item.price),
    oldPrice: item.formatted_old_price || formatPrice(item.old_price, ''),
    rating: item.rating ?? 'N/A',
    image: item.image || FALLBACK_IMAGE,
    store: item.store || 'Store',
    tag: item.discount_percent ? `${item.discount_percent}% off` : item.category,
    category: normalizeCategoryKey(item.category),
  }));
}

export function formatCountLabel(count) {
  const numericCount = Number(count) || 0;
  return new Intl.NumberFormat('en-IN').format(numericCount);
}

function buildCompareSpecs(product) {
  return product?.specs || {};
}

function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function titleSimilarity(left, right) {
  const leftTokens = new Set(normalizeText(left).split(' ').filter(Boolean));
  const rightTokens = new Set(normalizeText(right).split(' ').filter(Boolean));

  if (!leftTokens.size || !rightTokens.size) {
    return 0;
  }

  const intersection = [...leftTokens].filter((token) => rightTokens.has(token)).length;
  const union = new Set([...leftTokens, ...rightTokens]).size;
  return union ? intersection / union : 0;
}

function isRelevantMatch(product, match) {
  const currentStore = normalizeText(product.store_key);
  const currentSide = currentStore === 'amazon' ? match.amazon : match.flipkart;
  if (!currentSide) {
    return false;
  }

  const productTitle = product.title || product.name || '';
  const currentTitle = currentSide.name || '';
  const productBrand = normalizeText(product.brand);
  const currentBrand = normalizeText(currentSide.brand);
  const productModel = normalizeText(product.specs?.model || '');
  const currentModel = normalizeText(currentSide.model_code || '');

  if (productBrand || currentBrand) {
    if (!productBrand || !currentBrand || productBrand !== currentBrand) {
      return false;
    }
  }

  if (productModel && currentModel && productModel === currentModel) {
    return true;
  }

  let score = 0;
  if (productBrand && currentBrand && productBrand === currentBrand) score += 2;
  if (titleSimilarity(productTitle, currentTitle) >= 0.45) score += 4;
  if (normalizeText(product.specs?.ram) && normalizeText(product.specs?.ram) === normalizeText(currentSide.ram)) score += 1;
  if (normalizeText(product.specs?.storage) && normalizeText(product.specs?.storage) === normalizeText(currentSide.storage)) score += 1;
  if (normalizeText(product.specs?.processor) && normalizeText(product.specs?.processor) === normalizeText(currentSide.processor)) score += 1;

  return score >= 5;
}

export function selectRelevantComparePayload(product, comparePayload) {
  const filteredPayload = {
    ...comparePayload,
    exact_matches: (comparePayload?.exact_matches || []).filter((match) => isRelevantMatch(product, match)),
    variant_matches: (comparePayload?.variant_matches || []).filter((match) => isRelevantMatch(product, match)),
    spec_comparable_matches: (comparePayload?.spec_comparable_matches || []).filter((match) => isRelevantMatch(product, match)),
    possible_matches: (comparePayload?.possible_matches || []).filter((match) => isRelevantMatch(product, match)),
  };

  filteredPayload.exact_total = filteredPayload.exact_matches.length;
  filteredPayload.variant_total = filteredPayload.variant_matches.length;
  filteredPayload.spec_comparable_total = filteredPayload.spec_comparable_matches.length;
  filteredPayload.possible_total = filteredPayload.possible_matches.length;
  filteredPayload.all_comparable_total = (
    filteredPayload.exact_total
    + filteredPayload.variant_total
    + filteredPayload.spec_comparable_total
  );

  return filteredPayload;
}

function formatDifferenceValue(field, value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  if (field === 'price' || field === 'original_price') {
    return formatPrice(value);
  }

  return String(value);
}

function buildDifferenceChips(differences = {}) {
  return Object.entries(differences)
    .filter(([, difference]) => {
      if (!difference || difference.status === 'unknown') {
        return false;
      }

      return difference.amazon !== null
        && difference.amazon !== undefined
        && difference.amazon !== ''
        && difference.flipkart !== null
        && difference.flipkart !== undefined
        && difference.flipkart !== '';
    })
    .map(([field, difference]) => {
      const label = FIELD_LABELS[field] || field.replace(/_/g, ' ');
      const leftValue = formatDifferenceValue(field, difference.amazon);
      const rightValue = formatDifferenceValue(field, difference.flipkart);

      if (!leftValue || !rightValue || leftValue === rightValue) {
        return null;
      }

      return {
        key: field,
        label,
        summary: `${label}: ${leftValue} vs ${rightValue}`,
      };
    })
    .filter(Boolean);
}

function buildCompareStores(match) {
  const stores = [match.amazon, match.flipkart]
    .filter(Boolean)
    .map((store) => ({
      storeName: store.website ? store.website.charAt(0).toUpperCase() + store.website.slice(1) : 'Store',
      numericPrice: Number(store.price) || 0,
      price: formatPrice(store.price),
      link: store.link || '#',
    }));

  return stores.sort((left, right) => left.numericPrice - right.numericPrice);
}

export function normalizeCompareSection(matches = []) {
  return matches.map((match, index) => ({
    id: `${match.match_type || 'match'}-${index}-${match.amazon?.link || match.flipkart?.link || match.amazon?.name || match.flipkart?.name || 'product'}`,
    name: match.amazon?.name || match.flipkart?.name || 'Matched product',
    title: match.amazon?.name || match.flipkart?.name || 'Matched product',
    image: match.amazon?.image || match.flipkart?.image || 'https://placehold.co/600x600?text=No+Image',
    specs: buildCompareSpecs(match.amazon || match.flipkart),
    stores: buildCompareStores(match),
    rating: match.amazon?.rating || match.flipkart?.rating || 0,
    discount: match.price_difference ? `${formatPrice(match.price_difference)} diff` : null,
    differingFields: buildDifferenceChips(match.differences || {}),
    productId: null,
  }));
}

export function normalizeProductDetail(product, comparePayload) {
  const comparableMatches = [
    ...(comparePayload?.exact_matches || []),
    ...(comparePayload?.variant_matches || []),
    ...(comparePayload?.spec_comparable_matches || []),
  ];

  const storesByName = new Map();
  const addStore = (store) => {
    if (!store) return;
    const name = store.website ? store.website.charAt(0).toUpperCase() + store.website.slice(1) : 'Store';
    const key = name.toLowerCase();
    const numericPrice = Number(store.price) || 0;
    const next = {
      name,
      storeName: name,
      numericPrice,
      price: formatPrice(store.price),
      link: store.link || '#',
      inStock: true,
      delivery: 'Latest DB listing',
    };
    const current = storesByName.get(key);
    if (!current || numericPrice < current.numericPrice) {
      storesByName.set(key, next);
    }
  };

  addStore({
    website: product.store_key,
    price: product.price,
    link: product.link,
  });

  comparableMatches.forEach((match) => {
    addStore(match.amazon);
    addStore(match.flipkart);
  });

  return {
    id: product.id,
    title: product.title,
    rating: product.rating ?? 0,
    reviewsCount: product.reviews_count ?? 0,
    price: product.formatted_price || formatPrice(product.price),
    oldPrice: product.formatted_old_price || null,
    discount: product.discount_label || null,
    description: product.description,
    images: product.images?.length ? product.images : [product.image || FALLBACK_IMAGE],
    specs: product.specs || {},
    category: normalizeCategoryKey(product.category),
    stores: Array.from(storesByName.values()).sort((left, right) => left.numericPrice - right.numericPrice),
    primaryStoreLink: Array.from(storesByName.values()).sort((left, right) => left.numericPrice - right.numericPrice)[0]?.link || product.link || '#',
    exactMatches: normalizeCompareSection(comparePayload?.exact_matches || []),
    variantMatches: normalizeCompareSection(comparePayload?.variant_matches || []),
    similarSpecs: normalizeCompareSection(comparePayload?.spec_comparable_matches || []),
  };
}
