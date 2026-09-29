import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  LayoutDashboard,
  Sparkles,
  Heart,
  Star,
  Activity,
  Sliders,
  Compass,
  ArrowRight,
  Clock,
  Layers,
  Trash2,
  RefreshCw,
} from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const Dashboard = () => {
  const { user } = useAuth();
  const { addToast } = useToast();

  const [recommendations, setRecommendations] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [ratings, setRatings] = useState([]);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    setRefreshing(true);
    try {
      const [recRes, favRes, ratRes, prefRes] = await Promise.all([
        api.get('/recommendations?limit=6'),
        api.get('/interactions/favorites'),
        api.get('/ratings/user'),
        api.get('/preferences'),
      ]);

      setRecommendations(recRes.data.recommendations || []);
      setFavorites(favRes.data || []);
      setRatings(ratRes.data || []);
      setPreferences(prefRes.data || null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleDeleteRating = async (itemId) => {
    try {
      await api.delete(`/ratings/${itemId}`);
      setRatings((prev) => prev.filter((r) => r.item_id !== itemId));
      addToast('Rating deleted successfully', 'info');
      // refresh recommendations
      api.get('/recommendations?limit=6').then((res) => {
        setRecommendations(res.data.recommendations || []);
      });
    } catch (err) {
      addToast('Failed to delete rating', 'error');
    }
  };

  return (
    <div className="space-y-10 py-6">
      {/* Header Profile Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 shadow-xl">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              Architect Workspace
            </span>
            <span className="text-xs text-slate-400 capitalize">• {user?.role}</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Welcome back, {user?.name}
          </h1>
          <p className="text-xs sm:text-sm text-slate-300">
            {preferences?.preferred_categories?.length ? (
              <span>Focused on: <strong className="text-indigo-400">{preferences.preferred_categories.join(', ')}</strong></span>
            ) : (
              <span>Personalize your technical recommendations in onboarding preferences</span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchDashboardData}
            disabled={refreshing}
            className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors cursor-pointer"
            title="Refresh dashboard metrics"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-indigo-400' : ''}`} />
          </button>
          <Link
            to="/onboarding"
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Sliders className="w-4 h-4 text-emerald-400" />
            Edit Preferences
          </Link>
          <Link
            to="/recommendations"
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 transition-all"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            Tuning Lab
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-semibold uppercase tracking-wider">Top Match Score</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-white">
            {recommendations[0]?.score ? `${Math.round(recommendations[0].score * 100)}%` : '92%'}
          </div>
          <p className="text-[11px] text-slate-500">Hybrid similarity confidence</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-semibold uppercase tracking-wider">Saved Favorites</span>
            <Heart className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-white">
            {favorites.length}
          </div>
          <p className="text-[11px] text-slate-500">Items in your stack</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-semibold uppercase tracking-wider">Ratings Given</span>
            <Star className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-black text-white">
            {ratings.length}
          </div>
          <p className="text-[11px] text-slate-500">Contributions to collab matrix</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span className="font-semibold uppercase tracking-wider">Engine Mode</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl sm:text-2xl font-black text-emerald-400">
            Hybrid v1.0
          </div>
          <p className="text-[11px] text-slate-500">60% TF-IDF + 40% CF</p>
        </div>
      </div>

      {/* Personalized Recommendations Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Your Tailored Cloud Recommendations
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Dynamic recommendations calculated from your views, likes, and ratings.
            </p>
          </div>
          <Link
            to="/recommendations"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            Adjust Algorithm Weights <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <LoadingSkeleton count={3} />
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.slice(0, 6).map((rec) => (
              <ItemCard key={rec.item_id} item={rec} recommendation={rec} />
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-slate-900/40 border border-slate-800 rounded-3xl space-y-4">
            <Compass className="w-10 h-10 text-slate-500 mx-auto" />
            <h3 className="text-base font-bold text-white">No Recommendations Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Start by selecting your preferred domains or browsing through the catalog.
            </p>
            <Link
              to="/items"
              className="inline-flex px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-xs shadow-lg"
            >
              Browse Cloud Catalog
            </Link>
          </div>
        )}
      </section>

      {/* Saved Stack (Favorites) Section */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Heart className="w-5 h-5 text-rose-400" />
              Saved Cloud Stack ({favorites.length})
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Services you've liked and earmarked for deployment
            </p>
          </div>
          <Link
            to="/favorites"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
          >
            View All Saved <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {favorites.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {favorites.slice(0, 4).map((fav) => (
              <ItemCard
                key={fav.id}
                item={{ ...fav, is_liked: true }}
                onLikedChange={(id, liked) => {
                  if (!liked) setFavorites((prev) => prev.filter((f) => f.id !== id));
                }}
              />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl">
            <p className="text-xs text-slate-400">
              No favorites saved yet. Click the heart icon on any product to save it here.
            </p>
          </div>
        )}
      </section>

      {/* User's Ratings & Reviews Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Star className="w-5 h-5 text-amber-400" />
              Your Reviews & Ratings ({ratings.length})
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Ratings directly guide the Collaborative Filtering engine for peer recommendations
            </p>
          </div>
        </div>

        {ratings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {ratings.map((rat) => (
              <div
                key={rat.id}
                className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 flex items-start justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-sm text-white">Item #{rat.item_id}</span>
                    <div className="flex items-center text-amber-400">
                      <Star className="w-3.5 h-3.5 fill-amber-400" />
                      <span className="text-xs font-bold ml-1">{rat.rating} / 5.0</span>
                    </div>
                  </div>
                  {rat.review && (
                    <p className="text-xs text-slate-400 italic">"{rat.review}"</p>
                  )}
                  <div className="text-[10px] text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(rat.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    to={`/items/${rat.item_id}`}
                    className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition-colors"
                  >
                    View
                  </Link>
                  <button
                    onClick={() => handleDeleteRating(rat.item_id)}
                    className="p-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-900/50 text-rose-400 text-xs transition-colors cursor-pointer"
                    title="Delete rating"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl">
            <p className="text-xs text-slate-400">
              You haven't submitted any ratings yet. Open any item and submit a 1-5 star review to train your collaborative profile!
            </p>
          </div>
        )}
      </section>
    </div>
  );
};

export default Dashboard;
