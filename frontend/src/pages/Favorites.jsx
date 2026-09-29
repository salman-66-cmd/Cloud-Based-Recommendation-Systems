import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Compass, ArrowRight, Trash2 } from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useToast } from '../context/ToastContext';

const Favorites = () => {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const res = await api.get('/interactions/favorites');
      setFavorites(res.data || []);
    } catch (err) {
      console.error('Failed to load favorites:', err);
      addToast('Could not load favorites', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  const handleLikedChange = (itemId, isLiked) => {
    if (!isLiked) {
      setFavorites((prev) => prev.filter((item) => item.id !== itemId));
    }
  };

  return (
    <div className="space-y-8 py-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Heart className="w-7 h-7 text-rose-500 fill-rose-500/20" />
            Saved Cloud Stack
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Cloud solutions and AI models bookmarked in your personal workspace ({favorites.length} items)
          </p>
        </div>

        <Link
          to="/items"
          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
        >
          Add More Services <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {loading ? (
        <LoadingSkeleton count={6} />
      ) : favorites.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {favorites.map((item) => (
            <ItemCard
              key={item.id}
              item={{ ...item, is_liked: true }}
              onLikedChange={handleLikedChange}
            />
          ))}
        </div>
      ) : (
        <div className="p-16 text-center bg-slate-900/40 border border-slate-800 rounded-3xl space-y-4">
          <Heart className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">Your stack is currently empty</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click the heart icon on any cloud service or AI product to save it to your personalized stack.
          </p>
          <Link
            to="/items"
            className="inline-flex px-5 py-2.5 rounded-xl bg-indigo-600 text-white font-semibold text-xs shadow-lg"
          >
            Browse Cloud Catalog
          </Link>
        </div>
      )}
    </div>
  );
};

export default Favorites;
