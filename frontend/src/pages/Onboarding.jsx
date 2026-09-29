import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Check,
  Cpu,
  Server,
  GitBranch,
  Database,
  ShieldCheck,
  HardDrive,
  Zap,
  Globe,
  Radio,
  Activity,
  ArrowRight,
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';

const AVAILABLE_CATEGORIES = [
  { name: 'Artificial Intelligence & ML', icon: Cpu, desc: 'LLMs, Vector Search, Computer Vision, MLOps' },
  { name: 'Cloud Compute & Containers', icon: Server, desc: 'Kubernetes, Bare Metal GPUs, MicroVMs, Auto-scaling' },
  { name: 'DevOps & CI/CD Pipelines', icon: GitBranch, desc: 'Terraform IaC, GitOps Argo, Secret Vaults' },
  { name: 'Big Data & Real-Time Analytics', icon: Database, desc: 'Lakehouse, Apache Kafka, ClickHouse, Trino' },
  { name: 'Cybersecurity & IAM', icon: ShieldCheck, desc: 'Zero-Trust, CloudGuard WAF, KMS, SIEM Threat' },
  { name: 'Database & Distributed Storage', icon: HardDrive, desc: 'Aurora SQL, Redis Enterprise, S3 Glacier, Supabase' },
  { name: 'Serverless & Microservices', icon: Zap, desc: 'Lambda Edge, Workers, EventBridge, Temporal' },
  { name: 'Web & Modern Cloud Frontend', icon: Globe, desc: 'Vercel Edge, Netlify Jamstack, Headless CMS' },
  { name: 'IoT & Edge Computing', icon: Radio, desc: 'Edge Gateways, HiveMQ MQTT, Balena Fleet' },
  { name: 'Observability & APM', icon: Activity, desc: 'Datadog, Grafana Cloud, OpenTelemetry, Sentry' },
];

const CLOUD_PROVIDERS = ['AWS', 'Google Cloud', 'Microsoft Azure', 'Cloudflare', 'Multi-Cloud'];

const POPULAR_TAGS = [
  'kubernetes',
  'llm',
  'vector-db',
  'zero-trust',
  'serverless',
  'postgres',
  'redis',
  'kafka',
  'edge',
  'finops',
  'iac',
  'wasm'
];

const Onboarding = () => {
  const { user, refreshUser } = useAuth();
  const { addToast } = useToast();
  const navigate = useNavigate();

  const [selectedCategories, setSelectedCategories] = useState([]);
  const [selectedProviders, setSelectedProviders] = useState(['Multi-Cloud']);
  const [selectedTags, setSelectedTags] = useState(['kubernetes', 'serverless']);
  const [loading, setLoading] = useState(false);

  // Fetch current preferences if user already has some
  useEffect(() => {
    const fetchExisting = async () => {
      try {
        const res = await api.get('/preferences');
        if (res.data) {
          if (res.data.preferred_categories?.length) {
            setSelectedCategories(res.data.preferred_categories);
          }
          if (res.data.preferred_cloud_providers?.length) {
            setSelectedProviders(res.data.preferred_cloud_providers);
          }
          if (res.data.preferred_tags?.length) {
            setSelectedTags(res.data.preferred_tags);
          }
        }
      } catch (err) {
        // default empty
      }
    };
    fetchExisting();
  }, []);

  const toggleCategory = (catName) => {
    setSelectedCategories((prev) =>
      prev.includes(catName) ? prev.filter((c) => c !== catName) : [...prev, catName]
    );
  };

  const toggleProvider = (provider) => {
    setSelectedProviders((prev) =>
      prev.includes(provider) ? prev.filter((p) => p !== provider) : [...prev, provider]
    );
  };

  const toggleTag = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSave = async () => {
    if (selectedCategories.length === 0) {
      addToast('Please select at least one cloud category to personalize recommendations', 'info');
      return;
    }

    setLoading(true);
    try {
      await api.post('/preferences', {
        preferred_categories: selectedCategories,
        preferred_cloud_providers: selectedProviders,
        preferred_tags: selectedTags,
      });
      await refreshUser();
      addToast('Preferences saved! Recommendations customized.', 'success');
      navigate('/dashboard');
    } catch (err) {
      addToast('Failed to save preferences', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-10">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-xs font-semibold text-indigo-300">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Cold-Start Personalization Protocol</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Select Your Technical Focus
        </h1>
        <p className="text-sm text-slate-400 max-w-xl mx-auto">
          Our recommendation engine calibrates its TF-IDF vector space based on your selected architectural domains and cloud environments.
        </p>
      </div>

      {/* Category selection grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Primary Cloud Domains ({selectedCategories.length} selected)
          </h3>
          <span className="text-xs text-slate-400">Select at least 1 domain</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {AVAILABLE_CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedCategories.includes(cat.name);

            return (
              <div
                key={cat.name}
                onClick={() => toggleCategory(cat.name)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer flex items-start gap-4 ${
                  isSelected
                    ? 'bg-indigo-950/60 border-indigo-500 shadow-lg shadow-indigo-500/15'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40'
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                    isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold text-white">{cat.name}</h4>
                    <div
                      className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                        isSelected
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'border-slate-700 bg-slate-800'
                      }`}
                    >
                      {isSelected && <Check className="w-3 h-3" />}
                    </div>
                  </div>
                  <p className="text-xs text-slate-400">{cat.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cloud Provider selector */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Preferred Cloud Providers
        </h3>
        <div className="flex flex-wrap gap-2.5">
          {CLOUD_PROVIDERS.map((provider) => {
            const isSelected = selectedProviders.includes(provider);
            return (
              <button
                key={provider}
                type="button"
                onClick={() => toggleProvider(provider)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-indigo-600 border-indigo-500 text-white shadow-md'
                    : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {provider}
              </button>
            );
          })}
        </div>
      </div>

      {/* Technical Tags */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Core Architectural Keywords
        </h3>
        <div className="flex flex-wrap gap-2">
          {POPULAR_TAGS.map((tag) => {
            const isSelected = selectedTags.includes(tag);
            return (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-sky-500/20 border-sky-400 text-sky-200'
                    : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                #{tag}
              </button>
            );
          })}
        </div>
      </div>

      {/* Bottom Save Action */}
      <div className="pt-6 border-t border-slate-800 flex items-center justify-between">
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="text-xs font-semibold text-slate-400 hover:text-white"
        >
          Skip for now
        </button>

        <button
          type="button"
          onClick={handleSave}
          disabled={loading || selectedCategories.length === 0}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl font-bold text-sm shadow-xl shadow-indigo-600/30 flex items-center gap-2 transition-all cursor-pointer"
        >
          {loading ? 'Calibrating Engine...' : 'Save & Launch Recommendations'}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default Onboarding;
