import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Compass,
  Sparkles,
  LayoutDashboard,
  Heart,
  User,
  Shield,
  Layers,
  BarChart3,
  Package,
  FolderTree,
  Sliders,
  Cpu,
  Zap,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = ({ isOpen, onClose }) => {
  const { isAuthenticated, isAdmin } = useAuth();

  const navLinkClasses = ({ isActive }) =>
    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
      isActive
        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20 font-semibold'
        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
    }`;

  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
        />
      )}

      {/* Sidebar container */}
      <aside
        className={`fixed top-16 bottom-0 left-0 z-40 w-64 bg-slate-950/95 border-r border-slate-800/80 p-4 flex flex-col justify-between transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="space-y-6 overflow-y-auto pr-1">
          {/* Main Discovery */}
          <div>
            <div className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
              Cloud Discovery
            </div>
            <div className="space-y-1">
              <NavLink to="/items" onClick={onClose} className={navLinkClasses}>
                <Compass className="w-4 h-4 text-sky-400" />
                Product Catalog
              </NavLink>
              <NavLink to="/recommendations" onClick={onClose} className={navLinkClasses}>
                <Sparkles className="w-4 h-4 text-amber-400" />
                Recommendation Engine
              </NavLink>
            </div>
          </div>

          {/* User Workspace */}
          {isAuthenticated && (
            <div>
              <div className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
                My Workspace
              </div>
              <div className="space-y-1">
                <NavLink to="/dashboard" onClick={onClose} className={navLinkClasses}>
                  <LayoutDashboard className="w-4 h-4 text-indigo-400" />
                  User Dashboard
                </NavLink>
                <NavLink to="/favorites" onClick={onClose} className={navLinkClasses}>
                  <Heart className="w-4 h-4 text-rose-400" />
                  Saved Stack
                </NavLink>
                <NavLink to="/onboarding" onClick={onClose} className={navLinkClasses}>
                  <Sliders className="w-4 h-4 text-emerald-400" />
                  Preferences Onboarding
                </NavLink>
                <NavLink to="/profile" onClick={onClose} className={navLinkClasses}>
                  <User className="w-4 h-4 text-purple-400" />
                  Profile & History
                </NavLink>
              </div>
            </div>
          )}

          {/* Admin Management */}
          {isAdmin && (
            <div>
              <div className="px-3 text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center justify-between mb-2">
                <span>Admin Console</span>
                <Shield className="w-3.5 h-3.5" />
              </div>
              <div className="space-y-1">
                <NavLink to="/admin" end onClick={onClose} className={navLinkClasses}>
                  <Layers className="w-4 h-4 text-indigo-400" />
                  Admin Overview
                </NavLink>
                <NavLink to="/admin/analytics" onClick={onClose} className={navLinkClasses}>
                  <BarChart3 className="w-4 h-4 text-emerald-400" />
                  Deep Analytics
                </NavLink>
                <NavLink to="/admin/items" onClick={onClose} className={navLinkClasses}>
                  <Package className="w-4 h-4 text-sky-400" />
                  Manage Items
                </NavLink>
                <NavLink to="/admin/categories" onClick={onClose} className={navLinkClasses}>
                  <FolderTree className="w-4 h-4 text-amber-400" />
                  Manage Categories
                </NavLink>
                <NavLink to="/admin/users" onClick={onClose} className={navLinkClasses}>
                  <User className="w-4 h-4 text-purple-400" />
                  Manage Users
                </NavLink>
              </div>
            </div>
          )}

          {/* Cloud Simulation Box */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 space-y-2">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Hybrid Rec Formula</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed font-mono bg-slate-950 p-2 rounded border border-slate-800">
              Score = 0.6·Content + 0.4·Collab
            </p>
            <p className="text-[10px] text-slate-500">
              Real-time cosine similarity & neighbor matrix factor.
            </p>
          </div>
        </div>

        {/* Bottom footer badge */}
        <div className="pt-3 border-t border-slate-800/60 text-xs text-slate-500 flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Cloud Rec v1.0</span>
          </div>
          <span className="text-[10px] bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">SaaS Ready</span>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
