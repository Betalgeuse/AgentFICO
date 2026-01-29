import { useState } from 'react';
import { useScore } from '../hooks/useScore';
import { AgentSearch } from '../components/AgentSearch';
import { ScoreCard } from '../components/ScoreCard';
import { SampleAgents } from '../components/SampleAgents';
import { AgentList } from '../components/AgentList';
import { AlertCircle, Loader2, X } from 'lucide-react';
import { SAMPLE_8004_AGENTS } from '../data/sampleAgents';

export function Dashboard() {
  const [address, setAddress] = useState<string | null>(null);
  const { data: score, isLoading, error } = useScore(address);

  const handleSearch = (newAddress: string) => {
    setAddress(newAddress);
    // Scroll to top when searching
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleClose = () => {
    setAddress(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-8 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-2">AgentFICO</h1>
          <p className="text-indigo-200 text-lg">AI Agent Credit Scoring System</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Search */}
        <AgentSearch onSearch={handleSearch} isLoading={isLoading} />

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <span className="ml-2 text-gray-600">Loading score...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="max-w-md mx-auto bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-center text-red-700">
              <AlertCircle className="w-5 h-5 mr-2" />
              <span className="font-semibold">Error</span>
            </div>
            <p className="text-red-600 mt-1 text-sm">
              {error.message || 'Failed to fetch score. Make sure the API server is running.'}
            </p>
          </div>
        )}

        {/* Score Card */}
        {score && !isLoading && (
          <div className="animate-fade-in relative">
            <button
              onClick={handleClose}
              className="absolute -top-2 -right-2 bg-gray-200 hover:bg-gray-300 rounded-full p-1 z-10"
            >
              <X className="w-4 h-4 text-gray-600" />
            </button>
            <ScoreCard score={score} />
          </div>
        )}

        {/* Quick Test Agents */}
        {!score && !isLoading && (
          <SampleAgents onSelect={handleSearch} />
        )}

        {/* Info Section */}
        <div className="mt-8 max-w-2xl mx-auto text-center text-gray-500 text-sm">
          <p className="mb-2">
            AgentFICO evaluates AI agents based on three key metrics:
          </p>
          <div className="flex justify-center gap-6 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600">40%</div>
              <div className="text-xs">TX Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">40%</div>
              <div className="text-xs">x402 Profitability</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-violet-600">20%</div>
              <div className="text-xs">ERC-8004 Stability</div>
            </div>
          </div>
        </div>

        {/* Agent Registry List */}
        <AgentList agents={SAMPLE_8004_AGENTS} onSelectAgent={handleSearch} />
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-gray-400 text-sm">
        <p>AgentFICO - AI Agent Credit Scoring Infrastructure</p>
        <p className="mt-1">
          Data from{' '}
          <a href="https://www.8004scan.io" target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:underline">
            8004scan.io
          </a>
        </p>
      </footer>
    </div>
  );
}
