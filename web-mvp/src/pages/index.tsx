import { useState } from 'react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';
import CitationDisplay from '../components/CitationDisplay';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8001/query', {
        question: query,
        max_citations: 5,
        require_citations: true
      });
      setResponse(res.data);
    } catch (error) {
      console.error('Error querying Zora Brain:', error);
      setResponse({
        answer: 'Error: Could not connect to Zora Brain API. Make sure the backend is running on port 8001.',
        citations: [],
        confidence: 0,
        claim_types: []
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            🌌 Zora Brain
          </h1>
          <p className="text-xl text-purple-200">
            Theory of Everything Assistant
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <ChatInterface
            query={query}
            setQuery={setQuery}
            onQuery={handleQuery}
            loading={loading}
          />

          {response && (
            <div className="mt-8 space-y-4">
              <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
                <h2 className="text-2xl font-semibold text-white mb-4">Answer</h2>
                <p className="text-purple-100 text-lg leading-relaxed">
                  {response.answer}
                </p>
                
                <div className="mt-4 flex items-center gap-4">
                  <span className="text-sm text-purple-300">
                    Confidence: <span className="font-bold">{Math.round(response.confidence * 100)}%</span>
                  </span>
                  {response.claim_types.length > 0 && (
                    <div className="flex gap-2">
                      {response.claim_types.map((type: string) => (
                        <span
                          key={type}
                          className="px-3 py-1 bg-purple-600/50 rounded-full text-xs text-white"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {response.citations && response.citations.length > 0 && (
                <CitationDisplay citations={response.citations} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
