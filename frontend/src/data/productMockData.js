export const mockProductDetail = {
  id: 'iphone-15-pro-max',
  title: 'Apple iPhone 15 Pro Max (256GB) - Natural Titanium',
  rating: 4.8,
  reviewsCount: 12450,
  price: '₹1,56,900',
  oldPrice: '₹1,59,900',
  discount: '2% off',
  description: "Forged in titanium and featuring the groundbreaking A17 Pro chip, a customizable Action button, and the most powerful iPhone camera system ever. The iPhone 15 Pro Max redefines premium flagship experiences.",
  images: [
    'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=1000&q=80',
    'https://images.unsplash.com/photo-1604671368394-2240d0b1bb6c?auto=format&fit=crop&w=1000&q=80'
  ],
  specs: {
    ram: '8 GB',
    storage: '256 GB',
    display: '6.7 inch OLED',
    processor: 'A17 Pro Chip'
  },
  stores: [
    { name: 'Amazon', logo: 'A', price: '₹1,56,900', link: '#', inStock: true, delivery: 'Tomorrow' },
    { name: 'Flipkart', logo: 'F', price: '₹1,57,990', link: '#', inStock: true, delivery: 'In 2 Days' },
    { name: 'Croma', logo: 'C', price: '₹1,58,000', link: '#', inStock: false, delivery: 'Out of Stock' },
    { name: 'Reliance Digital', logo: 'R', price: '₹1,59,900', link: '#', inStock: true, delivery: 'In 3 Days' }
  ],
  exactMatches: [
    { title: 'Apple iPhone 15 Pro Max (256GB) - Blue Titanium', price: '₹1,56,900', image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=400&q=80', rating: 4.8 },
    { title: 'Apple iPhone 15 Pro Max (256GB) - Black Titanium', price: '₹1,56,900', image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=400&q=80', rating: 4.8 }
  ],
  variantMatches: [
    { title: 'Apple iPhone 15 Pro Max (512GB) - Natural Titanium', price: '₹1,76,900', image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=400&q=80', rating: 4.9 },
    { title: 'Apple iPhone 15 Pro Max (1TB) - Natural Titanium', price: '₹1,96,900', image: 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=400&q=80', rating: 4.7 }
  ],
  similarSpecs: [
    { title: 'Samsung Galaxy S24 Ultra (256GB) - Titanium Gray', price: '₹1,29,999', image: 'https://images.unsplash.com/photo-1707026725345-31a31d4d3c6c?auto=format&fit=crop&w=400&q=80', rating: 4.7 },
    { title: 'Google Pixel 8 Pro (128GB) - Obsidian', price: '₹1,06,999', image: 'https://images.unsplash.com/photo-1696446702334-037198dfffcd?auto=format&fit=crop&w=400&q=80', rating: 4.6 }
  ]
};
