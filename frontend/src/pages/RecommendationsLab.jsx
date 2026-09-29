import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Sliders,
  Cpu,
  Users,
  Layers,
  Zap,
  RefreshCw,
  Info,
  Clock,
  CheckCircle2,
} from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const RecommendationsLab = () => {
  const { user, isAuthenticated } = useAuth();
  const { addToast } = useToast();

  const [activeTab, setActiveTab] = useState('hybrid'); // hybrid, content, collaborative, trending, popular
  const [contentWeight, setContentWeight] = useState(0.6);
  const [collabWeight, setCollabWeight] = useState(0.4);

  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executionTime, setExecutionTime] = useState(0);
  const [isCached, setIsCached] = useState(false);
  const [algorithmName, setAlgorithmName] = useState('hybrid');

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      let endpoint = '/recommendations';

      if (activeTab === 'hybrid') {
        endpoint = `/recommendations?content_weight=${contentWeight}&collab_weight=${collabWeight}&limit=12`;
      } else if (activeTab === 'content') {
        endpoint = '/recommendations/content-based?limit=12';
      } else if (activeTab === 'collaborative') {
        endpoint = '/recommendations/collaborative?limit=12';
      } else if (activeTab === 'trending') {
        endpoint = '/recommendations/trending?limit=12';
      } else if (activeTab === 'popular') {
        endpoint = '/recommendations/popular?limit=12';
      }

      const res = await api.get(endpoint);
      setRecommendations(res.data.recommendations || []);
      setExecutionTime(res.data.execution_time_ms || 0);
      setIsCached(res.data.cached || false);
      setAlgorithmName(res.data.algorithm || activeTab);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
      addToast('Error generating recommendations', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [activeTab, contentWeight, collabWeight, user]);

  const handleContentWeightChange = (newVal) => {
    const val = parseFloat(newVal);
    setContentWeight(val);
    setCollabWeight(parseFloat((1.0 - val).toFixed(2)));
  };

  return (
    <div className="space-y-8 py-6">
      {/* Title & Diagnostic Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-slate-900/90 border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="space-y-2 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-xs font-semibold text-indigo-300">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Interactive Recommendation Algorithm Lab</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Recommendation Engine Control Center
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Dynamically adjust algorithmic weights between TF-IDF Content Similarity and User-Item Collaborative Matrix Factorization in real time.
          </p>
        </div>

        {/* Cloud Diagnostics Pill */}
        <div className="flex flex-col items-end gap-2 shrink-0">
          <div className="flex items-center gap-2 bg-slate-950 px-3.5 py-2 rounded-xl border border-slate-800 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-400">Latency:</span>
            <span className="text-white font-bold">{executionTime}ms</span>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${
                isCached
                  ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/30'
                  : 'bg-indigo-950/80 text-indigo-300 border-indigo-500/30'
              }`}
            >
              {isCached ? 'Cache HIT (Redis/Memory)' : 'Real-time Math Model (MISS)'}
            </span>
            <button
              onClick={fetchRecommendations}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
              title="Recalculate now"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-slate-900/80 border border-slate-800 rounded-2xl">
        <button
          onClick={() => setActiveTab('hybrid')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
            activeTab === 'hybrid'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Layers className="w-4 h-4" />
          Hybrid Engine (Recommended)
        </button>

        <button
          onClick={() => setActiveTab('content')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
            activeTab === 'content'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Cpu className="w-4 h-4 text-sky-400" />
          Content-Based (TF-IDF)
        </button>

        <button
          onClick={() => setActiveTab('collaborative')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
            activeTab === 'collaborative'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Users className="w-4 h-4 text-emerald-400" />
          Collaborative Filtering
        </button>

        <button
          onClick={() => setActiveTab('trending')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
            activeTab === 'trending'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Zap className="w-4 h-4 text-amber-400" />
          Trending Velocity
        </button>

        <button
          onClick={() => setActiveTab('popular')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
            activeTab === 'popular'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25'
              : 'text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4 text-purple-400" />
          Top Rated Popularity
        </button>
      </div>

      {/* Interactive Hybrid Slider Box (Visible when activeTab === 'hybrid') */}
      {activeTab === 'hybrid' && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-indigo-400" />
                Hybrid Weight Calibration
              </h3>
              <p className="text-xs text-slate-400">
                Formula: <span className="font-mono text-indigo-300">Score = ({contentWeight} × Content) + ({collabWeight} × Collaborative)</span>
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="px-2.5 py-1 rounded bg-sky-950/80 text-sky-300 border border-sky-500/30">
                Content: {Math.round(contentWeight * 100)}%
              </span>
              <span className="px-2.5 py-1 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-500/30">
                Collab: {Math.round(collabWeight * 100)}%
              </span>
            </div>
          </div>

          <div className="space-y-2">
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={contentWeight}
              onChange={(e) => handleContentWeightChange(e.target.value)}
              className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
            />
            <div className="flex justify-between text-[11px] text-slate-500 font-medium">
              <span>0% Content / 100% Collaborative</span>
              <span className="text-indigo-400 font-semibold">Standard Default (60 / 40)</span>
              <span>100% Content / 0% Collaborative</span>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation Results Grid */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span>Generated Results</span>
            <span className="text-xs font-normal text-slate-400">({recommendations.length} items ranked)</span>
          </h2>
        </div>

        {loading ? (
          <LoadingSkeleton count={8} />
        ) : recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {recommendations.map((rec) => (
              <div key={rec.item_id} className="relative">
                <ItemCard item={rec} recommendation={rec} />
              </div>
            ))}
          </div>
        ) : (
          <div className="p-16 text-center bg-slate-900/40 border border-slate-800 rounded-3xl space-y-3">
            <Sparkles className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-white">No results returned</h3>
            <p className="text-xs text-slate-400">
              The recommendation engine could not find matching candidates for this configuration.
            </p>
          </div>
        )}
      </section>
    </div>
  );
};

export default RecommendationsLab;
