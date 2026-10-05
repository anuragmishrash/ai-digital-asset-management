import React, { useState } from 'react';
import { 
  Play, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Loader2, 
  ChevronDown, 
  ChevronUp, 
  Terminal,
  FileCode
} from 'lucide-react';

export default function IndexingPanel({ indexingStatus, onStartIndexing }) {
  const [isExpanded, setIsExpanded] = useState(true);
  
  const isRunning = indexingStatus?.is_running;
  const counts = indexingStatus?.counts || { total: 0, indexed: 0, failed: 0, pending: 0, processing: 0 };
  const logs = indexingStatus?.logs || [];
  const currentFile = indexingStatus?.current_file;

  const total = counts.total || 0;
  const completed = (counts.indexed || 0) + (counts.failed || 0);
  const percent = total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0;

  return (
    <div className="w-full rounded-2xl glass-panel border border-vault-800/90 shadow-xl overflow-hidden">
      {/* Header Bar */}
      <div className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-vault-800/80 bg-vault-900/40">
        <div className="flex items-center space-x-3">
          <div className={`p-2.5 rounded-xl ${isRunning ? 'bg-amber-500/20 text-amber-300' : 'bg-brand-500/20 text-brand-300'}`}>
            {isRunning ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Terminal className="w-5 h-5" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-100">Dataset Ingestion Engine</h3>
              {isRunning && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  Processing
                </span>
              )}
            </div>
            <p className="text-xs text-vault-400">
              {isRunning
                ? `Analyzing: ${currentFile || 'Scanning dataset directory...'}`
                : 'Scans local images, videos, and PDFs into CLIP & Sentence-Transformers vector collections.'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            id="start-indexing-btn"
            onClick={onStartIndexing}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold shadow-md transition-all duration-200 active:scale-95 ${
              isRunning
                ? 'bg-vault-800 text-vault-400 border border-vault-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-emerald-600/20'
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                <span>Indexing in Progress</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>Start Indexing</span>
              </>
            )}
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 rounded-xl bg-vault-900/80 hover:bg-vault-800 text-vault-400 hover:text-slate-200 border border-vault-800 transition"
            title={isExpanded ? "Collapse Feed" : "Expand Feed"}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Progress & Live Feed Body */}
      {isExpanded && (
        <div className="p-4 sm:p-5 space-y-4 bg-vault-950/60">
          {/* Progress Bar */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs font-medium">
              <span className="text-vault-300">
                Processed <span className="text-slate-100 font-bold">{completed}</span> of <span className="text-slate-100 font-bold">{total}</span> files
              </span>
              <span className="text-brand-400 font-bold">{percent}%</span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-vault-900 border border-vault-800/80 overflow-hidden relative">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  isRunning
                    ? 'bg-gradient-to-r from-brand-500 via-brand-accent to-emerald-400 animate-pulse'
                    : 'bg-emerald-500'
                }`}
                style={{ width: `${percent}%` }}
              />
            </div>
          </div>

          {/* Real-time Activity Feed / Logs */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-medium text-vault-400">
              <span>Live Ingestion Feed</span>
              <span>{logs.length} entries</span>
            </div>

            <div className="h-44 overflow-y-auto space-y-1.5 p-3 rounded-xl bg-vault-900/90 border border-vault-800 font-mono text-xs">
              {logs.length === 0 ? (
                <div className="h-full flex items-center justify-center text-vault-500 text-xs italic">
                  No indexing events yet. Click "Start Indexing" to scan dataset.
                </div>
              ) : (
                logs.map((log, idx) => {
                  let badgeColor = "text-vault-400 bg-vault-800";
                  let Icon = FileCode;

                  if (log.level === 'success') {
                    badgeColor = "text-emerald-400 bg-emerald-950/60 border border-emerald-800/40";
                    Icon = CheckCircle;
                  } else if (log.level === 'error') {
                    badgeColor = "text-red-400 bg-red-950/60 border border-red-800/40";
                    Icon = XCircle;
                  } else if (log.level === 'warning') {
                    badgeColor = "text-amber-400 bg-amber-950/60 border border-amber-800/40";
                    Icon = AlertCircle;
                  }

                  return (
                    <div
                      key={idx}
                      className="flex items-start gap-2.5 py-1 px-2 rounded hover:bg-vault-800/50 transition-colors"
                    >
                      <span className="text-[11px] text-vault-500 whitespace-nowrap">{log.time}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase ${badgeColor}`}>
                        {log.level}
                      </span>
                      <span className="text-slate-300 break-all">{log.message}</span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
