#!/usr/bin/env python3
"""
Quantized Sensor Loop - Zorathenation Controller
Connects to Phyphox API, reads sensor data, and implements Z-Loop feedback logic.
"""

import argparse
import csv
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


class ZorathenaController:
    """Controller for Zorathenic sensor feedback loops."""
    
    def __init__(self, phyphox_url: str, output_dir: Path):
        """
        Initialize controller.
        
        Args:
            phyphox_url: Base URL for Phyphox API (e.g., http://192.168.1.5:8080)
            output_dir: Directory for logging data
        """
        self.phyphox_url = phyphox_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        self.log_file = self.output_dir / f'zora_feedback_log_{timestamp}.csv'
        
        # Initialize CSV log
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_utc', 'sensor_type', 'value', 'amplitude', 
                'frequency', 'coherence_score', 'action_taken', 'tone_frequency'
            ])
        
        # Z-Loop parameters
        self.chaos_threshold = 0.5  # Amplitude threshold for "chaos"
        self.order_frequency = 432.0  # Hz - resonance frequency for "order"
        self.coherence_window = 10  # Number of samples for coherence calculation
        
        # State
        self.sensor_history: List[Dict] = []
        self.last_action_time = 0.0
    
    def get_sensor_data(self, sensor_type: str = 'audio') -> Optional[Dict]:
        """
        Poll Phyphox API for sensor data.
        
        Args:
            sensor_type: Type of sensor ('audio', 'magnetometer', 'accelerometer')
        
        Returns:
            Dictionary with sensor data or None if error
        """
        try:
            # Phyphox API endpoint structure
            if sensor_type == 'audio':
                endpoint = f"{self.phyphox_url}/get?audio"
            elif sensor_type == 'magnetometer':
                endpoint = f"{self.phyphox_url}/get?magnetometer"
            elif sensor_type == 'accelerometer':
                endpoint = f"{self.phyphox_url}/get?accelerometer"
            else:
                raise ValueError(f"Unknown sensor type: {sensor_type}")
            
            response = requests.get(endpoint, timeout=2.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant values
            if sensor_type == 'audio':
                # Audio amplitude
                buffer = data.get('buffer', {}).get('audio', [])
                if buffer:
                    amplitude = max(buffer) if isinstance(buffer, list) else float(buffer)
                    return {
                        'sensor_type': 'audio',
                        'amplitude': amplitude,
                        'value': amplitude,
                        'raw_data': buffer
                    }
            
            elif sensor_type == 'magnetometer':
                # Magnetic field strength
                x = data.get('buffer', {}).get('magnetometerX', [0])
                y = data.get('buffer', {}).get('magnetometerY', [0])
                z = data.get('buffer', {}).get('magnetometerZ', [0])
                
                if isinstance(x, list):
                    x, y, z = x[0] if x else 0, y[0] if y else 0, z[0] if z else 0
                
                magnitude = math.sqrt(x**2 + y**2 + z**2)
                return {
                    'sensor_type': 'magnetometer',
                    'magnitude': magnitude,
                    'value': magnitude,
                    'x': x, 'y': y, 'z': z
                }
            
            elif sensor_type == 'accelerometer':
                # Acceleration magnitude
                x = data.get('buffer', {}).get('accelerometerX', [0])
                y = data.get('buffer', {}).get('accelerometerY', [0])
                z = data.get('buffer', {}).get('accelerometerZ', [0])
                
                if isinstance(x, list):
                    x, y, z = x[0] if x else 0, y[0] if y else 0, z[0] if z else 0
                
                magnitude = math.sqrt(x**2 + y**2 + z**2)
                return {
                    'sensor_type': 'accelerometer',
                    'magnitude': magnitude,
                    'value': magnitude,
                    'x': x, 'y': y, 'z': z
                }
            
            return None
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sensor data: {e}")
            return None
        except Exception as e:
            print(f"Error processing sensor data: {e}")
            return None
    
    def compute_coherence_score(self, history: List[Dict]) -> float:
        """
        Compute coherence score from sensor history.
        
        Lower variance = higher coherence (more ordered).
        """
        if len(history) < 2:
            return 0.5  # Neutral
        
        values = [h['value'] for h in history[-self.coherence_window:]]
        
        if not values:
            return 0.5
        
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        
        # Normalize to [0, 1] where 1 = perfect coherence
        # Use inverse of normalized variance
        max_variance = max(values) - min(values) if values else 1.0
        if max_variance == 0:
            return 1.0
        
        coherence = 1.0 - min(1.0, variance / max_variance)
        return coherence
    
    def zora_logic(self, sensor_data: Dict) -> Tuple[str, Optional[float]]:
        """
        Core Z-Loop logic: map chaos to order.
        
        Args:
            sensor_data: Current sensor reading
        
        Returns:
            Tuple (action_description, tone_frequency)
        """
        # Add to history
        self.sensor_history.append(sensor_data)
        
        # Keep only recent history
        if len(self.sensor_history) > self.coherence_window * 2:
            self.sensor_history = self.sensor_history[-self.coherence_window * 2:]
        
        # Compute coherence
        coherence = self.compute_coherence_score(self.sensor_history)
        
        # Get amplitude (normalized)
        amplitude = sensor_data.get('amplitude', sensor_data.get('value', 0))
        
        # Z-Loop decision: if chaos (low coherence or high amplitude), emit order (tone)
        if amplitude > self.chaos_threshold or coherence < 0.3:
            action = "chaos_detected_emit_order"
            tone_freq = self.order_frequency
        else:
            action = "stable_no_action"
            tone_freq = None
        
        return action, tone_freq
    
    def control_tone(self, frequency: float, amplitude: float = 0.5):
        """
        Send tone control command to Phyphox.
        
        Args:
            frequency: Tone frequency in Hz
            amplitude: Tone amplitude [0, 1]
        """
        try:
            # Phyphox tone generator control
            endpoint = f"{self.phyphox_url}/control"
            payload = {
                'tone': {
                    'frequency': frequency,
                    'amplitude': amplitude,
                    'duration': 0.1  # Short pulse
                }
            }
            
            response = requests.post(endpoint, json=payload, timeout=1.0)
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not control tone: {e}")
            # Non-fatal - continue logging
    
    def log_data(self, sensor_data: Dict, action: str, tone_freq: Optional[float]):
        """Log sensor data and actions to CSV."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        amplitude = sensor_data.get('amplitude', sensor_data.get('value', 0))
        coherence = self.compute_coherence_score(self.sensor_history)
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                sensor_data.get('sensor_type', 'unknown'),
                sensor_data.get('value', 0),
                amplitude,
                0.0,  # Frequency (if applicable)
                coherence,
                action,
                tone_freq if tone_freq else ''
            ])
    
    def run_loop(self, sensor_type: str = 'audio', interval: float = 0.5, 
                duration: Optional[float] = None):
        """
        Run main sensor loop.
        
        Args:
            sensor_type: Type of sensor to read
            interval: Polling interval in seconds
            duration: Total duration to run (None = run indefinitely)
        """
        print(f"Starting Zorathenation Controller")
        print(f"  Phyphox URL: {self.phyphox_url}")
        print(f"  Sensor: {sensor_type}")
        print(f"  Log file: {self.log_file}")
        print(f"  Press Ctrl+C to stop\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - start_time) > duration:
                    break
                
                # Get sensor data
                sensor_data = self.get_sensor_data(sensor_type)
                
                if sensor_data:
                    # Run Z-Loop logic
                    action, tone_freq = self.zora_logic(sensor_data)
                    
                    # Control tone if needed
                    if tone_freq:
                        self.control_tone(tone_freq)
                    
                    # Log data
                    self.log_data(sensor_data, action, tone_freq)
                    
                    # Print status
                    coherence = self.compute_coherence_score(self.sensor_history)
                    print(f"[{iteration:04d}] "
                          f"Value: {sensor_data.get('value', 0):.4f}, "
                          f"Coherence: {coherence:.3f}, "
                          f"Action: {action}")
                
                iteration += 1
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\nStopping controller...")
        
        print(f"\n✓ Loop complete. Logged {iteration} iterations to {self.log_file}")


def main():
    parser = argparse.ArgumentParser(description="Zorathenation Sensor Controller")
    parser.add_argument("--phyphox-url", required=True,
                       help="Phyphox API URL (e.g., http://192.168.1.5:8080)")
    parser.add_argument("--sensor", default="audio",
                       choices=['audio', 'magnetometer', 'accelerometer'],
                       help="Sensor type to read")
    parser.add_argument("--interval", type=float, default=0.5,
                       help="Polling interval in seconds")
    parser.add_argument("--duration", type=float, default=None,
                       help="Duration to run in seconds (None = run indefinitely)")
    parser.add_argument("--output-dir", default="./telemetry/logs",
                       help="Output directory for logs")
    
    args = parser.parse_args()
    
    controller = ZorathenaController(args.phyphox_url, Path(args.output_dir))
    controller.run_loop(
        sensor_type=args.sensor,
        interval=args.interval,
        duration=args.duration
    )


if __name__ == '__main__':
    main()
