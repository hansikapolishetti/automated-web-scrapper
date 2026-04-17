
require("dotenv").config();const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');
const { connectToDatabase, getCollection } = require('./db');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Helper to run Python comparison logic
function runPythonComparison(query, category = 'laptops', limit = 20) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, 'compare_products.py');
    const child = spawn('python', [
      pythonScript,
      '--query', query,
      '--category', category,
      '--limit', String(limit)
    ]);

    let data = '';
    let errorData = '';

    child.stdout.on('data', (chunk) => {
      data += chunk.toString();
    });

    child.stderr.on('data', (chunk) => {
      errorData += chunk.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(`Python script failed with code ${code}: ${errorData}`));
      }
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error(`Failed to parse Python output: ${err.message}`));
      }
    });
  });
}

// Routes

// 1. GET /api/products - List products (grouped by slug)
app.get('/api/products', async (req, res) => {
  try {
    const category = req.query.category || 'laptops';
    const limit = parseInt(req.query.limit) || 24;
    const collection = getCollection(category);

    // Grouping by slug to return unique products
    const products = await collection.aggregate([
      { $match: { slug: { $exists: true } } },
      { $sort: { last_seen_at: -1 } },
      {
        $group: {
          _id: '$slug',
          name: { $first: '$name' },
          brand: { $first: '$brand' },
          image: { $first: '$image' },
          images: { $first: '$images' },
          price: { $min: '$price' }, // Show lowest price
          original_price: { $first: '$original_price' },
          rating: { $first: '$rating' },
          category: { $first: '$category' },
          slug: { $first: '$slug' }
        }
      },
      { $limit: limit }
    ]).toArray();

    const total = (await collection.distinct('slug')).length;
    res.json({ products, total });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch products', detail: error.message });
  }
});

// 2. GET /api/products/:slug - Product detail (aggregated stores)
app.get('/api/products/:slug', async (req, res) => {
  try {
    const { slug } = req.params;
    const categories = ['laptops', 'mobiles', 'tvs', 'audio'];
    let productVariants = [];

    // Search across categories if needed, but usually we know the category or check all
    for (const cat of categories) {
      const col = getCollection(cat);
      const variants = await col.find({ slug }).toArray();
      if (variants.length > 0) {
        productVariants = variants;
        break;
      }
    }

    if (productVariants.length === 0) {
      return res.status(404).json({ error: 'Product not found' });
    }

    // Aggregate data for the UI
    const first = productVariants[0];
    const product = {
      title: first.name,
      slug: first.slug,
      brand: first.brand,
      images: first.images || [first.image],
      specifications: first.specifications || {},
      category: first.category,
      rating: first.rating,
      review_count: first.review_count,
      description: first.source_text || '',
      stores: productVariants.map(v => ({
        name: v.website === 'amazon' ? 'Amazon' : v.website === 'flipkart' ? 'Flipkart' : v.website,
        price: v.price,
        oldPrice: v.original_price,
        link: v.link,
        rating: v.rating,
        review_count: v.review_count,
        logo: v.website === 'amazon' ? '/images/amazon-logo.png' : '/images/flipkart-logo.png'
      }))
    };

    res.json(product);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch product details', detail: error.message });
  }
});

// 3. GET /api/products/:slug/prices - Price comparison (uses Python logic)
app.get('/api/products/:slug/prices', async (req, res) => {
  try {
    const { slug } = req.params;
    // We use the slug as a name query for the comparison logic
    const query = slug.replace(/-/g, ' ');
    const results = await runPythonComparison(query);
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: 'Failed to compare prices', detail: error.message });
  }
});

// 4. GET /api/products/:slug/similar - Similar products
app.get('/api/products/:slug/similar', async (req, res) => {
  try {
    const { slug } = req.params;
    const category = req.query.category || 'laptops';
    const collection = getCollection(category);

    const product = await collection.findOne({ slug });
    if (!product) return res.json([]);

    const similar = await collection.find({
      category: product.category,
      brand: product.brand,
      slug: { $ne: slug }
    }).limit(6).toArray();

    res.json(similar);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch similar products', detail: error.message });
  }
});

// 5. GET /api/categories - Available categories
app.get('/api/categories', async (req, res) => {
  try {
    const categories = ['laptops', 'mobiles', 'tvs', 'audio'];
    const counts = await Promise.all(categories.map(async (cat) => {
      const col = getCollection(cat);
      const uniqueSlugs = await col.distinct('slug');
      const count = uniqueSlugs.length;
      return { id: cat, name: cat.charAt(0).toUpperCase() + cat.slice(1), count };
    }));
    res.json(counts);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch categories', detail: error.message });
  }
});

// 6. GET /api/search?q=query - Search (uses Python logic)
app.get('/api/search', async (req, res) => {
  try {
    const query = req.query.q || '';
    const category = req.query.category || 'laptops';
    if (!query) return res.json({ products: [], total: 0 });

    const results = await runPythonComparison(query, category);
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: 'Search failed', detail: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK' });
});

// Start Server
connectToDatabase().then(() => {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Express API running on http://localhost:${PORT}`);
  });
}).catch(err => {
  console.error('Failed to connect to database:', err);
  process.exit(1);
});
