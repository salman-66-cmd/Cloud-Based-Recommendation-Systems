import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Mail,
  Shield,
  Clock,
  Search,
  Sliders,
  LogOut,
  Layers,
  CheckCircle2,
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const Profile = () => {
  const { user, logout } = useAuth();
  const { addToast } = useToast();

  const [preferences, setPreferences] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      setLoading(true);
      try {
        const [prefRes, searchRes] = await Promise.all([
          api.get('/preferences'),
          api.get('/search/history?limit=15'),
        ]);
        setPreferences(prefRes.data || null);
        setSearchHistory(searchRes.data || []);
      } catch (err) {
        console.error('Failed to load profile details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8 space-y-8">
      {/* Profile Header Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-slate-900/80 border border-slate-800 shadow-xl flex flex-col sm:flex-row items-center gap-6">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-indigo-600 to-sky-400 flex items-center justify-center text-white text-2xl font-black uppercase shadow-lg shadow-indigo-600/30">
          {user?.name?.slice(0, 2) || 'US'}
        </div>

        <div className="space-y-1 text-center sm:text-left flex-1">
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2">
            <h1 className="text-2xl font-bold text-white">{user?.name}</h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase font-semibold">
              {user?.role}
            </span>
          </div>
          <p className="text-xs text-slate-400 flex items-center justify-center sm:justify-start gap-1.5">
            <Mail className="w-3.5 h-3.5" />
            {user?.email}
          </p>
          <p className="text-[11px] text-slate-500 flex items-center justify-center sm:justify-start gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            Member since {new Date(user?.created_at).toLocaleDateString()}
          </p>
        </div>

        <button
          onClick={logout}
          className="px-4 py-2 rounded-xl bg-rose-950/40 hover:bg-rose-900/50 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>

      {/* Onboarding Technical Focus */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-emerald-400" />
              Active Recommendation Profile
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              These categories and cloud providers are boosted in your TF-IDF vector space
            </p>
          </div>
          <Link
            to="/onboarding"
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200"
          >
            Edit Preferences
          </Link>
        </div>

        <div className="space-y-3 pt-2">
          <div>
            <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
              Preferred Domains:
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {preferences?.preferred_categories?.length ? (
                preferences.preferred_categories.map((cat) => (
                  <span
                    key={cat}
                    className="px-2.5 py-1 rounded-lg bg-indigo-950/80 text-indigo-300 border border-indigo-500/30 text-xs font-medium"
                  >
                    {cat}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-500">None selected</span>
              )}
            </div>
          </div>

          <div>
            <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400">
              Cloud Environments:
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {preferences?.preferred_cloud_providers?.length ? (
                preferences.preferred_cloud_providers.map((prov) => (
                  <span
                    key={prov}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 text-xs font-medium"
                  >
                    {prov}
                  </span>
                ))
              ) : (
                <span className="text-xs text-slate-500">None selected</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Search History Signal Log */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Search className="w-4 h-4 text-sky-400" />
            Recent Search Queries (Recommendation Signal)
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Search terms are indexed into your interaction profile to refine item ranking
          </p>
        </div>

        {searchHistory.length > 0 ? (
          <div className="divide-y divide-slate-800/80">
            {searchHistory.map((s) => (
              <div key={s.id} className="py-2.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-slate-500">"</span>
                  <span className="font-semibold text-slate-200">{s.query}</span>
                  <span className="text-slate-500">"</span>
                  <span className="text-[10px] text-slate-500">({s.results_count} results)</span>
                </div>
                <span className="text-[11px] text-slate-500 font-mono">{s.created_at}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">No searches recorded yet.</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
