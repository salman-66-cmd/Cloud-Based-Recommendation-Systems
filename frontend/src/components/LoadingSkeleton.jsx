import React from 'react';

const LoadingSkeleton = ({ count = 6, type = 'card' }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden animate-pulse flex flex-col justify-between h-[360px]"
        >
          <div className="h-44 bg-slate-800/80 w-full" />
          <div className="p-4 space-y-3 flex-1">
            <div className="flex justify-between">
              <div className="h-3 bg-slate-800 rounded w-1/3" />
              <div className="h-3 bg-slate-800 rounded w-1/4" />
            </div>
            <div className="h-5 bg-slate-800 rounded w-3/4" />
            <div className="space-y-1.5">
              <div className="h-3 bg-slate-800 rounded w-full" />
              <div className="h-3 bg-slate-800 rounded w-5/6" />
            </div>
            <div className="flex gap-2 pt-2">
              <div className="h-4 bg-slate-800 rounded w-12" />
              <div className="h-4 bg-slate-800 rounded w-16" />
            </div>
          </div>
          <div className="p-4 border-t border-slate-800/80 flex justify-between items-center">
            <div className="h-4 bg-slate-800 rounded w-16" />
            <div className="h-8 bg-slate-800 rounded w-20" />
          </div>
        </div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;
