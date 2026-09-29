import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Search,
  Filter,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  Compass,
  X,
  RefreshCw,
} from 'lucide-react';
import api from '../services/api';
import ItemCard from '../components/ItemCard';
import LoadingSkeleton from '../components/LoadingSkeleton';

const CLOUD_PROVIDERS = ['All', 'AWS', 'Google Cloud', 'Microsoft Azure', 'Cloudflare', 'Multi-Cloud'];

const SORT_OPTIONS = [
  { value: 'popular', label: 'Most Popular' },
  { value: 'rating', label: 'Highest Rated' },
  { value: 'newest', label: 'Newest Added' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
];

const ItemsCatalog = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [items, setItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Filters state from URL or default
  const page = parseInt(searchParams.get('page') || '1', 10);
  const search = searchParams.get('search') || '';
  const category = searchParams.get('category') || '';
  const provider = searchParams.get('provider') || 'All';
  const sortBy = searchParams.get('sort_by') || 'popular';

  const [searchInput, setSearchInput] = useState(search);

  // Fetch categories once
  useEffect(() => {
    const fetchCats = async () => {
      try {
        const res = await api.get('/categories');
        setCategories(res.data || []);
      } catch (e) {
        console.error('Failed to load categories:', e);
      }
    };
    fetchCats();
  }, []);

  // Fetch items whenever params change
  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        params.set('page', page.toString());
        params.set('page_size', '12');
        if (search) params.set('search', search);
        if (category) params.set('category', category);
        if (provider && provider !== 'All') params.set('cloud_provider', provider);
        params.set('sort_by', sortBy);

        const res = await api.get(`/items?${params.toString()}`);
        setItems(res.data.items || []);
        setTotal(res.data.total || 0);
        setTotalPages(res.data.total_pages || 1);
      } catch (err) {
        console.error('Failed to fetch items:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, [page, search, category, provider, sortBy]);

  const updateParam = (key, value) => {
    const nextParams = new URLSearchParams(searchParams);
    if (value && value !== 'All') {
      nextParams.set(key, value);
    } else {
      nextParams.delete(key);
    }
    // reset to page 1 on filter change
    if (key !== 'page') {
      nextParams.set('page', '1');
    }
    setSearchParams(nextParams);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    updateParam('search', searchInput.trim());
  };

  const clearAllFilters = () => {
    setSearchInput('');
    setSearchParams(new URLSearchParams());
  };

  return (
    <div className="space-y-8 py-6">
      {/* Catalog Title Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Compass className="w-7 h-7 text-sky-400" />
            Cloud & AI Architecture Catalog
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Explore 100+ production cloud services, foundational models, databases, and DevOps tools.
          </p>
        </div>

        <div className="text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3.5 py-1.5 rounded-xl self-start sm:self-auto">
          Showing <strong className="text-white">{items.length}</strong> of{' '}
          <strong className="text-white">{total}</strong> cloud solutions
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 sm:p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {/* Keyword Search */}
          <form onSubmit={handleSearchSubmit} className="md:col-span-2 relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by keyword, tag, or technology..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full pl-10 pr-20 py-2.5 bg-slate-950 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
            >
              Filter
            </button>
          </form>

          {/* Cloud Provider Filter */}
          <div>
            <select
              value={provider}
              onChange={(e) => updateParam('provider', e.target.value)}
              className="w-full py-2.5 px-3 bg-slate-950 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              {CLOUD_PROVIDERS.map((p) => (
                <option key={p} value={p}>
                  {p === 'All' ? 'All Cloud Providers' : p}
                </option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => updateParam('sort_by', e.target.value)}
              className="w-full py-2.5 px-3 bg-slate-950 border border-slate-700/80 rounded-xl text-xs sm:text-sm text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  Sort: {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Category Pills Slider */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 no-scrollbar text-xs">
          <button
            onClick={() => updateParam('category', '')}
            className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-colors cursor-pointer ${
              !category
                ? 'bg-indigo-600 text-white font-semibold'
                : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => updateParam('category', cat.slug)}
              className={`px-3 py-1.5 rounded-lg font-medium whitespace-nowrap transition-colors cursor-pointer ${
                category === cat.slug || category === cat.name
                  ? 'bg-indigo-600 text-white font-semibold'
                  : 'bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        {/* Active Filters Clear Pill */}
        {(search || category || provider !== 'All') && (
          <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <span>Active filters:</span>
              {search && (
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                  Search: "{search}"
                </span>
              )}
              {category && (
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                  Category: {category}
                </span>
              )}
              {provider !== 'All' && (
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                  Provider: {provider}
                </span>
              )}
            </div>
            <button
              onClick={clearAllFilters}
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              Reset all
            </button>
          </div>
        )}
      </div>

      {/* Items Grid */}
      {loading ? (
        <LoadingSkeleton count={12} />
      ) : items.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {items.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </div>
      ) : (
        <div className="p-16 text-center bg-slate-900/40 border border-slate-800 rounded-3xl space-y-4">
          <Compass className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No products found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            No cloud services match your current query or filters. Try adjusting your search keywords or clearing active filters.
          </p>
          <button
            onClick={clearAllFilters}
            className="px-4 py-2 bg-indigo-600 text-white rounded-xl text-xs font-semibold"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-800 pt-6">
          <button
            onClick={() => updateParam('page', (page - 1).toString())}
            disabled={page <= 1}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>

          <div className="text-xs text-slate-400 font-medium">
            Page <strong className="text-white">{page}</strong> of{' '}
            <strong className="text-white">{totalPages}</strong>
          </div>

          <button
            onClick={() => updateParam('page', (page + 1).toString())}
            disabled={page >= totalPages}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

export default ItemsCatalog;
