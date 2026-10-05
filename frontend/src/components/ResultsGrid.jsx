import React from 'react';
import AssetCard from './AssetCard';
import { SearchX, Sparkles, FolderSearch } from 'lucide-react';

export default function ResultsGrid({ assets, isLoading, onSelectAsset, onStartIndexing }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
          <div key={n} className="rounded-2xl glass-card overflow-hidden animate-pulse">
            <div className="aspect-video bg-vault-900/80 w-full" />
            <div className="p-4 space-y-3">
              <div className="h-4 bg-vault-800 rounded w-3/4" />
              <div className="h-3 bg-vault-800/60 rounded w-full" />
              <div className="h-3 bg-vault-800/40 rounded w-2/3" />
              <div className="pt-2 flex justify-between">
                <div className="h-3 bg-vault-800/50 rounded w-16" />
                <div className="h-3 bg-vault-800/50 rounded w-12" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!assets || assets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-3xl glass-panel border border-vault-800/80 my-4 space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-vault-900 border border-vault-800 flex items-center justify-center text-vault-400">
          <SearchX className="w-8 h-8 text-brand-400" />
        </div>
        <div className="space-y-1 max-w-md">
          <h3 className="text-lg font-bold text-slate-100">No matching assets found</h3>
          <p className="text-sm text-vault-400">
            Try searching with natural language like "woman with cat", "luxury residential brochure", or click "Index Dataset" to scan new media files.
          </p>
        </div>
        <button
          onClick={onStartIndexing}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-600/20 transition-all active:scale-95"
        >
          <Sparkles className="w-4 h-4" />
          <span>Scan & Index Dataset</span>
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
      {assets.map((asset) => (
        <AssetCard
          key={asset.id}
          asset={asset}
          onSelect={onSelectAsset}
        />
      ))}
    </div>
  );
}
