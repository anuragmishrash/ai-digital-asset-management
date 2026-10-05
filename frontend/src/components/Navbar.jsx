import React from 'react';
import { Database, Sparkles, RefreshCw, Trash2, HardDrive, FileText, Image as ImageIcon, Video as VideoIcon } from 'lucide-react';

export default function Navbar({ stats, indexingStatus, onStartIndexing, onResetIndex }) {
  const isRunning = indexingStatus?.is_running;

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-vault-800/80 bg-vault-950/85">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-accent flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Database className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                AssetVault
              </span>
              <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> AI DAM
              </span>
            </div>
            <p className="text-xs text-vault-400 hidden sm:block">Multimodal Semantic Intelligence</p>
          </div>
        </div>

        {/* System Stats Badges */}
        <div className="hidden md:flex items-center space-x-4 text-xs text-vault-300">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-vault-900/80 border border-vault-800">
            <ImageIcon className="w-3.5 h-3.5 text-blue-400" />
            <span>{stats?.images || 0} Images</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-vault-900/80 border border-vault-800">
            <VideoIcon className="w-3.5 h-3.5 text-purple-400" />
            <span>{stats?.videos || 0} Videos</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-vault-900/80 border border-vault-800">
            <FileText className="w-3.5 h-3.5 text-amber-400" />
            <span>{stats?.pdfs || 0} PDFs</span>
          </div>
        </div>

        {/* Global Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            id="btn-index-dataset"
            onClick={onStartIndexing}
            disabled={isRunning}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 ${
              isRunning
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 cursor-not-allowed'
                : 'bg-brand-600 hover:bg-brand-500 text-white shadow-md shadow-brand-600/25 hover:shadow-brand-500/40 active:scale-95'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${isRunning ? 'animate-spin' : ''}`} />
            <span>{isRunning ? 'Indexing...' : 'Index Dataset'}</span>
          </button>

          <button
            id="btn-reset-index"
            onClick={onResetIndex}
            disabled={isRunning}
            title="Clear all indexed records and vectors"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-vault-400 hover:text-red-400 bg-vault-900/80 hover:bg-red-950/30 border border-vault-800 hover:border-red-800/40 transition-all duration-200 active:scale-95"
          >
            <Trash2 className="w-4 h-4" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>
      </div>
    </header>
  );
}
