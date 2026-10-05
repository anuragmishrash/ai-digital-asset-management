import React, { useState } from 'react';
import { 
  Play, 
  FileText, 
  Image as ImageIcon, 
  Video as VideoIcon, 
  Sparkles, 
  Clock, 
  Layers, 
  AlertTriangle,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function AssetCard({ asset, onSelect }) {
  const [imgError, setImgError] = useState(false);
  
  const {
    id,
    filename,
    file_type,
    extension,
    size_bytes,
    status,
    ai_description,
    similarity_percentage = 100,
    thumbnail_url,
    error_message
  } = asset;

  // Score color gradient based on percentage
  const getScoreBadge = () => {
    if (similarity_percentage >= 80) {
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    } else if (similarity_percentage >= 60) {
      return 'bg-brand-500/20 text-brand-300 border-brand-500/40';
    } else if (similarity_percentage >= 40) {
      return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    }
    return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
  };

  const getTypeBadge = () => {
    switch (file_type) {
      case 'image':
        return { label: 'Image', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30', Icon: ImageIcon };
      case 'video':
        return { label: 'Video', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30', Icon: VideoIcon };
      case 'pdf':
        return { label: 'PDF', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30', Icon: FileText };
      default:
        return { label: extension || 'File', color: 'bg-slate-500/20 text-slate-300 border-slate-500/30', Icon: Layers };
    }
  };

  const typeInfo = getTypeBadge();
  const TypeIcon = typeInfo.Icon;

  return (
    <div
      onClick={() => onSelect(asset)}
      className="group relative rounded-2xl glass-card overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl flex flex-col justify-between"
    >
      {/* Top Media Thumbnail Area */}
      <div className="relative aspect-video w-full bg-vault-900 overflow-hidden flex items-center justify-center">
        {imgError || !thumbnail_url ? (
          <div className="flex flex-col items-center justify-center p-4 text-vault-500">
            <TypeIcon className="w-10 h-10 mb-1 opacity-50" />
            <span className="text-[11px] uppercase font-semibold">{file_type}</span>
          </div>
        ) : (
          <img
            src={thumbnail_url}
            alt={filename}
            onError={() => setImgError(true)}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
        )}

        {/* Video Overlay Indicator */}
        {file_type === 'video' && (
          <div className="absolute inset-0 bg-black/30 flex items-center justify-center group-hover:bg-black/15 transition-all">
            <div className="w-10 h-10 rounded-full bg-brand-600/90 text-white flex items-center justify-center shadow-lg shadow-black/50 group-hover:scale-110 transition-transform">
              <Play className="w-5 h-5 fill-current ml-0.5" />
            </div>
          </div>
        )}

        {/* Badges Overlay */}
        <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5">
          <span className={`px-2 py-0.5 rounded-md text-[11px] font-semibold uppercase tracking-wider border backdrop-blur-md flex items-center gap-1 ${typeInfo.color}`}>
            <TypeIcon className="w-3 h-3" />
            {typeInfo.label}
          </span>
        </div>

        {similarity_percentage !== undefined && (
          <div className="absolute top-2.5 right-2.5">
            <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold border backdrop-blur-md flex items-center gap-1 ${getScoreBadge()}`}>
              <Sparkles className="w-2.5 h-2.5" />
              {similarity_percentage}% Match
            </span>
          </div>
        )}

        {/* Failed / Partially Indexed Warning Stamp */}
        {status === 'failed' && (
          <div className="absolute bottom-2 left-2 right-2 px-2 py-1 rounded bg-red-950/90 border border-red-800 text-red-300 text-[10px] flex items-center gap-1 font-medium">
            <AlertTriangle className="w-3 h-3 text-red-400 shrink-0" />
            <span className="truncate">{error_message || 'Indexing Failed'}</span>
          </div>
        )}

        {status === 'partially_indexed' && (
          <div className="absolute bottom-2 left-2 right-2 px-2 py-1 rounded bg-amber-950/90 border border-amber-800 text-amber-300 text-[10px] flex items-center gap-1 font-medium">
            <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
            <span className="truncate">Scanned Document (No text)</span>
          </div>
        )}
      </div>

      {/* Card Body Info */}
      <div className="p-4 space-y-2.5 flex-1 flex flex-col justify-between">
        <div className="space-y-1">
          <h4 className="text-sm font-semibold text-slate-100 group-hover:text-brand-300 transition-colors truncate" title={filename}>
            {filename}
          </h4>
          
          <p className="text-xs text-vault-400 line-clamp-2 leading-relaxed">
            {ai_description || 'No AI description available.'}
          </p>
        </div>

        {/* Card Footer Metadata */}
        <div className="pt-2 border-t border-vault-800/80 flex items-center justify-between text-[11px] text-vault-400">
          <span>{formatBytes(size_bytes)}</span>
          <span className="flex items-center gap-1 group-hover:text-brand-400 transition-colors">
            Inspect <ExternalLink className="w-3 h-3" />
          </span>
        </div>
      </div>
    </div>
  );
}
