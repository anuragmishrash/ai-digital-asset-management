import React from 'react';
import { 
  Layers, 
  Image as ImageIcon, 
  Video as VideoIcon, 
  FileText, 
  ArrowUpDown, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  Activity,
  SlidersHorizontal
} from 'lucide-react';

const FILE_TYPES = [
  { id: 'all', label: 'All Files', icon: Layers },
  { id: 'image', label: 'Images', icon: ImageIcon },
  { id: 'video', label: 'Videos', icon: VideoIcon },
  { id: 'pdf', label: 'PDFs', icon: FileText },
];

const SORT_OPTIONS = [
  { id: 'relevance', label: 'AI Relevance' },
  { id: 'date', label: 'Date Added' },
  { id: 'file_size', label: 'File Size' },
];

export default function FilterPanel({
  fileType,
  setFileType,
  sortBy,
  setSortBy,
  indexingStatus,
  stats
}) {
  const counts = indexingStatus?.counts || {};

  return (
    <div className="w-full space-y-6">
      {/* File Type Filter */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-vault-400">
          <SlidersHorizontal className="w-3.5 h-3.5 text-brand-400" />
          <span>Filter by Type</span>
        </div>

        <div className="space-y-1.5">
          {FILE_TYPES.map((type) => {
            const Icon = type.icon;
            const isSelected = fileType === type.id;
            
            // Determine count
            let typeCount = stats?.total_assets || 0;
            if (type.id === 'image') typeCount = stats?.images || 0;
            if (type.id === 'video') typeCount = stats?.videos || 0;
            if (type.id === 'pdf') typeCount = stats?.pdfs || 0;

            return (
              <label
                key={type.id}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl cursor-pointer transition-all duration-150 border ${
                  isSelected
                    ? 'bg-brand-600/15 border-brand-500/50 text-white font-medium shadow-sm'
                    : 'bg-vault-900/40 border-vault-800/80 hover:bg-vault-900/80 text-vault-300 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <input
                    type="radio"
                    name="file_type_filter"
                    value={type.id}
                    checked={isSelected}
                    onChange={() => setFileType(type.id)}
                    className="sr-only"
                  />
                  <Icon className={`w-4 h-4 ${isSelected ? 'text-brand-400' : 'text-vault-400'}`} />
                  <span className="text-sm">{type.label}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  isSelected ? 'bg-brand-500/20 text-brand-300' : 'bg-vault-800 text-vault-400'
                }`}>
                  {typeCount}
                </span>
              </label>
            );
          })}
        </div>
      </div>

      {/* Sort By Filter */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-vault-400">
          <ArrowUpDown className="w-3.5 h-3.5 text-brand-400" />
          <span>Sort Order</span>
        </div>

        <div className="grid grid-cols-1 gap-1.5">
          {SORT_OPTIONS.map((sort) => {
            const isSelected = sortBy === sort.id;
            return (
              <button
                key={sort.id}
                type="button"
                onClick={() => setSortBy(sort.id)}
                className={`w-full text-left px-3.5 py-2 rounded-lg text-xs font-medium transition-all border ${
                  isSelected
                    ? 'bg-vault-800 border-vault-700 text-brand-300'
                    : 'bg-vault-900/40 border-transparent hover:bg-vault-900/80 text-vault-400 hover:text-slate-200'
                }`}
              >
                {sort.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Indexing Status Summary Box */}
      <div className="p-4 rounded-2xl bg-vault-900/60 border border-vault-800/80 space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold text-vault-300">
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-brand-accent" />
            <span>Vault Status</span>
          </div>
          {indexingStatus?.is_running && (
            <span className="flex items-center gap-1 text-[11px] text-amber-400 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span> Active
            </span>
          )}
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between text-vault-300">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Indexed</span>
            </div>
            <span className="font-semibold text-emerald-400">{counts.indexed || 0}</span>
          </div>

          <div className="flex items-center justify-between text-vault-300">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Pending</span>
            </div>
            <span className="font-semibold text-amber-400">{counts.pending || 0}</span>
          </div>

          <div className="flex items-center justify-between text-vault-300">
            <div className="flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5 text-red-400" />
              <span>Failed</span>
            </div>
            <span className="font-semibold text-red-400">{counts.failed || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
