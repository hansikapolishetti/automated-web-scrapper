import { startTransition, useDeferredValue, useEffect, useMemo, useRef, useState } from "react";

const API_URL = "http://localhost:5000/compare";
const MATCH_TABS = [
  { id: "all", label: "All Comparable" },
  { id: "exact", label: "Exact Match" },
  { id: "variant", label: "Variant Match" },
  { id: "similar_specs", label: "Similar Specs" },
  { id: "best_value", label: "Best Deals" },
];
const CATEGORIES = [
  {
    id: "laptops",
    title: "Laptops",
    tagline: "Live now",
    description: "Matched Amazon and Flipkart listings with comparison tiers and better-deal callouts.",
    eyebrow: "Laptops",
    heroText: "Search a laptop name or paste a product link to compare Amazon and Flipkart faster.",
    searchPlaceholder: "Search laptop model or paste Amazon / Flipkart link",
    workspaceTitle: "Matched laptop comparisons",
    workspaceText:
      "Focus on strong overlap first. Exact matches, family-level variants, and broader spec-comparable pairs all stay in one workspace.",
    laneLabel: "Laptop lane",
    statsSummary: "Primary laptop pairs ready for UI",
    exactSummary: "Near-identical listings on both stores",
    variantSummary: "Same family with variant-level differences",
    bestValueSummary: "Pairs where one site is clearly cheaper",
    quickBrands: ["asus", "hp", "lenovo", "dell", "acer", "msi"],
    specFields: ["processor", "ram", "storage", "screen_size", "gpu"],
    live: true,
  },
  {
    id: "mobiles",
    title: "Mobiles",
    tagline: "Live now",
    description: "Compare Amazon and Flipkart mobile listings by chipset, RAM, storage, battery, camera, and price.",
    eyebrow: "Mobiles",
    heroText: "Search a phone model or paste a product link to compare mobile deals across Amazon and Flipkart.",
    searchPlaceholder: "Search mobile model or paste Amazon / Flipkart link",
    workspaceTitle: "Matched mobile comparisons",
    workspaceText:
      "Compare phone listings with stronger mobile-aware matching across brand, model family, RAM, storage, battery, camera, network, and price.",
    laneLabel: "Mobile lane",
    statsSummary: "Primary mobile pairs ready for UI",
    exactSummary: "Strong phone listing overlaps across both stores",
    variantSummary: "Same phone family with small configuration differences",
    bestValueSummary: "Phones where one store is notably cheaper",
    quickBrands: ["samsung", "iphone", "oneplus", "vivo", "oppo", "realme"],
    specFields: ["processor", "ram", "storage", "display_size", "camera", "battery", "network"],
    live: true,
  },
  {
    id: "audio",
    title: "Audio",
    tagline: "Later",
    description: "Headphones and earbuds with price gaps, offer tracking, and overlap detection.",
    live: false,
  },
];

const CATEGORY_LOOKUP = Object.fromEntries(CATEGORIES.map((category) => [category.id, category]));
const SHORT_QUERY_ALLOWLIST = new Set(
  CATEGORIES.flatMap((category) => category.quickBrands || []).filter((brand) => brand.length < 3),
);

function activeCategoryConfig(categoryId) {
  return CATEGORY_LOOKUP[categoryId] || CATEGORY_LOOKUP.laptops;
}

function extractQueryFromInput(input) {
  const value = input.trim();
  if (!value) {
    return "";
  }

  const lowerValue = value.toLowerCase();
  if (SHORT_QUERY_ALLOWLIST.has(lowerValue)) {
    return lowerValue;
  }

  try {
    const parsed = new URL(value);
    const rawPath = parsed.pathname
      .replace(/\/(dp|p)\/[^/]+/gi, " ")
      .replace(/\/+/g, " ")
      .replace(/-/g, " ");

    const usefulTokens = rawPath
      .split(/\s+/)
      .map((token) => token.trim())
      .filter(Boolean)
      .filter((token) => /[a-z]/i.test(token))
      .filter((token) => token.length > 2)
      .filter((token) => !/^(dp|p|ref|itm[a-z0-9]+|b0[a-z0-9]+)$/i.test(token));

    const extracted = usefulTokens.slice(0, 6).join(" ").trim();
    if (extracted.length < 3) {
      return "";
    }
    return extracted;
  } catch {
    if (value.length < 3) {
      return "";
    }
    return value;
  }
}

function formatPrice(value) {
  if (typeof value !== "number") {
    return "Unknown";
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatRating(value) {
  if (typeof value !== "number") {
    return null;
  }
  return value.toFixed(1);
}

function isKnownValue(value) {
  return value !== null && value !== undefined && value !== "" && value !== "Unknown" && value !== "Unavailable";
}

function specBadge(label, value) {
  if (!isKnownValue(value)) {
    return null;
  }

  return (
    <span className="spec-pill" key={`${label}-${value}`}>
      {value}
    </span>
  );
}

function differenceTone(status) {
  if (status === "different") return "difference-card different";
  if (status === "same") return "difference-card same";
  return "difference-card unknown";
}

function ProductPane({ siteLabel, product, accentClass, specFields }) {
  const rating = formatRating(product.rating);
  const metaItems = [
    product.discount_percent > 0 ? `${product.discount_percent}% off` : null,
    rating ? `Rating ${rating}` : null,
    product.review_count > 0 ? `${product.review_count} reviews` : null,
  ].filter(Boolean);

  return (
    <article className={`product-pane ${accentClass}`}>
      <div className="site-row">
        <span className="site-dot" />
        <span>{siteLabel}</span>
      </div>
      <div className="product-top">
        <div className="image-shell">
          <img
            src={product.image}
            alt={product.name}
            onError={(event) => {
              event.currentTarget.style.opacity = "0";
            }}
          />
        </div>
        <div className="product-copy">
          <h3>{product.name}</h3>
          <div className="price-row">
            <strong>{formatPrice(product.price)}</strong>
            {product.original_price > product.price ? (
              <span className="strikethrough">{formatPrice(product.original_price)}</span>
            ) : null}
          </div>
          {metaItems.length ? (
            <div className="meta-row">
              {metaItems.map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
      <div className="spec-pill-row">
        {specFields.map((field) => specBadge(field, product[field]))}
      </div>
      <a className="details-link" href={product.link} target="_blank" rel="noreferrer">
        View product
      </a>
    </article>
  );
}

function formatDifferenceValue(field, value) {
  if (typeof value === "number" && ["price", "original_price", "discount_amount"].includes(field)) {
    return formatPrice(value);
  }
  return value;
}

function ComparisonCard({ item, categoryConfig }) {
  const differenceEntries = Object.entries(item.differences || {}).filter(([field, value]) => {
    if (field === "model_code") {
      return false;
    }
    const leftKnown = isKnownValue(value.amazon);
    const rightKnown = isKnownValue(value.flipkart);
    return leftKnown && rightKnown;
  });

  return (
    <article className="comparison-card">
      <div className="comparison-head">
        <div>
          <div className="match-badges">
            <span className={`confidence-badge ${item.match_type}`}>{item.confidence_label}</span>
            <span className="score-badge">Score {item.score}</span>
          </div>
          <h2>{item.amazon.brand} comparison</h2>
          <p className="reason-line">{item.match_reasons.join(" • ")}</p>
        </div>
        <div className="deal-box">
          <span>{item.cheaper_site === "same" ? "Same price" : `${item.cheaper_site} is cheaper`}</span>
          <strong>{formatPrice(item.price_difference)}</strong>
        </div>
      </div>

      <div className="pane-grid">
        <ProductPane
          siteLabel="Amazon"
          product={item.amazon}
          accentClass="amazon-pane"
          specFields={categoryConfig.specFields}
        />
        <ProductPane
          siteLabel="Flipkart"
          product={item.flipkart}
          accentClass="flipkart-pane"
          specFields={categoryConfig.specFields}
        />
      </div>

      <div className="differences-block">
        <div className="block-head">
          <h4>What differs</h4>
          <span>{differenceEntries.length} tracked fields</span>
        </div>
        <div className="difference-grid">
          {differenceEntries.length ? (
            differenceEntries.map(([field, value]) => (
              <div className={differenceTone(value.status)} key={field}>
                <small>{field.replaceAll("_", " ")}</small>
                <strong>{value.status}</strong>
                <span>Amazon: {formatDifferenceValue(field, value.amazon)}</span>
                <span>Flipkart: {formatDifferenceValue(field, value.flipkart)}</span>
              </div>
            ))
          ) : (
            <div className="difference-card same">
              <small>comparison</small>
              <strong>No important differences</strong>
              <span>These listings align on tracked fields.</span>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}

function App() {
  const [theme, setTheme] = useState("light");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [searchInput, setSearchInput] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState("Pick a category to start comparing.");
  const [loading, setLoading] = useState(false);
  const workspaceRef = useRef(null);
  const categoryConfig = activeCategoryConfig(selectedCategory || "laptops");

  const deferredQuery = useDeferredValue(extractQueryFromInput(searchInput));

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.title = "PriceScout";
  }, [theme]);

  useEffect(() => {
    if (!selectedCategory || !activeCategoryConfig(selectedCategory).live) {
      setPayload(null);
      setLoading(false);
      setStatus("Pick a category to start comparing.");
      return;
    }

    if (!deferredQuery) {
      setPayload(null);
      setLoading(false);
      setStatus("Type at least 3 characters, choose a brand, or paste a product link.");
      return;
    }

    const controller = new AbortController();
    const queryString = `?query=${encodeURIComponent(deferredQuery)}&category=${encodeURIComponent(selectedCategory)}&limit=12`;

    setLoading(true);
    setStatus("Scanning comparable products...");

    fetch(`${API_URL}${queryString}`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Comparison API failed");
        }
        return response.json();
      })
      .then((data) => {
        setPayload(data);
        if ((data.all_comparable_total || 0) === 0) {
          if ((data.amazon_source_total || 0) === 0 && (data.flipkart_source_total || 0) === 0) {
            setStatus("No products found for this search.");
          } else {
            setStatus("No cross-store comparable products found yet for this search.");
          }
        } else {
          setStatus("Comparison data ready");
        }
      })
      .catch((error) => {
        if (error.name === "AbortError") {
          return;
        }
        setStatus("Could not load comparison data");
        setPayload(null);
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [deferredQuery, selectedCategory]);

  const collections = useMemo(() => {
    if (!payload) {
      return {
        all: [],
        exact: [],
        variant: [],
        similar_specs: [],
        best_value: [],
      };
    }

    return {
      all: payload.all_comparable_matches || [],
      exact: payload.exact_matches || [],
      variant: payload.variant_matches || [],
      similar_specs: payload.spec_comparable_matches || [],
      best_value: payload.best_value_matches || [],
    };
  }, [payload]);

  const visibleItems = collections[activeTab] || [];

  function openCategory(categoryId, presetQuery = "") {
    startTransition(() => {
      setSelectedCategory(categoryId);
      setActiveTab("all");
      if (presetQuery) {
        setSearchInput(presetQuery);
      }
    });

    requestAnimationFrame(() => {
      workspaceRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">ps</div>
          <div>
            <strong>PriceScout</strong>
            <span>Smarter price comparison</span>
          </div>
        </div>
        <nav className="topnav">
          <a href="#hero">Home</a>
          <a href="#search">Search</a>
          <a href="#categories">Categories</a>
          <a href="#workspace">Compare</a>
        </nav>
        <button
          className="theme-toggle"
          onClick={() => setTheme((current) => (current === "light" ? "dark" : "light"))}
          type="button"
        >
          {theme === "light" ? "Dark mode" : "Light mode"}
        </button>
      </header>

      <section className="hero-stage" id="hero">
        <div className="hero-panel">
          <div className="hero-copy">
            <p className="hero-kicker">Compare prices across top stores</p>
            <h1>Find the better store price before you buy.</h1>
            <p className="hero-text">{categoryConfig.heroText}</p>
            <div className="hero-actions">
              <button className="primary-action" onClick={() => openCategory("laptops")} type="button">
                Start comparing
              </button>
              <a className="ghost-action" href="#categories">
                Browse categories
              </a>
            </div>
          </div>
          <div className="hero-preview" id="search">
            <div className="preview-search">
              <span>Search by model, brand, or product link</span>
              <div className="preview-search-row">
                <input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder={categoryConfig.searchPlaceholder}
                />
                <button onClick={() => openCategory(selectedCategory || "laptops")} type="button">
                  Search
                </button>
              </div>
            </div>
            <div className="hero-highlights">
              <span>Amazon + Flipkart</span>
              <span>Matched comparisons</span>
              <span>Best deal signals</span>
            </div>
          </div>
        </div>
      </section>

      <section className="category-stage" id="categories">
        <div className="section-heading">
          <p className="eyebrow">Categories</p>
          <h2>Pick what you want to compare.</h2>
        </div>
        <div className="category-grid">
          {CATEGORIES.map((category) => (
            <article
              className={selectedCategory === category.id ? "category-card active" : "category-card"}
              key={category.id}
            >
              <div className="category-head">
                <span>{category.tagline}</span>
                <strong>{category.title}</strong>
              </div>
              <p>{category.description}</p>
              {category.live ? (
                <button className="category-action" onClick={() => openCategory(category.id)} type="button">
                  Slide into workspace
                </button>
              ) : (
                <button className="category-action disabled" type="button">
                  Coming soon
                </button>
              )}
            </article>
          ))}
        </div>
      </section>

      <section
        className={selectedCategory && categoryConfig.live ? "workspace-shell open" : "workspace-shell"}
        id="workspace"
        ref={workspaceRef}
      >
        <aside className="workspace-rail">
          <span className="rail-pill">{selectedCategory && categoryConfig.live ? categoryConfig.laneLabel : "Workspace locked"}</span>
          <h3>{selectedCategory && categoryConfig.live ? "Comparison workspace" : "Choose a category first"}</h3>
          <p>
            {selectedCategory && categoryConfig.live
              ? "Use brand shortcuts, direct text search, or pasted product links to open the matched comparison feed."
              : "The comparison board stays hidden until a category is selected, so the homepage can stay discovery-first."}
          </p>
          <div className="rail-brand-list">
            {categoryConfig.quickBrands?.map((brand) => (
              <button
                className={brand === searchInput.trim().toLowerCase() ? "rail-chip active" : "rail-chip"}
                key={brand}
                onClick={() => {
                  if (!selectedCategory || !categoryConfig.live) {
                    openCategory(categoryConfig.id, brand);
                    return;
                  }
                  startTransition(() => {
                    setSearchInput(brand);
                    setActiveTab("all");
                  });
                }}
                type="button"
              >
                {brand}
              </button>
            ))}
          </div>
        </aside>

        <div className="workspace-panel">
          <div className="workspace-head">
            <div>
              <p className="eyebrow">{categoryConfig.eyebrow}</p>
              <h2>{categoryConfig.workspaceTitle}</h2>
              <p className="workspace-text">{categoryConfig.workspaceText}</p>
            </div>
            <label className="workspace-search">
              <span>Search inside {categoryConfig.eyebrow.toLowerCase()} comparisons</span>
              <input
                value={searchInput}
                onChange={(event) => setSearchInput(event.target.value)}
                placeholder="Type at least 3 characters or paste a product link"
              />
            </label>
          </div>

          <section className="stats-grid">
            <div className="stat-card">
              <span>All comparable</span>
              <strong>{payload?.all_comparable_total ?? 0}</strong>
              <small>{categoryConfig.statsSummary}</small>
            </div>
            <div className="stat-card">
              <span>Exact matches</span>
              <strong>{payload?.exact_total ?? 0}</strong>
              <small>{categoryConfig.exactSummary}</small>
            </div>
            <div className="stat-card">
              <span>Variant matches</span>
              <strong>{payload?.variant_total ?? 0}</strong>
              <small>{categoryConfig.variantSummary}</small>
            </div>
            <div className="stat-card">
              <span>Best value</span>
              <strong>{payload?.best_value_total ?? 0}</strong>
              <small>{categoryConfig.bestValueSummary}</small>
            </div>
          </section>

          <section className="toolbar">
            <div className="tab-row">
              {MATCH_TABS.map((tab) => (
                <button
                  className={activeTab === tab.id ? "tab active" : "tab"}
                  key={tab.id}
                  onClick={() => {
                    startTransition(() => setActiveTab(tab.id));
                  }}
                  type="button"
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="toolbar-status">
              <strong>{status}</strong>
              <span>{loading ? "Refreshing..." : `${visibleItems.length} visible cards`}</span>
            </div>
          </section>

          <section className="results-shell">
            {visibleItems.length ? (
              visibleItems.map((item, index) => (
                <ComparisonCard
                  item={item}
                  categoryConfig={categoryConfig}
                  key={`${item.amazon.link}-${item.flipkart.link}-${index}`}
                />
              ))
            ) : (
              <div className="empty-state">
                <h2>No comparison cards in this bucket yet.</h2>
                <p>
                  {!selectedCategory || !categoryConfig.live
                    ? "Pick a live category lane to open the board."
                    : "Try another brand, or switch to All Comparable to see the broader match set."}
                </p>
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}

export default App;





