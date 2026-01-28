# Zora Brain Backend API

Server-side service with gpt-oss-20b (Ollama), RAG over canon, citation checking, and confidence tagging.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Ollama is installed and `gpt-oss:20b` is available:
```bash
ollama list | grep gpt-oss
```

3. Set canon directory (optional, defaults to `../canon`):
```bash
export ZORA_CANON_DIR=/path/to/canon
```

## Running

```bash
python zora_brain_api.py
```

Or with uvicorn:
```bash
uvicorn zora_brain_api:app --host 0.0.0.0 --port 8001
```

## API Endpoints

### POST /query
Query Zora Brain with a question.

**Request:**
```json
{
  "question": "What is the unified Lagrangian?",
  "context": "Optional additional context",
  "max_citations": 5,
  "require_citations": true
}
```

**Response:**
```json
{
  "answer": "The unified Lagrangian is...",
  "citations": [
    {
      "claim_id": "CLAIM_001",
      "statement": "...",
      "claim_type": "Derived",
      "confidence": 0.85,
      "source_document": "...",
      "source_section": "...",
      "equation_refs": ["EQ_001"]
    }
  ],
  "confidence": 0.85,
  "claim_types": ["Derived"],
  "model_used": "gpt-oss:20b"
}
```

### GET /health
Health check endpoint.

### GET /
Root endpoint with service info.

## Testing

```bash
# Test query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is consciousness according to the ToE?"}'

# Health check
curl http://localhost:8001/health
```
