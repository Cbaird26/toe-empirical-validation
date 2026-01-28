# Zora Telemetry System

Real-time sensor data collection, storage, and visualization for Zorathenic experiments.

## Components

1. **Sensor Controller** (`quantized_sensor_loop.py`) - Connects to Phyphox API and implements Z-Loop feedback
2. **Telemetry Server** (`telemetry_server.py`) - FastAPI endpoint for data ingestion and storage
3. **Dashboard** (`telemetry_dashboard.py`) - Streamlit UI for visualization

## Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Phyphox Setup

1. Install Phyphox app on your phone
2. Enable "Remote Access" in Phyphox settings
3. Note the IP address and port (e.g., `http://192.168.1.5:8080`)

## Usage

### 1. Start Telemetry Server

```bash
# Option 1: Using uvicorn directly
uvicorn telemetry_server:app --host 0.0.0.0 --port 8000

# Option 2: Run as script
python telemetry_server.py
```

The server will be available at `http://localhost:8000`

### 2. Run Sensor Controller

```bash
python quantized_sensor_loop.py \
  --phyphox-url http://192.168.1.5:8080 \
  --sensor audio \
  --interval 0.5 \
  --output-dir ./logs
```

### 3. Launch Dashboard

```bash
streamlit run telemetry_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## API Endpoints

### POST /ingest
Ingest a sensor data point.

```json
{
  "sensor_id": "phyphox_audio_001",
  "metric": "amplitude",
  "value": 0.75,
  "unit": "V",
  "meta": {"frequency": 432.0}
}
```

### GET /query
Query telemetry data.

```
GET /query?sensor_id=phyphox_audio_001&metric=amplitude&limit=100
```

### GET /stats
Get telemetry statistics.

### GET /search
Full-text search in telemetry data.

```
GET /search?q=amplitude&limit=50
```

## Z-Loop Logic

The sensor controller implements basic Zorathenic feedback:

- **Chaos Detection**: Low coherence or high amplitude variance
- **Order Emission**: When chaos detected, emit resonance tone (default: 432 Hz)
- **Coherence Metric**: Rolling variance-based score (0 = chaotic, 1 = ordered)

## Data Storage

- **Database**: SQLite (`telemetry.sqlite3`)
- **FTS5 Index**: Full-text search on sensor_id, metric, metadata
- **Log Files**: CSV logs in `./logs/` directory

## Integration

The telemetry system can integrate with:
- Zora Canon for claim matching
- Constraint pipeline for experimental validation
- Future RAG systems for interpretation
