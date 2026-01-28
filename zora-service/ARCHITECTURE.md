# Zora-as-a-Service Architecture

Scalable backend for researchers/think tanks with model routing, AirLLM integration, rate limiting, caching, multi-tenant support, and audit trails.

## Overview

Zora-as-a-Service (ZaaS) is a production-ready API service that provides access to the Zora Brain system with enterprise-grade features.

## Architecture Components

### 1. Model Routing Layer

**Purpose:** Route requests to appropriate models based on complexity, cost, and latency requirements.

**Models:**
- **On-device small:** Local models (e.g., Ollama small variants) for fast, low-cost queries
- **Cloud large:** GPT-OSS-120B or similar for complex reasoning
- **Hybrid:** Route simple queries locally, complex queries to cloud

**Implementation:**
```python
class ModelRouter:
    def route(self, query: str, context: Dict) -> str:
        complexity = self.estimate_complexity(query)
        if complexity < threshold:
            return "local_ollama"
        else:
            return "cloud_large"
```

### 2. AirLLM Integration

**Purpose:** Memory-efficient inference for large models via layer-splitting.

**Benefits:**
- Run larger models on constrained VRAM
- Cost-effective inference
- Supports MPS/CUDA/CPU

**Integration:**
- Wrap model calls with AirLLM layer-splitting
- Fallback to standard inference if AirLLM unavailable
- Monitor memory usage and performance

### 3. Rate Limiting

**Purpose:** Prevent abuse and ensure fair resource usage.

**Implementation:**
- Token bucket algorithm
- Per-user rate limits
- Tiered limits (Free/Pro/Team/Enterprise)
- Redis-based distributed rate limiting

**Limits:**
- Free: 10 queries/hour
- Pro: 100 queries/hour
- Team: 1000 queries/hour
- Enterprise: Custom limits

### 4. Caching Layer

**Purpose:** Reduce redundant computation and improve response times.

**Strategy:**
- Cache canonical queries (exact match)
- Cache semantic similarity (vector search)
- TTL-based expiration
- Invalidation on canon updates

**Storage:**
- Redis for hot cache
- PostgreSQL for persistent cache
- Vector DB for semantic similarity

### 5. Multi-Tenant Support

**Purpose:** Isolate data and resources per organization.

**Features:**
- Tenant isolation (database/namespace)
- Per-tenant canon customization
- Usage tracking per tenant
- Billing integration

**Implementation:**
- Tenant ID in all requests
- Row-level security in database
- Separate API keys per tenant

### 6. Audit Trails

**Purpose:** Track all API usage for compliance and debugging.

**Logged Events:**
- All queries (anonymized)
- Model responses
- Citations used
- Performance metrics
- Error logs

**Storage:**
- Time-series database (InfluxDB/TimescaleDB)
- Retention policies
- Compliance exports

## API Design

### Endpoints

#### POST /api/v1/query
Query Zora Brain with authentication.

**Headers:**
- `Authorization: Bearer <api_key>`
- `X-Tenant-ID: <tenant_id>` (optional, from API key)

**Request:**
```json
{
  "question": "What is the unified Lagrangian?",
  "context": "Optional context",
  "max_citations": 5,
  "model_preference": "auto" | "local" | "cloud"
}
```

**Response:**
```json
{
  "answer": "...",
  "citations": [...],
  "confidence": 0.85,
  "model_used": "gpt-oss-20b",
  "cache_hit": false,
  "query_id": "uuid"
}
```

#### GET /api/v1/health
Health check endpoint.

#### GET /api/v1/stats
Usage statistics (per tenant).

#### POST /api/v1/canon/update
Update canon (Enterprise only).

## Deployment Architecture

### Production Stack

```
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   Load Balancer (NGINX) │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   API Gateway           │
│   - Rate Limiting       │
│   - Authentication      │
│   - Request Routing     │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Application Servers   │
│   - FastAPI/Uvicorn     │
│   - Model Router        │
│   - RAG Engine          │
└──────┬──────────────────┘
       │
┌──────▼──────────────────┐
│   Data Layer            │
│   - PostgreSQL (Canon)  │
│   - Redis (Cache)       │
│   - Vector DB (RAG)     │
│   - InfluxDB (Audit)    │
└─────────────────────────┘
```

### Scaling Strategy

- **Horizontal:** Add more API servers behind load balancer
- **Vertical:** Scale model inference servers independently
- **Caching:** Aggressive caching to reduce model calls
- **Async:** Background processing for expensive operations

## Security

- API key authentication
- Rate limiting per key
- Input validation and sanitization
- Output filtering (prevent prompt injection)
- Audit logging for compliance
- Tenant isolation

## Monitoring

- **Metrics:** Request rate, latency, error rate, cache hit rate
- **Alerts:** High error rate, rate limit violations, model failures
- **Dashboards:** Grafana for real-time monitoring
- **Logging:** Structured logging (JSON) to centralized log aggregator

## Cost Optimization

- **Caching:** Reduce redundant model calls
- **Model Routing:** Use cheaper models when possible
- **Batch Processing:** Batch similar queries
- **AirLLM:** Reduce memory costs
- **CDN:** Cache static responses

## Roadmap

### Phase 1: MVP (Weeks 1-2)
- Basic API with authentication
- Rate limiting
- Simple caching
- Single model (Ollama)

### Phase 2: Production (Weeks 3-4)
- Multi-tenant support
- Advanced caching
- Model routing
- Audit trails

### Phase 3: Scale (Weeks 5-6)
- AirLLM integration
- Distributed rate limiting
- Advanced monitoring
- Cost optimization

## Implementation Notes

- Use FastAPI for API framework (already in use)
- Redis for rate limiting and caching
- PostgreSQL for persistent data
- Qdrant/FAISS for vector search
- Docker containers for deployment
- Kubernetes for orchestration (optional)
