import React, { useState } from 'react';
import { 
  X, 
  Copy, 
  Check, 
  Download, 
  ExternalLink, 
  Sparkles, 
  FileText, 
  Image as ImageIcon, 
  Video as VideoIcon, 
  HardDrive, 
  Hash, 
  Calendar,
  AlertCircle
} from 'lucide-react';

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function PreviewModal({ asset, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!asset) return null;

  const {
    id,
    filename,
    filepath,
    file_type,
    extension,
    size_bytes,
    md5_hash,
    status,
    error_message,
    ai_description,
    similarity_percentage,
    created_at,
    file_url
  } = asset;

  const handleCopyPath = () => {
    navigator.clipboard.writeText(filepath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in">
      <div 
        className="relative w-full max-w-5xl max-h-[92vh] glass-panel bg-vault-950 border border-vault-700/80 rounded-3xl shadow-2xl overflow-hidden flex flex-col lg:flex-row"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-vault-900/80 hover:bg-vault-800 text-vault-300 hover:text-white border border-vault-700/60 transition shadow-lg backdrop-blur-md"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Media Preview Stage (Left / Top) */}
        <div className="lg:w-3/5 bg-black/60 flex items-center justify-center p-4 min-h-[320px] lg:min-h-[520px] max-h-[60vh] lg:max-h-full overflow-hidden relative border-b lg:border-b-0 lg:border-r border-vault-800">
          {file_type === 'image' && (
            <img
              src={file_url}
              alt={filename}
              className="max-h-[80vh] w-auto max-w-full object-contain rounded-xl shadow-2xl"
            />
          )}

          {file_type === 'video' && (
            <video
              src={file_url}
              controls
              autoPlay
              playsInline
              className="max-h-[80vh] w-auto max-w-full rounded-xl shadow-2xl bg-black"
            />
          )}

          {file_type === 'pdf' && (
            <div className="w-full h-full min-h-[480px] flex flex-col rounded-xl overflow-hidden bg-vault-900 border border-vault-800">
              <iframe
                src={`${file_url}#toolbar=1&navpanes=0`}
                title={filename}
                className="w-full h-full min-h-[460px] flex-1 rounded-xl"
              />
            </div>
          )}

          {file_type !== 'image' && file_type !== 'video' && file_type !== 'pdf' && (
            <div className="text-center p-8 space-y-3">
              <FileText className="w-16 h-16 text-vault-500 mx-auto" />
              <p className="text-sm text-vault-400">Preview not supported for this file type.</p>
            </div>
          )}
        </div>

        {/* Metadata & AI Inspector Sidebar (Right / Bottom) */}
        <div className="lg:w-2/5 p-6 overflow-y-auto space-y-6 flex flex-col justify-between max-h-[45vh] lg:max-h-[92vh]">
          <div className="space-y-5">
            {/* Title & Status */}
            <div className="space-y-2 pr-8">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider bg-brand-500/20 text-brand-300 border border-brand-500/30">
                  {file_type}
                </span>
                {similarity_percentage !== undefined && (
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> {similarity_percentage}% Match
                  </span>
                )}
              </div>
              <h2 className="text-lg font-bold text-slate-100 break-words leading-snug">
                {filename}
              </h2>
            </div>

            {/* AI Generated Content Analysis */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-brand-950/40 to-vault-900/80 border border-brand-500/20 space-y-2">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-brand-300 uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5 text-brand-accent" />
                <span>AI Multimodal Analysis</span>
              </div>
              <p className="text-xs text-slate-200 leading-relaxed">
                {ai_description || 'Asset has not been analyzed or is pending indexing.'}
              </p>
            </div>

            {/* Error Message if Failed */}
            {error_message && (
              <div className="p-3 rounded-xl bg-red-950/60 border border-red-800/60 text-red-300 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold block">Processing Error:</span>
                  <span className="text-red-200">{error_message}</span>
                </div>
              </div>
            )}

            {/* Technical Metadata Properties */}
            <div className="space-y-2.5 text-xs text-vault-300 border-t border-vault-800/80 pt-4">
              <div className="flex justify-between items-center py-1">
                <span className="flex items-center gap-1.5 text-vault-400">
                  <HardDrive className="w-3.5 h-3.5" /> File Size:
                </span>
                <span className="font-medium text-slate-200">{formatBytes(size_bytes)}</span>
              </div>

              <div className="flex justify-between items-center py-1">
                <span className="flex items-center gap-1.5 text-vault-400">
                  <Hash className="w-3.5 h-3.5" /> MD5 Checksum:
                </span>
                <span className="font-mono text-[11px] text-slate-300 truncate max-w-[180px]" title={md5_hash}>
                  {md5_hash || 'N/A'}
                </span>
              </div>

              <div className="flex justify-between items-center py-1">
                <span className="flex items-center gap-1.5 text-vault-400">
                  <Calendar className="w-3.5 h-3.5" /> Added:
                </span>
                <span className="text-slate-200">
                  {created_at ? new Date(created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>

              {/* Local Filepath with Copy Button */}
              <div className="space-y-1.5 pt-2">
                <span className="text-vault-400 block">Local File Location:</span>
                <div className="flex items-center gap-2 p-2 rounded-xl bg-vault-900 border border-vault-800 text-[11px] font-mono text-slate-300">
                  <span className="truncate flex-1" title={filepath}>{filepath}</span>
                  <button
                    onClick={handleCopyPath}
                    className="p-1 hover:bg-vault-800 rounded text-brand-400 hover:text-brand-300 transition"
                    title="Copy File Path"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons Footer */}
          <div className="pt-4 border-t border-vault-800/80 flex items-center gap-3">
            <button
              onClick={handleCopyPath}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-vault-900 hover:bg-vault-800 border border-vault-700 text-xs font-semibold text-slate-200 transition active:scale-95"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4 text-emerald-400" />
                  <span className="text-emerald-400">Path Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  <span>Open File Location</span>
                </>
              )}
            </button>

            <a
              href={file_url}
              target="_blank"
              rel="noreferrer"
              download={filename}
              className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-xs font-semibold shadow-md shadow-brand-600/25 transition active:scale-95"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
