import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  Activity,
  Layers,
  Star,
  RefreshCw,
  Clock,
  Shield,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import api from '../services/api';
import { useToast } from '../context/ToastContext';

const COLORS = ['#6366f1', '#38bdf8', '#34d399', '#f59e0b', '#ec4899', '#a855f7', '#14b8a6'];

const AdminAnalytics = () => {
  const [stats, setStats] = useState(null);
  const [interactionLogs, setInteractionLogs] = useState([]);
  const [recLogs, setRecLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeLogTab, setActiveLogTab] = useState('interactions'); // interactions, recommendations
  const { addToast } = useToast();

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [statsRes, logsRes, recLogsRes] = await Promise.all([
        api.get('/admin/stats'),
        api.get('/admin/interaction-logs?limit=40'),
        api.get('/admin/recommendation-logs?limit=40'),
      ]);

      setStats(statsRes.data);
      setInteractionLogs(logsRes.data || []);
      setRecLogs(recLogsRes.data || []);
    } catch (err) {
      console.error(err);
      addToast('Error fetching analytics data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-8 py-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-emerald-400" />
            Deep Analytics & Interaction Telemetry
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Recharts visual diagnostics and real-time event logs for the hybrid recommendation engine
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          className="px-3.5 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* Grid of 4 Detailed Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Ratings Distribution */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Star className="w-4 h-4 text-amber-400" />
              Rating Score Distribution (1–5 Stars)
            </h3>
            <span className="text-[11px] text-slate-500">Collaborative Factor</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats?.ratings_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="stars" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Bar dataKey="count" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Interaction Types Breakdown */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-400" />
              Interaction Types Volume
            </h3>
            <span className="text-[11px] text-slate-500">View, Click, Like, Cart</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.interaction_types_breakdown || []}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {(stats?.interaction_types_breakdown || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. Category Popularity */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              Category Inventory & Density
            </h3>
            <span className="text-[11px] text-slate-500">Products per domain</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={stats?.popular_categories || []}
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fontSize: 9 }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. Recommendation Algorithm Usage */}
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-purple-400" />
              Algorithm Distribution
            </h3>
            <span className="text-[11px] text-slate-500">Model Deployment Mix</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats?.algorithm_distribution || []}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={5}
                >
                  {(stats?.algorithm_distribution || []).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Real-time Interaction Logs & Recommendation Audits */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveLogTab('interactions')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                activeLogTab === 'interactions'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              User Interaction Events ({interactionLogs.length})
            </button>
            <button
              onClick={() => setActiveLogTab('recommendations')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors cursor-pointer ${
                activeLogTab === 'recommendations'
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              Recommendation Audit Trail ({recLogs.length})
            </button>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Live Telemetry Feed</span>
        </div>

        {activeLogTab === 'interactions' ? (
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0">
                <tr>
                  <th className="py-2.5 px-3">Architect</th>
                  <th className="py-2.5 px-3">Product</th>
                  <th className="py-2.5 px-3">Event Type</th>
                  <th className="py-2.5 px-3">Weight</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {interactionLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-medium text-white">{log.user_name}</td>
                    <td className="py-2.5 px-3 text-slate-300">{log.item_name}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-800 text-indigo-300 border border-slate-700">
                        {log.interaction_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-mono text-emerald-400">+{log.weight}</td>
                    <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">{log.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0">
                <tr>
                  <th className="py-2.5 px-3">Target User</th>
                  <th className="py-2.5 px-3">Recommended Item</th>
                  <th className="py-2.5 px-3">Score</th>
                  <th className="py-2.5 px-3">Algorithm</th>
                  <th className="py-2.5 px-3">Dynamic Reason</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-medium text-white">{log.user_name}</td>
                    <td className="py-2.5 px-3 text-slate-300">{log.item_name}</td>
                    <td className="py-2.5 px-3 font-mono text-amber-400 font-bold">
                      {Math.round(log.score * 100)}%
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-sky-300 border border-slate-700">
                        {log.algorithm}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 italic max-w-xs truncate">{log.reason}</td>
                    <td className="py-2.5 px-3 text-slate-500 font-mono text-[11px]">{log.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminAnalytics;
