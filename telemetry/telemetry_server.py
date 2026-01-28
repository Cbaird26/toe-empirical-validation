#!/usr/bin/env python3
"""
Telemetry Server - FastAPI endpoint for sensor data ingestion
Stores sensor packets in SQLite with FTS5 index for fast search.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# Database path
DB_PATH = Path(__file__).parent / "telemetry.sqlite3"

app = FastAPI(
    title="Zora Telemetry Server",
    description="Sensor data ingestion and storage for Zorathenic experiments",
    version="0.1.0"
)


class SensorPoint(BaseModel):
    """Sensor data point model."""
    sensor_id: str = Field(..., description="Unique sensor identifier")
    t_utc: Optional[datetime] = None
    metric: str = Field(..., description="Metric name (e.g., 'amplitude', 'magnitude')")
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    meta: Dict = Field(default_factory=dict, description="Additional metadata")


def init_db():
    """Initialize SQLite database with telemetry table and FTS5 index."""
    with sqlite3.connect(DB_PATH) as con:
        # Main telemetry table
        con.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                t_utc TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                meta_json TEXT,
                INDEX idx_sensor_time (sensor_id, t_utc),
                INDEX idx_metric (metric)
            )
        """)
        
        # FTS5 full-text search table
        con.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS telemetry_fts USING fts5(
                sensor_id,
                metric,
                meta_json,
                content='telemetry',
                content_rowid='id'
            )
        """)
        
        con.commit()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print(f"Telemetry server started. Database: {DB_PATH}")


@app.post("/ingest", response_model=Dict[str, bool])
async def ingest(p: SensorPoint):
    """
    Ingest a sensor data point.
    
    Stores the data point in SQLite and updates FTS5 index.
    """
    t_utc = p.t_utc or datetime.now(timezone.utc)
    
    try:
        with sqlite3.connect(DB_PATH) as con:
            # Insert into main table
            cursor = con.execute(
                """
                INSERT INTO telemetry(sensor_id, t_utc, metric, value, unit, meta_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    p.sensor_id,
                    t_utc.isoformat(),
                    p.metric,
                    p.value,
                    p.unit,
                    str(p.meta) if p.meta else None
                )
            )
            
            row_id = cursor.lastrowid
            
            # Update FTS5 index
            con.execute(
                """
                INSERT INTO telemetry_fts(rowid, sensor_id, metric, meta_json)
                VALUES (?, ?, ?, ?)
                """,
                (row_id, p.sensor_id, p.metric, str(p.meta) if p.meta else None)
            )
            
            con.commit()
        
        return {"ok": True, "id": row_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/query", response_model=List[Dict])
async def query(
    sensor_id: Optional[str] = None,
    metric: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
):
    """
    Query telemetry data.
    
    Args:
        sensor_id: Filter by sensor ID
        metric: Filter by metric name
        limit: Maximum number of results
        offset: Offset for pagination
    """
    conditions = []
    params = []
    
    if sensor_id:
        conditions.append("sensor_id = ?")
        params.append(sensor_id)
    
    if metric:
        conditions.append("metric = ?")
        params.append(metric)
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query_sql = f"""
        SELECT id, sensor_id, t_utc, metric, value, unit, meta_json
        FROM telemetry
        {where_clause}
        ORDER BY t_utc DESC
        LIMIT ? OFFSET ?
    """
    
    params.extend([limit, offset])
    
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute(query_sql, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "sensor_id": row["sensor_id"],
                    "t_utc": row["t_utc"],
                    "metric": row["metric"],
                    "value": row["value"],
                    "unit": row["unit"],
                    "meta": eval(row["meta_json"]) if row["meta_json"] else {}
                })
            
            return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")


@app.get("/stats", response_model=Dict)
async def stats():
    """Get telemetry statistics."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            # Total records
            total = con.execute("SELECT COUNT(*) FROM telemetry").fetchone()[0]
            
            # Unique sensors
            sensors = con.execute("SELECT COUNT(DISTINCT sensor_id) FROM telemetry").fetchone()[0]
            
            # Unique metrics
            metrics = con.execute("SELECT COUNT(DISTINCT metric) FROM telemetry").fetchone()[0]
            
            # Time range
            time_range = con.execute(
                "SELECT MIN(t_utc), MAX(t_utc) FROM telemetry"
            ).fetchone()
            
            return {
                "total_records": total,
                "unique_sensors": sensors,
                "unique_metrics": metrics,
                "time_range": {
                    "min": time_range[0],
                    "max": time_range[1]
                } if time_range[0] else None
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@app.get("/search", response_model=List[Dict])
async def search(q: str, limit: int = 100):
    """
    Full-text search in telemetry data.
    
    Uses FTS5 index for fast searching across sensor_id, metric, and metadata.
    """
    try:
        with sqlite3.connect(DB_PATH) as con:
            con.row_factory = sqlite3.Row
            cursor = con.execute(
                """
                SELECT t.id, t.sensor_id, t.t_utc, t.metric, t.value, t.unit, t.meta_json
                FROM telemetry t
                JOIN telemetry_fts fts ON t.id = fts.rowid
                WHERE telemetry_fts MATCH ?
                ORDER BY t.t_utc DESC
                LIMIT ?
                """,
                (q, limit)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "sensor_id": row["sensor_id"],
                    "t_utc": row["t_utc"],
                    "metric": row["metric"],
                    "value": row["value"],
                    "unit": row["unit"],
                    "meta": eval(row["meta_json"]) if row["meta_json"] else {}
                })
            
            return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
