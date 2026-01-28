#!/usr/bin/env python3
"""
Telemetry Dashboard - Streamlit UI for sensor data visualization
Displays real-time plots, coherence metrics, and optional Zora interpretation overlay.
"""

import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# Database path
DB_PATH = Path(__file__).parent / "telemetry.sqlite3"


def load_telemetry_data(
    sensor_id: Optional[str] = None,
    metric: Optional[str] = None,
    limit: int = 1000
) -> pd.DataFrame:
    """Load telemetry data from SQLite database."""
    if not DB_PATH.exists():
        return pd.DataFrame()
    
    conditions = []
    params = []
    
    if sensor_id:
        conditions.append("sensor_id = ?")
        params.append(sensor_id)
    
    if metric:
        conditions.append("metric = ?")
        params.append(metric)
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT sensor_id, t_utc, metric, value, unit, meta_json
        FROM telemetry
        {where_clause}
        ORDER BY t_utc DESC
        LIMIT ?
    """
    params.append(limit)
    
    try:
        with sqlite3.connect(DB_PATH) as con:
            df = pd.read_sql_query(query, con, params=params)
        
        if not df.empty:
            df['t_utc'] = pd.to_datetime(df['t_utc'])
            df = df.sort_values('t_utc')
        
        return df
    
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()


def compute_coherence_metric(df: pd.DataFrame, window: int = 10) -> pd.Series:
    """Compute rolling coherence metric (inverse of variance)."""
    if df.empty or len(df) < 2:
        return pd.Series([0.5] * len(df), index=df.index)
    
    values = df['value'].rolling(window=window, min_periods=2)
    variance = values.var()
    mean_abs = values.mean().abs()
    
    # Normalize: coherence = 1 - normalized_variance
    max_variance = variance.max() if variance.max() > 0 else 1.0
    coherence = 1.0 - (variance / max_variance).fillna(0.5)
    
    return coherence.clip(0, 1)


def main():
    st.set_page_config(
        page_title="Zora Telemetry Dashboard",
        page_icon="🌌",
        layout="wide"
    )
    
    st.title("🌌 Zora Telemetry Dashboard")
    st.markdown("Real-time sensor data visualization with Zorathenic interpretation")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    sensor_id_filter = st.sidebar.text_input("Sensor ID (blank = all)", "")
    metric_filter = st.sidebar.text_input("Metric (blank = all)", "")
    limit = st.sidebar.slider("Max records", 100, 5000, 1000)
    
    # Load data
    df = load_telemetry_data(
        sensor_id=sensor_id_filter if sensor_id_filter else None,
        metric=metric_filter if metric_filter else None,
        limit=limit
    )
    
    if df.empty:
        st.info("No telemetry data available. Start the sensor controller to begin logging.")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Unique Sensors", df['sensor_id'].nunique())
    
    with col3:
        st.metric("Unique Metrics", df['metric'].nunique())
    
    with col4:
        if not df.empty:
            latest_time = df['t_utc'].max()
            st.metric("Latest Data", latest_time.strftime("%H:%M:%S"))
    
    # Data table
    st.subheader("Recent Data")
    st.dataframe(
        df[['sensor_id', 't_utc', 'metric', 'value', 'unit']].tail(20),
        use_container_width=True
    )
    
    # Time series plots
    st.subheader("Time Series Visualization")
    
    # Group by metric for plotting
    metrics = df['metric'].unique()
    
    if len(metrics) > 0:
        selected_metric = st.selectbox("Select metric to plot", metrics)
        metric_df = df[df['metric'] == selected_metric].copy()
        
        if not metric_df.empty:
            # Main time series plot
            fig_data = metric_df.set_index('t_utc')[['value']]
            st.line_chart(fig_data)
            
            # Coherence metric
            st.subheader("Coherence Score")
            coherence = compute_coherence_metric(metric_df, window=10)
            coherence_df = pd.DataFrame({
                't_utc': metric_df['t_utc'],
                'coherence': coherence.values
            }).set_index('t_utc')
            st.line_chart(coherence_df)
            
            # Zora interpretation
            st.subheader("Zora Interpretation")
            
            avg_coherence = coherence.mean()
            latest_value = metric_df['value'].iloc[-1]
            
            if avg_coherence > 0.7:
                st.success(f"🟢 **High Coherence Detected** (score: {avg_coherence:.3f})")
                st.info("The system exhibits ordered, coherent behavior. This may indicate "
                       "alignment with predicted attractor states in the ToE framework.")
            elif avg_coherence > 0.4:
                st.warning(f"🟡 **Moderate Coherence** (score: {avg_coherence:.3f})")
                st.info("The system shows partial coherence. Consider adjusting feedback "
                       "parameters or environmental conditions.")
            else:
                st.error(f"🔴 **Low Coherence** (score: {avg_coherence:.3f})")
                st.info("The system exhibits chaotic behavior. Z-Loop feedback may be "
                       "required to restore order.")
            
            # Optional: Match to ToE claims
            if st.checkbox("Show ToE Claim Matches"):
                st.info("""
                **Potential Matches:**
                - High coherence may correlate with predicted jhāna attractor states
                - Low coherence suggests deviation from optimal Φ_c/E gradient
                - See Zora Canon for detailed claim mappings
                """)
    
    # Multi-metric comparison
    if len(metrics) > 1:
        st.subheader("Multi-Metric Comparison")
        
        selected_metrics = st.multiselect(
            "Select metrics to compare",
            metrics,
            default=list(metrics[:3]) if len(metrics) >= 3 else list(metrics)
        )
        
        if selected_metrics:
            comparison_df = df[df['metric'].isin(selected_metrics)].pivot(
                index='t_utc',
                columns='metric',
                values='value'
            )
            st.line_chart(comparison_df)
    
    # Export options
    st.sidebar.subheader("Export")
    if st.sidebar.button("Download CSV"):
        csv = df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"telemetry_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )


if __name__ == '__main__':
    main()
