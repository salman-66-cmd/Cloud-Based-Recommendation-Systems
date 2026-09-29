import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Star,
  Heart,
  ShoppingCart,
  Sparkles,
  Server,
  Tag,
  ArrowLeft,
  CheckCircle2,
  Trash2,
  Share2,
  Layers,
  Terminal,
  Clock,
  Send,
  Zap,
} from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const ItemDetail = () => {
  const { id } = useParams();
  const { isAuthenticated, user } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);

  // Rating state
  const [userRating, setUserRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [reviewText, setReviewText] = useState('');
  const [submittingRating, setSubmittingRating] = useState(false);
  const [hasRated, setHasRated] = useState(false);

  // Like state
  const [isLiked, setIsLiked] = useState(false);
  const [likeLoading, setLikeLoading] = useState(false);

  const fetchItemDetail = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/items/${id}`);
      setItem(res.data);
      setIsLiked(res.data.is_liked || false);
      if (res.data.user_rating) {
        setUserRating(res.data.user_rating);
        setHasRated(true);
      } else {
        setUserRating(0);
        setHasRated(false);
      }
    } catch (err) {
      console.error('Failed to load item:', err);
      addToast('Could not load item details', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItemDetail();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [id]);

  const handleLikeToggle = async () => {
    if (!isAuthenticated) {
      addToast('Please sign in to save items to your favorites', 'info');
      navigate('/login');
      return;
    }

    setLikeLoading(true);
    try {
      if (isLiked) {
        await api.delete(`/interactions/favorites/${item.id}`);
        setIsLiked(false);
        addToast(`Removed ${item.name} from favorites`, 'info');
      } else {
        await api.post('/interactions', {
          item_id: item.id,
          interaction_type: 'like',
        });
        setIsLiked(true);
        addToast(`Saved ${item.name} to favorites!`, 'success');
      }
    } catch (err) {
      addToast('Failed to update favorites', 'error');
    } finally {
      setLikeLoading(false);
    }
  };

  const handleRatingSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      addToast('Please sign in to rate cloud products', 'info');
      navigate('/login');
      return;
    }

    if (userRating === 0) {
      addToast('Please select a star rating from 1 to 5', 'info');
      return;
    }

    setSubmittingRating(true);
    try {
      const res = await api.post('/ratings', {
        item_id: item.id,
        rating: userRating,
        review: reviewText.trim() || null,
      });

      setHasRated(true);
      addToast(`Rating of ${userRating}★ saved! Collaborative engine updated.`, 'success');
      // Refresh item to get updated avg rating
      const updated = await api.get(`/items/${id}`);
      setItem(updated.data);
    } catch (err) {
      addToast('Failed to submit rating', 'error');
    } finally {
      setSubmittingRating(false);
    }
  };

  const handleDeleteRating = async () => {
    try {
      await api.delete(`/ratings/${item.id}`);
      setUserRating(0);
      setReviewText('');
      setHasRated(false);
      addToast('Rating deleted', 'info');
      const updated = await api.get(`/items/${id}`);
      setItem(updated.data);
    } catch (err) {
      addToast('Failed to delete rating', 'error');
    }
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      addToast('Please sign in to add to your stack', 'info');
      navigate('/login');
      return;
    }
    try {
      await api.post('/interactions', {
        item_id: item.id,
        interaction_type: 'add_to_cart',
      });
      addToast(`Added ${item.name} to active cloud deployment plan!`, 'success');
    } catch (e) {
      addToast('Error recording stack interaction', 'error');
    }
  };

  const handleSimulateDeploy = () => {
    addToast(`Provisioning sandbox infrastructure for ${item.name}... (Simulated Cloud Task)`, 'info');
  };

  if (loading) {
    return (
      <div className="py-12 space-y-6">
        <div className="h-8 bg-slate-800 rounded w-1/4 animate-pulse" />
        <div className="h-96 bg-slate-800 rounded-3xl animate-pulse" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="py-20 text-center space-y-4">
        <h2 className="text-xl font-bold text-white">Item Not Found</h2>
        <Link to="/items" className="text-indigo-400 hover:text-indigo-300 text-sm">
          Return to Catalog
        </Link>
      </div>
    );
  }

  let featuresList = [];
  try {
    featuresList = JSON.parse(item.features || '[]');
  } catch (e) {
    featuresList = [];
  }

  const tagsList = (item.tags || '')
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean);

  return (
    <div className="space-y-12 py-6">
      {/* Back button */}
      <div>
        <Link
          to="/items"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Catalog
        </Link>
      </div>

      {/* Main Product Hero Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left: Product Media Gallery */}
        <div className="lg:col-span-5 space-y-4">
          <div className="relative h-80 sm:h-96 rounded-3xl overflow-hidden bg-slate-900 border border-slate-800 shadow-2xl">
            <img
              src={item.image_url || 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&auto=format&fit=crop&q=80'}
              alt={item.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />

            {/* Provider and Tier pills */}
            <div className="absolute top-4 left-4 flex flex-wrap gap-2">
              <span className="text-xs font-bold px-3 py-1 rounded-lg bg-slate-900/90 text-white border border-slate-700 backdrop-blur-md">
                {item.cloud_provider}
              </span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-indigo-950/90 text-indigo-300 border border-indigo-500/40 backdrop-blur-md">
                {item.tier}
              </span>
            </div>

            {/* Price Badge */}
            <div className="absolute bottom-4 left-4 bg-slate-900/90 border border-slate-800 backdrop-blur-md px-4 py-2 rounded-2xl">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Pricing</div>
              <div className="text-lg font-black text-white">
                {item.price > 0 ? `$${item.price} / mo` : 'Free Tier Included'}
              </div>
            </div>
          </div>

          {/* Action Row */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleLikeToggle}
              disabled={likeLoading}
              className={`flex-1 py-3 px-4 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                isLiked
                  ? 'bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/25'
                  : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800 hover:text-white'
              }`}
            >
              <Heart className={`w-4 h-4 ${isLiked ? 'fill-white' : ''}`} />
              {isLiked ? 'Saved to Favorites' : 'Add to Favorites'}
            </button>

            <button
              onClick={handleAddToCart}
              className="flex-1 py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              <ShoppingCart className="w-4 h-4" />
              Add to Cloud Stack
            </button>
          </div>
        </div>

        {/* Right: Technical Details & Interactive Rating */}
        <div className="lg:col-span-7 space-y-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-indigo-400 uppercase tracking-wider">
                {item.category?.name}
              </span>
              <span className="text-slate-500">ID: #{item.id}</span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              {item.name}
            </h1>

            {/* Rating Stars Bar */}
            <div className="flex items-center gap-3 pt-1">
              <div className="flex items-center text-amber-400">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < Math.floor(item.rating)
                        ? 'fill-amber-400 text-amber-400'
                        : i < item.rating
                        ? 'fill-amber-400/50 text-amber-400'
                        : 'text-slate-700'
                    }`}
                  />
                ))}
              </div>
              <span className="text-base font-bold text-white">{Number(item.rating).toFixed(1)}</span>
              <span className="text-xs text-slate-400">({item.rating_count} verified architects)</span>
            </div>
          </div>

          {/* Description */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">Overview</h3>
            <p className="text-sm text-slate-300 leading-relaxed">{item.description}</p>
          </div>

          {/* Technical Specifications & Features */}
          {featuresList.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Key Technical Capabilities
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {featuresList.map((feat, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 flex items-center gap-2.5 text-xs text-slate-200"
                  >
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Architectural Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {tagsList.map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 text-xs flex items-center gap-1.5"
                >
                  <Tag className="w-3 h-3 text-sky-400" />
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Interactive Rating Section */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950/20 to-slate-900 border border-indigo-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                  <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                  Rate this Cloud Service (1–5 Stars)
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Your rating instantly recalibrates the Collaborative Filtering recommendation engine.
                </p>
              </div>

              {hasRated && (
                <button
                  type="button"
                  onClick={handleDeleteRating}
                  className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Remove Rating
                </button>
              )}
            </div>

            <form onSubmit={handleRatingSubmit} className="space-y-4">
              {/* Star selector */}
              <div className="flex items-center gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setUserRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="p-1 focus:outline-none transition-transform hover:scale-125 cursor-pointer"
                  >
                    <Star
                      className={`w-7 h-7 transition-colors ${
                        (hoverRating || userRating) >= star
                          ? 'fill-amber-400 text-amber-400'
                          : 'text-slate-700'
                      }`}
                    />
                  </button>
                ))}
                <span className="text-xs font-bold text-slate-300 ml-2">
                  {userRating > 0 ? `${userRating} Stars` : 'Click to select'}
                </span>
              </div>

              {/* Review input */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Share a short architect review (e.g. 'Exceptional latency, simple deployment')..."
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={submittingRating || userRating === 0}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-md transition-all flex items-center gap-2 cursor-pointer"
              >
                <Send className="w-3.5 h-3.5" />
                {hasRated ? 'Update Rating & Review' : 'Submit Review'}
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Similar Items & Alternatives Section */}
      <section className="space-y-6 pt-6 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Similar Cloud Solutions & Alternatives
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Calculated dynamically via TF-IDF cosine similarity across tech specifications, category, and tags.
            </p>
          </div>
        </div>

        {item.similar_items && item.similar_items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {item.similar_items.map((sim) => (
              <ItemCard key={sim.id} item={sim} />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-2xl">
            <p className="text-xs text-slate-400">No direct alternatives found for this item.</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default ItemDetail;
