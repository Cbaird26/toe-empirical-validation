interface Citation {
  claim_id: string;
  statement: string;
  claim_type: string;
  confidence: number;
  source_document: string;
  source_section: string;
  equation_refs: string[];
}

interface CitationDisplayProps {
  citations: Citation[];
}

export default function CitationDisplay({ citations }: CitationDisplayProps) {
  const getClaimTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'Proven': 'bg-green-600/50',
      'Derived': 'bg-blue-600/50',
      'Modeled': 'bg-yellow-600/50',
      'Conjectural': 'bg-orange-600/50',
      'Narrative': 'bg-purple-600/50'
    };
    return colors[type] || 'bg-gray-600/50';
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6 border border-white/20">
      <h2 className="text-2xl font-semibold text-white mb-4">
        📚 Sources & Citations
      </h2>
      
      <div className="space-y-4">
        {citations.map((citation, idx) => (
          <div
            key={citation.claim_id || idx}
            className="bg-white/5 rounded-lg p-4 border border-white/10"
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold text-white ${getClaimTypeColor(citation.claim_type)}`}>
                {citation.claim_type}
              </span>
              <span className="text-sm text-purple-300">
                {Math.round(citation.confidence * 100)}% confidence
              </span>
            </div>
            
            <p className="text-purple-100 mb-2">{citation.statement}</p>
            
            <div className="text-sm text-purple-300">
              <p>
                <span className="font-semibold">Source:</span> {citation.source_document}
              </p>
              <p>
                <span className="font-semibold">Section:</span> {citation.source_section}
              </p>
              {citation.equation_refs && citation.equation_refs.length > 0 && (
                <p>
                  <span className="font-semibold">Equations:</span> {citation.equation_refs.join(', ')}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
