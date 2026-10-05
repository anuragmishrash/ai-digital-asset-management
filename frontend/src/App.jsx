import React, { useState, useEffect, useCallback, useRef } from 'react';
import Navbar from './components/Navbar';
import SearchBar from './components/SearchBar';
import FilterPanel from './components/FilterPanel';
import IndexingPanel from './components/IndexingPanel';
import ResultsGrid from './components/ResultsGrid';
import PreviewModal from './components/PreviewModal';
import { 
  searchAssets, 
  startIndexing, 
  getIndexingStatus, 
  resetIndex, 
  getSystemStats 
} from './api/client';

export default function App() {
  const [query, setQuery] = useState('');
  const [activeSearchQuery, setActiveSearchQuery] = useState('');
  const [fileType, setFileType] = useState('all');
  const [sortBy, setSortBy] = useState('relevance');
  
  const [assets, setAssets] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  
  const [indexingStatus, setIndexingStatus] = useState(null);
  const [stats, setStats] = useState(null);
  const pollTimerRef = useRef(null);

  // Fetch Stats
  const refreshStats = async () => {
    try {
      const data = await getSystemStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  // Execute Search or Browse
  const handleSearch = useCallback(async (searchQuery = query, typeFilter = fileType, sort = sortBy) => {
    setIsLoading(true);
    try {
      const data = await searchAssets({
        q: searchQuery,
        type: typeFilter,
        limit: 40,
        sort: sort
      });
      setAssets(data.results || []);
      setActiveSearchQuery(searchQuery);
    } catch (err) {
      console.error('Search error:', err);
      setAssets([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, fileType, sortBy]);

  // Poll Indexing Status
  const fetchStatus = useCallback(async () => {
    try {
      const statusData = await getIndexingStatus();
      setIndexingStatus(statusData);
      
      // If indexing finished, refresh search results and stats
      if (!statusData.is_running && indexingStatus?.is_running) {
        handleSearch(query, fileType, sortBy);
        refreshStats();
      }
      return statusData;
    } catch (err) {
      console.error('Status fetch error:', err);
      return null;
    }
  }, [handleSearch, indexingStatus?.is_running, query, fileType, sortBy]);

  // Initial Data Load
  useEffect(() => {
    handleSearch('', 'all', 'relevance');
    refreshStats();
    fetchStatus();
  }, []);

  // Filter or Sort Change Handler
  useEffect(() => {
    handleSearch(query, fileType, sortBy);
  }, [fileType, sortBy]);

  // Polling management: Poll every 3 seconds if indexing is running
  useEffect(() => {
    if (indexingStatus?.is_running) {
      pollTimerRef.current = setInterval(() => {
        fetchStatus();
      }, 3000);
    } else {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    }
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [indexingStatus?.is_running, fetchStatus]);

  // Actions
  const handleStartIndexing = async () => {
    try {
      await startIndexing();
      const status = await fetchStatus();
      setIndexingStatus(status);
    } catch (err) {
      console.error('Failed to start indexing:', err);
    }
  };

  const handleResetIndex = async () => {
    if (window.confirm('Are you sure you want to reset all indexed vectors and metadata? You will need to re-index the dataset.')) {
      try {
        await resetIndex();
        await fetchStatus();
        await refreshStats();
        handleSearch('', 'all', 'relevance');
      } catch (err) {
        console.error('Failed to reset index:', err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-vault-950 text-slate-100 flex flex-col selection:bg-brand-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        stats={stats}
        indexingStatus={indexingStatus}
        onStartIndexing={handleStartIndexing}
        onResetIndex={handleResetIndex}
      />

      {/* Main Content Layout */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Left Sidebar Filter Panel */}
          <aside className="lg:col-span-1 space-y-6">
            <div className="sticky top-24 space-y-6">
              <FilterPanel
                fileType={fileType}
                setFileType={setFileType}
                sortBy={sortBy}
                setSortBy={setSortBy}
                indexingStatus={indexingStatus}
                stats={stats}
              />
            </div>
          </aside>

          {/* Main Area */}
          <main className="lg:col-span-3 space-y-6">
            {/* Search Header Area */}
            <div className="space-y-4">
              <SearchBar
                query={query}
                onSearch={(q) => {
                  setQuery(q);
                  handleSearch(q, fileType, sortBy);
                }}
                isLoading={isLoading}
                resultCount={assets.length}
                activeQuery={activeSearchQuery}
              />
            </div>

            {/* Ingestion Engine Status Feed */}
            <IndexingPanel
              indexingStatus={indexingStatus}
              onStartIndexing={handleStartIndexing}
            />

            {/* Assets Grid */}
            <section className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-200">
                  {activeSearchQuery ? 'Search Results' : 'Asset Catalog'}
                </h2>
                <span className="text-xs text-vault-400">
                  Showing {assets.length} items
                </span>
              </div>

              <ResultsGrid
                assets={assets}
                isLoading={isLoading}
                onSelectAsset={(asset) => setSelectedAsset(asset)}
                onStartIndexing={handleStartIndexing}
              />
            </section>
          </main>
        </div>
      </div>

      {/* Detail Preview Modal */}
      {selectedAsset && (
        <PreviewModal
          asset={selectedAsset}
          onClose={() => setSelectedAsset(null)}
        />
      )}
    </div>
  );
}
