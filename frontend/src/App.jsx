import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import CategoryGrid from './components/CategoryGrid';
import LoginPage from './pages/LoginPage';
import ComparePage from './pages/ComparePage';

function Home() {
  return (
    <>
      <Navbar />
      <main>
        <HeroSection />
        <CategoryGrid />
      </main>
      <footer className="py-12 bg-white border-t border-slate-100 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 text-sm font-medium flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-400 font-bold text-xl mb-2">P</div>
          <p>&copy; {new Date().getFullYear()} PriceScout. Assisting your market research.</p>
        </div>
      </footer>
    </>
  );
}

function App() {
  useEffect(() => {
    document.title = "PriceScout - Modern Deal Discovery";
  }, []);

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 selection:bg-cyan-200 selection:text-slate-900 antialiased flex flex-col">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/compare" element={<ComparePage />} />
      </Routes>
    </div>
  );
}

export default App;
