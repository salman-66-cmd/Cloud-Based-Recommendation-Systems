import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Star, Heart, ShoppingCart, Sparkles, Server, Tag, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

const ItemCard = ({ item, recommendation = null, onLikedChange = null }) => {
  const { isAuthenticated } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [isLiked, setIsLiked] = useState(item.is_liked || false);
  const [likeLoading, setLikeLoading] = useState(false);
  const [cartLoading, setCartLoading] = useState(false);

  // If item is wrapped inside recommendation response:
  const product = item.item || item;
  const score = recommendation?.score || item.score;
  const reason = recommendation?.reason || item.reason;
  const algorithm = recommendation?.algorithm || item.algorithm;

  const handleLike = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      addToast('Please sign in to save items to your favorites', 'info');
      navigate('/login');
      return;
    }

    setLikeLoading(true);
    try {
      if (isLiked) {
        await api.delete(`/interactions/favorites/${product.id}`);
        setIsLiked(false);
        addToast(`Removed ${product.name} from favorites`, 'info');
      } else {
        await api.post('/interactions', {
          item_id: product.id,
          interaction_type: 'like',
        });
        setIsLiked(true);
        addToast(`Added ${product.name} to your saved stack!`, 'success');
      }
      if (onLikedChange) onLikedChange(product.id, !isLiked);
    } catch (err) {
      addToast('Failed to update favorites', 'error');
    } finally {
      setLikeLoading(false);
    }
  };

  const handleAddToCart = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      addToast('Please sign in to add items to your architecture stack', 'info');
      navigate('/login');
      return;
    }

    setCartLoading(true);
    try {
      await api.post('/interactions', {
        item_id: product.id,
        interaction_type: 'add_to_cart',
      });
      addToast(`Added ${product.name} to Cloud Stack Cart!`, 'success');
    } catch (err) {
      addToast('Could not add to stack', 'error');
    } finally {
      setCartLoading(false);
    }
  };

  const handleCardClick = async () => {
    if (isAuthenticated) {
      try {
        api.post('/interactions', {
          item_id: product.id,
          interaction_type: 'click',
        });
      } catch (e) {
        // silent fail for non-blocking analytics
      }
    }
    navigate(`/items/${product.id}`);
  };

  const providerColors = {
    AWS: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    'Google Cloud': 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    'Microsoft Azure': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    Cloudflare: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    'Multi-Cloud': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  };

  const badgeClass =
    providerColors[product.cloud_provider] || 'bg-slate-800 text-slate-300 border-slate-700';

  const tagsList = (product.tags || '')
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
    .slice(0, 3);

  return (
    <div
      onClick={handleCardClick}
      className="group relative bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden hover:border-indigo-500/50 hover:shadow-2xl hover:shadow-indigo-500/10 transition-all duration-300 flex flex-col justify-between cursor-pointer"
    >
      {/* Top Media & Badges */}
      <div>
        <div className="relative h-44 w-full bg-slate-800/80 overflow-hidden">
          <img
            src={product.image_url || 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=600&auto=format&fit=crop&q=80'}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent" />

          {/* Cloud Provider & Tier Pill */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1.5 z-10">
            <span
              className={`text-[11px] font-semibold px-2 py-0.5 rounded-md border backdrop-blur-md ${badgeClass}`}
            >
              {product.cloud_provider}
            </span>
            <span className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-900/80 text-slate-300 border border-slate-700/60 backdrop-blur-md">
              {product.tier || 'Pay-as-you-go'}
            </span>
          </div>

          {/* Favorite Like Button */}
          <button
            onClick={handleLike}
            disabled={likeLoading}
            className={`absolute top-3 right-3 p-2 rounded-xl backdrop-blur-md border transition-all z-10 ${
              isLiked
                ? 'bg-rose-500 text-white border-rose-400 shadow-lg shadow-rose-500/30'
                : 'bg-slate-900/70 text-slate-300 border-slate-700/60 hover:text-white hover:bg-slate-800'
            }`}
            title={isLiked ? 'Remove from favorites' : 'Save to favorites'}
          >
            <Heart className={`w-4 h-4 ${isLiked ? 'fill-white' : ''}`} />
          </button>

          {/* Recommendation Match Badge */}
          {score !== undefined && score !== null && (
            <div className="absolute bottom-3 left-3 flex items-center gap-1.5 bg-indigo-950/90 border border-indigo-500/40 backdrop-blur-md px-2.5 py-1 rounded-lg text-xs font-bold text-indigo-200 shadow-lg">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              <span>{Math.round(score * 100)}% Match</span>
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="p-4 space-y-2.5">
          {/* Category */}
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-medium text-indigo-400 truncate max-w-[180px]">
              {product.category?.name || 'Cloud Solution'}
            </span>
            <div className="flex items-center gap-1 font-semibold text-slate-200">
              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
              <span>{product.rating ? Number(product.rating).toFixed(1) : '4.5'}</span>
              <span className="text-[11px] text-slate-500">({product.rating_count || 12})</span>
            </div>
          </div>

          {/* Title */}
          <h3 className="font-bold text-slate-100 text-base group-hover:text-indigo-300 transition-colors line-clamp-1">
            {product.name}
          </h3>

          {/* Description snippet */}
          <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
            {product.description}
          </p>

          {/* Dynamic Reason Pill (Recommendation Explanation) */}
          {reason && (
            <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-200 flex items-start gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <span className="leading-snug italic">{reason}</span>
            </div>
          )}

          {/* Tags */}
          {tagsList.length > 0 && (
            <div className="flex flex-wrap gap-1 pt-1">
              {tagsList.map((tag) => (
                <span
                  key={tag}
                  className="text-[10px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50 flex items-center gap-0.5"
                >
                  <Tag className="w-2.5 h-2.5" />
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer: Price and Quick Actions */}
      <div className="p-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
        <div className="flex flex-col">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Pricing</span>
          <span className="text-sm font-bold text-white">
            {product.price > 0 ? `$${product.price}/mo` : 'Free Tier'}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={handleAddToCart}
            disabled={cartLoading}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/60 transition-colors cursor-pointer"
            title="Add to cloud architecture stack"
          >
            <ShoppingCart className="w-4 h-4" />
          </button>

          <span className="px-2.5 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-medium transition-all flex items-center gap-1">
            Details <ArrowRight className="w-3.5 h-3.5" />
          </span>
        </div>
      </div>
    </div>
  );
};

export default ItemCard;
