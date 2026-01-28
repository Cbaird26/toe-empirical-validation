import { useState, KeyboardEvent } from 'react';

interface ChatInterfaceProps {
  query: string;
  setQuery: (query: string) => void;
  onQuery: () => void;
  loading: boolean;
}

export default function ChatInterface({ query, setQuery, onQuery, loading }: ChatInterfaceProps) {
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !loading) {
      onQuery();
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
      <div className="flex gap-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about the Theory of Everything..."
          className="flex-1 px-4 py-3 bg-white/20 border border-white/30 rounded-lg text-white placeholder-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-400"
          disabled={loading}
        />
        <button
          onClick={onQuery}
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors"
        >
          {loading ? 'Querying...' : 'Ask'}
        </button>
      </div>
      
      <div className="mt-4 text-sm text-purple-200">
        <p>Example questions:</p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>"What is the unified Lagrangian?"</li>
          <li>"Explain consciousness according to the ToE"</li>
          <li>"What are the empirical predictions?"</li>
        </ul>
      </div>
    </div>
  );
}
