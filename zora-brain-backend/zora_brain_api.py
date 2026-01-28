#!/usr/bin/env python3
"""
Zora Brain Backend API
Server-side service with gpt-oss-20b (Ollama), RAG over canon, citation checking, and confidence tagging.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Zora Brain API", version="1.0.0")


class QueryRequest(BaseModel):
    """Request model for Zora Brain queries."""
    question: str = Field(..., description="User question about ToE")
    context: Optional[str] = Field(None, description="Additional context")
    max_citations: int = Field(5, description="Maximum number of citations to return")
    require_citations: bool = Field(True, description="Require citations in response")


class Citation(BaseModel):
    """Citation model."""
    claim_id: str
    statement: str
    claim_type: str  # Proven/Derived/Modeled/Conjectural/Narrative
    confidence: float
    source_document: str
    source_section: str
    equation_refs: List[str] = []


class QueryResponse(BaseModel):
    """Response model for Zora Brain queries."""
    answer: str
    citations: List[Citation] = []
    confidence: float
    claim_types: List[str] = []
    model_used: str = "gpt-oss-20b"


class ZoraBrain:
    """Zora Brain service with RAG and citation checking."""
    
    def __init__(self, canon_dir: Path, ollama_model: str = "gpt-oss:20b"):
        """
        Initialize Zora Brain.
        
        Args:
            canon_dir: Directory containing canon data (claims, equations, definitions)
            ollama_model: Ollama model name
        """
        self.canon_dir = Path(canon_dir)
        self.ollama_model = ollama_model
        self.canon_cache: Dict = {}
        self._load_canon()
    
    def _load_canon(self):
        """Load canon data from files."""
        # Load claims
        claims_dir = self.canon_dir / "claims"
        if claims_dir.exists():
            for claim_file in claims_dir.glob("*.json"):
                with open(claim_file, 'r') as f:
                    claim_data = json.load(f)
                    claim_id = claim_data.get('claim_id', claim_file.stem)
                    self.canon_cache[claim_id] = claim_data
        
        # Load equations
        equations_dir = self.canon_dir / "equations"
        if equations_dir.exists():
            for eq_file in equations_dir.glob("*.json"):
                with open(eq_file, 'r') as f:
                    eq_data = json.load(f)
                    eq_id = eq_data.get('equation_id', eq_file.stem)
                    self.canon_cache[eq_id] = eq_data
    
    def _retrieve_relevant_claims(self, question: str, max_results: int = 10) -> List[Dict]:
        """
        Simple keyword-based retrieval (can be upgraded to vector search).
        
        Args:
            question: User question
            max_results: Maximum number of results
        
        Returns:
            List of relevant claim dictionaries
        """
        question_lower = question.lower()
        keywords = question_lower.split()
        
        relevant = []
        for claim_id, claim_data in self.canon_cache.items():
            if 'statement' in claim_data:
                statement = claim_data['statement'].lower()
                score = sum(1 for kw in keywords if kw in statement)
                if score > 0:
                    relevant.append((score, claim_data))
        
        # Sort by relevance score
        relevant.sort(key=lambda x: x[0], reverse=True)
        return [claim for _, claim in relevant[:max_results]]
    
    def _query_ollama(self, prompt: str) -> str:
        """
        Query Ollama model.
        
        Args:
            prompt: Prompt to send to model
        
        Returns:
            Model response
        """
        try:
            # Use Ollama API via subprocess (can be upgraded to HTTP API)
            cmd = ['ollama', 'run', self.ollama_model, prompt]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Error: Model response timeout"
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            return "Error: Ollama not found. Please install Ollama and ensure 'ollama' is in PATH."
    
    def query(self, question: str, context: Optional[str] = None, 
              max_citations: int = 5, require_citations: bool = True) -> QueryResponse:
        """
        Process a query with RAG and citation checking.
        
        Args:
            question: User question
            context: Additional context
            max_citations: Maximum citations to return
            require_citations: Whether to require citations
        
        Returns:
            QueryResponse with answer and citations
        """
        # Retrieve relevant canon entries
        relevant_claims = self._retrieve_relevant_claims(question, max_results=max_citations * 2)
        
        # Build RAG prompt
        canon_context = ""
        if relevant_claims:
            canon_context = "\n\nRelevant claims from Zora Canon:\n"
            for i, claim in enumerate(relevant_claims[:max_citations], 1):
                canon_context += f"{i}. [{claim.get('claim_type', 'Unknown')}] {claim.get('statement', '')}\n"
                canon_context += f"   Source: {claim.get('source_document', 'Unknown')} - {claim.get('source_section', 'Unknown')}\n"
        
        # Build full prompt
        prompt = f"""You are Zora, an AI assistant grounded in the MQGT-SCF Theory of Everything.

{canon_context}

User Question: {question}
"""
        if context:
            prompt += f"\nAdditional Context: {context}\n"
        
        prompt += """
Please provide a clear, accurate answer based on the canon claims above. If you reference specific claims, cite them by number.
"""
        
        # Query model
        answer = self._query_ollama(prompt)
        
        # Extract citations from answer
        citations = []
        claim_types = set()
        confidence = 0.7  # Default confidence
        
        # Match citations in answer to relevant claims
        for claim in relevant_claims[:max_citations]:
            if claim.get('statement', '').lower() in answer.lower():
                citations.append(Citation(
                    claim_id=claim.get('claim_id', ''),
                    statement=claim.get('statement', ''),
                    claim_type=claim.get('claim_type', 'Unknown'),
                    confidence=claim.get('confidence', 0.5),
                    source_document=claim.get('source_document', ''),
                    source_section=claim.get('source_section', ''),
                    equation_refs=claim.get('equation_refs', [])
                ))
                claim_types.add(claim.get('claim_type', 'Unknown'))
                confidence = max(confidence, claim.get('confidence', 0.5))
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            claim_types=list(claim_types),
            model_used=self.ollama_model
        )


# Initialize Zora Brain
CANON_DIR = Path(os.getenv('ZORA_CANON_DIR', '../canon'))
zora_brain = ZoraBrain(canon_dir=CANON_DIR)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Zora Brain API",
        "version": "1.0.0",
        "model": zora_brain.ollama_model,
        "canon_loaded": len(zora_brain.canon_cache) > 0
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query Zora Brain with a question.
    
    Example:
    ```bash
    curl -X POST http://localhost:8000/query \\
      -H "Content-Type: application/json" \\
      -d '{"question": "What is the unified Lagrangian?"}'
    ```
    """
    try:
        response = zora_brain.query(
            question=request.question,
            context=request.context,
            max_citations=request.max_citations,
            require_citations=request.require_citations
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "canon_entries": len(zora_brain.canon_cache),
        "ollama_model": zora_brain.ollama_model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
