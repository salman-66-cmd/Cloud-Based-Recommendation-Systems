import React, { useState, useEffect } from 'react';
import { Cloud, Zap, CheckCircle2, RefreshCw, Cpu, Server, AlertCircle } from 'lucide-react';
import api from '../services/api';

const CloudStatusBanner = () => {
  const [health, setHealth] = useState(null);
  const [latency, setLatency] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const checkHealth = async () => {
    setIsRefreshing(true);
    const start = performance.now();
    try {
      // api.baseURL is '/api', so api.get('/health') requests '/api/health'
      const res = await api.get('/health');
      const diff = Math.round(performance.now() - start);
      setLatency(diff);
      setHealth(res.data);
    } catch (err) {
      console.warn('Health check fallback:', err);
      // Secondary attempt directly at /health if proxy differs
      try {
        const fallbackRes = await fetch('/health');
        if (fallbackRes.ok) {
          const data = await fallbackRes.json();
          setLatency(Math.round(performance.now() - start));
          setHealth(data);
          return;
        }
      } catch (e) {
        // ignore
      }
      setLatency(null);
      setHealth({ status: 'degraded', database: 'disconnected', redis: 'fallback_in_memory' });
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const isHealthy = health?.status === 'healthy';
  const isDbConnected = health?.database === 'connected';

  return (
    <div className="bg-slate-900/60 border-b border-slate-800/80 px-4 py-2 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 font-medium text-slate-300">
            <Cloud className="w-3.5 h-3.5 text-indigo-400" />
            <span>Cloud Infrastructure:</span>
          </div>

          {/* System Status */}
          <span
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] font-semibold ${
              isHealthy
                ? 'text-emerald-300 bg-emerald-950/60 border-emerald-500/30'
                : 'text-amber-300 bg-amber-950/60 border-amber-500/30'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                isHealthy ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            ></span>
            {isHealthy ? 'Active & Healthy' : 'Degraded Mode'}
          </span>

          <span className="hidden sm:inline-block text-slate-600">•</span>

          {/* Database Status */}
          <span
            className={`hidden sm:flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] font-medium ${
              isDbConnected
                ? 'text-sky-300 bg-sky-950/40 border-sky-500/20'
                : 'text-rose-300 bg-rose-950/40 border-rose-500/20'
            }`}
          >
            <Server className={`w-3.5 h-3.5 ${isDbConnected ? 'text-sky-400' : 'text-rose-400'}`} />
            <span>DB:</span>{' '}
            <span className="font-semibold">{isDbConnected ? 'Connected' : 'Error'}</span>
          </span>

          <span className="hidden md:inline-block text-slate-600">•</span>

          {/* Cache Status */}
          <span className="hidden md:flex items-center gap-1 text-slate-300">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Cache:</span>{' '}
            <span className="text-amber-300 font-medium">
              {health?.redis === 'connected' ? 'Redis Cloud Engine' : 'In-Memory Engine'}
            </span>
          </span>
        </div>

        <div className="flex items-center gap-3">
          {latency !== null && (
            <div className="flex items-center gap-1.5 bg-slate-800/80 px-2.5 py-0.5 rounded-lg border border-slate-700/60 font-mono text-slate-300 text-[11px]">
              <span
                className={`w-2 h-2 rounded-full ${latency < 120 ? 'bg-emerald-400' : 'bg-amber-400'}`}
              ></span>
              <span>{latency}ms API Latency</span>
            </div>
          )}
          <button
            onClick={checkHealth}
            disabled={isRefreshing}
            className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors cursor-pointer"
            title="Refresh cloud health status"
          >
            <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
            <span className="hidden sm:inline font-medium">Diagnostics</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CloudStatusBanner;
