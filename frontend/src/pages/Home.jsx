import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Flame,
  Star,
  Compass,
  ArrowRight,
  Search,
  Cpu,
  Layers,
  Server,
  Zap,
  Shield,
  Activity,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';

const Home = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [recommended, setRecommended] = useState([]);
  const [trending, setTrending] = useState([]);
  const [popular, setPopular] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recMeta, setRecMeta] = useState({ latency: 0, cached: false, algo: 'hybrid' });
  const [searchQuery, setSearchQuery] = useState('');

  const fetchHomeData = async () => {
    setLoading(true);
    try {
      const [recRes, trendRes, popRes, catRes] = await Promise.all([
        api.get('/recommendations?limit=6'),
        api.get('/recommendations/trending?limit=4'),
        api.get('/recommendations/popular?limit=4'),
        api.get('/categories')
      ]);

      setRecommended(recRes.data.recommendations || []);
      setRecMeta({
        latency: recRes.data.execution_time_ms,
        cached: recRes.data.cached,
        algo: recRes.data.algorithm
      });
      setTrending(trendRes.data.recommendations || []);
      setPopular(popRes.data.recommendations || []);
      setCategories(catRes.data || []);
    } catch (err) {
      console.error('Failed to load home page data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHomeData();
  }, [user]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/items?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-indigo-950/40 via-slate-900/60 to-slate-950 border border-slate-800 p-8 sm:p-12 lg:p-16">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl -z-10 pointer-events-none" />

        <div className="max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-xs font-semibold text-indigo-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Hybrid Recommendation Engine • Content + Collaborative Filtering</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Discover the Best{' '}
            <span className="gradient-text">Cloud & AI Solutions</span>{' '}
            Tailored to You
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
            Real-time personalized recommendations powered by TF-IDF item feature vectors and user-item collaborative matrix factorization. Designed for modern cloud architects and engineers.
          </p>

          {/* Search bar inside Hero */}
          <form onSubmit={handleSearchSubmit} className="pt-2 max-w-xl">
            <div className="relative flex items-center">
              <Search className="w-5 h-5 text-slate-400 absolute left-4" />
              <input
                type="text"
                placeholder="Try 'kubernetes auto-scaling', 'vector db', 'waf'..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-28 py-3.5 bg-slate-900/90 border border-slate-700/80 rounded-2xl text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 shadow-xl"
              />
              <button
                type="submit"
                className="absolute right-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold shadow-md transition-colors cursor-pointer"
              >
                Search
              </button>
            </div>
          </form>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-3">
            <Link
              to="/recommendations"
              className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-all hover:-translate-y-0.5"
            >
              <Sparkles className="w-4 h-4 text-amber-400" />
              Tune Recommendations
            </Link>

            <Link
              to="/items"
              className="px-5 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 hover:text-white border border-slate-700 font-semibold text-sm flex items-center gap-2 transition-all"
            >
              <Compass className="w-4 h-4 text-sky-400" />
              Browse 100+ Products
            </Link>

            {!isAuthenticated && (
              <Link
                to="/register"
                className="px-5 py-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 font-semibold text-sm flex items-center gap-2 transition-all"
              >
                Start Onboarding
              </Link>
            )}
          </div>
        </div>

        {/* Cloud Stats Counter */}
        <div className="mt-12 pt-8 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-4 gap-6">
          <div>
            <div className="text-2xl sm:text-3xl font-black text-white">100+</div>
            <div className="text-xs text-slate-400 font-medium">Cloud Products</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-black text-sky-400">10</div>
            <div className="text-xs text-slate-400 font-medium">Tech Categories</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-black text-indigo-400">0.6 / 0.4</div>
            <div className="text-xs text-slate-400 font-medium">Content / Collab Ratio</div>
          </div>
          <div>
            <div className="text-2xl sm:text-3xl font-black text-emerald-400">&lt; 15ms</div>
            <div className="text-xs text-slate-400 font-medium">Average Latency</div>
          </div>
        </div>
      </section>

      {/* Recommended For You Section */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-amber-400" />
                Recommended For You
              </h2>
              {recMeta.cached ? (
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/30">
                  Cache HIT ({recMeta.latency}ms)
                </span>
              ) : (
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                  Real-time Engine ({recMeta.latency}ms)
                </span>
              )}
            </div>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              {isAuthenticated
                ? `Generated specifically for ${user?.name} based on interaction history & onboarding preferences.`
                : 'Showing top recommendations based on cloud popularity & featured architectures. Sign in for personalized scoring.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchHomeData}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
              title="Recalculate recommendations"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
            </button>
            <Link
              to="/recommendations"
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              View All Recommendations <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton count={6} />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommended.map((rec) => (
              <ItemCard key={rec.item_id} item={rec} recommendation={rec} />
            ))}
          </div>
        )}
      </section>

      {/* Cloud Categories Grid */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
              <Layers className="w-6 h-6 text-sky-400" />
              Explore Cloud Categories
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Browse services organized by modern cloud computing domains
            </p>
          </div>
          <Link
            to="/items"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            All Categories <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/items?category=${encodeURIComponent(cat.slug)}`}
              className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 hover:bg-slate-800/60 transition-all space-y-2 group"
            >
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:scale-110 group-hover:bg-indigo-600 group-hover:text-white transition-all">
                <Server className="w-5 h-5" />
              </div>
              <h4 className="font-semibold text-sm text-slate-200 group-hover:text-indigo-300 transition-colors line-clamp-1">
                {cat.name}
              </h4>
              <p className="text-[11px] text-slate-400">
                {cat.item_count || 10} products
              </p>
            </Link>
          ))}
        </div>
      </section>

      {/* Trending Items Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
              <Flame className="w-6 h-6 text-orange-400" />
              Trending Velocity
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Products with highest interaction velocity and click-through rates across all users
            </p>
          </div>
          <Link
            to="/items?sort_by=popular"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Explore Trending <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {trending.map((item) => (
            <ItemCard key={item.item_id} item={item} recommendation={item} />
          ))}
        </div>
      </section>

      {/* Popular & Highly Rated Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
              <Star className="w-6 h-6 text-amber-400" />
              Popular & Top Rated
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Solutions with top architect endorsements and average ratings above 4.5 stars
            </p>
          </div>
          <Link
            to="/items?sort_by=rating"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Highest Rated <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {popular.map((item) => (
            <ItemCard key={item.item_id} item={item} recommendation={item} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
