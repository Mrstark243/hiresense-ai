import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Cpu, LayoutDashboard } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const location = useLocation();
  const hasResult = !!localStorage.getItem('lastAnalysis');

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToAnalyze = () => {
    setIsOpen(false);
    if (location.pathname !== '/') {
      window.location.href = '/#analyze-section';
    } else {
      const element = document.getElementById('analyze-section');
      element?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className={`fixed top-0 z-50 w-full transition-all duration-300 px-6 glass ${
      scrolled ? 'py-3 border-b border-white/5' : 'py-5 shadow-none border-b border-transparent'
    }`}>
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2 group">
          <div className="bg-primary-600 p-2 rounded-xl shadow-lg group-hover:rotate-12 transition-transform duration-300">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight gradient-text">HireSense AI</span>
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex items-center space-x-8">
          <Link to="/" className="text-sm font-medium hover:text-primary-400 transition-colors">Home</Link>
          {hasResult && (
            <Link to="/dashboard" className="text-sm font-medium flex items-center gap-2 hover:text-primary-400 transition-colors">
              <LayoutDashboard size={16} />
              Dashboard
            </Link>
          )}
          <button 
            onClick={scrollToAnalyze}
            className="bg-primary-600 hover:bg-primary-500 text-white px-6 py-2.5 rounded-full text-sm font-bold transition-all shadow-lg shadow-primary-500/20 hover:shadow-primary-500/40 active:scale-95"
          >
            Get Started
          </button>
        </div>

        {/* Mobile Toggle */}
        <div className="md:hidden">
          <button onClick={() => setIsOpen(!isOpen)} className="text-slate-300 p-2">
            {isOpen ? <X /> : <Menu />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden absolute top-full left-0 w-full glass border-t border-white/5 p-6 space-y-4 animate-in slide-in-from-top duration-300">
          <Link to="/" className="block text-lg font-medium hover:text-primary-400" onClick={() => setIsOpen(false)}>Home</Link>
          {hasResult && (
            <Link to="/dashboard" className="block text-lg font-medium hover:text-primary-400" onClick={() => setIsOpen(false)}>Dashboard</Link>
          )}
          <button onClick={scrollToAnalyze} className="w-full bg-primary-600 text-white py-4 rounded-2xl font-bold">Get Started</button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
