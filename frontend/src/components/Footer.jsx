import React from 'react';
import { Layers, Cloud, Heart, GitBranch, Cpu, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/80 pt-12 pb-8 text-slate-400 text-xs mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand info */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">
                <Layers className="w-4 h-4" />
              </div>
              <span className="font-bold text-sm text-white">CloudRec Systems</span>
            </div>
            <p className="text-slate-400 leading-relaxed">
              Demonstrating scalable cloud-native recommendation engines combining content-based feature extraction and collaborative user matrices.
            </p>
          </div>

          {/* Architecture Concepts */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Cloud Stack</h4>
            <ul className="space-y-1.5 text-slate-400">
              <li className="flex items-center gap-1.5"><Cloud className="w-3.5 h-3.5 text-sky-400" /> Stateless FastAPI Backend</li>
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-indigo-400" /> Scikit-Learn TF-IDF Vectors</li>
              <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> PostgreSQL & SQLAlchemy ORM</li>
              <li className="flex items-center gap-1.5"><Layers className="w-3.5 h-3.5 text-amber-400" /> Redis Dynamic Caching Tier</li>
            </ul>
          </div>

          {/* Navigation */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Discovery</h4>
            <ul className="space-y-1.5">
              <li><Link to="/items" className="hover:text-indigo-400 transition-colors">Catalog & Categories</Link></li>
              <li><Link to="/recommendations" className="hover:text-indigo-400 transition-colors">Recommendation Lab</Link></li>
              <li><Link to="/onboarding" className="hover:text-indigo-400 transition-colors">Onboarding Preferences</Link></li>
              <li><a href="/docs" target="_blank" rel="noreferrer" className="hover:text-indigo-400 transition-colors">FastAPI Swagger Docs</a></li>
            </ul>
          </div>

          {/* Engine Parameters */}
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-200">Engine Tuning</h4>
            <p className="text-slate-400">
              Active configuration uses 60% TF-IDF Cosine Content similarity and 40% User-User collaborative filtering matrix factor.
            </p>
            <div className="pt-1">
              <span className="px-2 py-1 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono text-indigo-300">
                α = 0.60 | 1-α = 0.40
              </span>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-900 flex flex-col sm:flex-row items-center justify-between gap-4 text-slate-500">
          <p>© 2026 Cloud-Based Recommendation Systems. Production Full-Stack Architecture.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              All Cloud Services Operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
