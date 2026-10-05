import React, { useState, useEffect } from 'react';
import { Search, Sparkles, X, Loader2, Compass } from 'lucide-react';

const SUGGESTIONS = [
  "a woman standing with a cat",
  "residential project brochure",
  "construction activity",
  "nature landscape with mountains",
  "financial quarterly earnings report"
];

export default function SearchBar({ query, onSearch, isLoading, resultCount, activeQuery }) {
  const [inputValue, setInputValue] = useState(query || '');

  useEffect(() => {
    setInputValue(query || '');
  }, [query]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(inputValue);
  };

  const handleClear = () => {
    setInputValue('');
    onSearch('');
  };

  const handleChipClick = (suggestion) => {
    setInputValue(suggestion);
    onSearch(suggestion);
  };

  return (
    <div className="w-full max-w-3xl mx-auto space-y-3">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-vault-400">
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin text-brand-400" />
          ) : (
            <Search className="w-5 h-5 text-brand-400" />
          )}
        </div>

        <input
          id="search-input"
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder='Try "a woman standing with a cat" or "brochures related to residential projects"...'
          className="w-full pl-12 pr-28 py-3.5 bg-vault-900/90 hover:bg-vault-900 border border-vault-700/80 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/25 rounded-2xl text-slate-100 placeholder-vault-400 text-base shadow-xl transition-all duration-200 outline-none backdrop-blur-md"
        />

        <div className="absolute inset-y-0 right-0 pr-2 flex items-center space-x-1.5">
          {inputValue && (
            <button
              type="button"
              onClick={handleClear}
              className="p-1.5 text-vault-400 hover:text-slate-200 rounded-lg hover:bg-vault-800 transition"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            id="search-submit-btn"
            type="submit"
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white rounded-xl text-sm font-semibold shadow-md shadow-brand-500/25 transition duration-200 active:scale-95 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>Search</span>
          </button>
        </div>
      </form>

      {/* Suggested Natural Language Queries */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-medium text-vault-400 flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-brand-400" /> Suggestions:
        </span>
        {SUGGESTIONS.map((suggestion, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleChipClick(suggestion)}
            className="text-xs px-2.5 py-1 rounded-lg bg-vault-900/70 hover:bg-vault-800 text-slate-300 hover:text-white border border-vault-800 hover:border-vault-700 transition duration-150"
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Results Header Info */}
      {activeQuery && (
        <div className="flex items-center justify-between text-xs text-vault-400 px-1 pt-1">
          <span>
            Found <span className="font-semibold text-slate-200">{resultCount}</span> assets matching "{activeQuery}"
          </span>
          <button
            onClick={handleClear}
            className="text-brand-400 hover:text-brand-300 hover:underline"
          >
            Clear Search
          </button>
        </div>
      )}
    </div>
  );
}
