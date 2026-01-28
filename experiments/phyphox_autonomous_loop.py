#!/usr/bin/env python3
"""
Phyphox Autonomous Modulation Loop
Closed-loop sensor (microphone) → AI processing → actuator (tone generator) with resonance seeking objective.
Enhanced version of quantized_sensor_loop.py with autonomous modulation.
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
import numpy as np


class AutonomousModulationLoop:
    """Autonomous modulation loop for resonance seeking."""
    
    def __init__(self, phyphox_url: str, output_dir: Path):
        """
        Initialize autonomous loop.
        
        Args:
            phyphox_url: Base URL for Phyphox API
            output_dir: Directory for logging
        """
        self.phyphox_url = phyphox_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        self.log_file = self.output_dir / f'autonomous_loop_{timestamp}.csv'
        
        # Initialize CSV log
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp_utc', 'sensor_type', 'amplitude', 'frequency_detected',
                'coherence_score', 'target_frequency', 'tone_frequency', 
                'action', 'resonance_error'
            ])
        
        # Resonance seeking parameters
        self.target_frequencies = [61.31, 7.83, 14.3, 20.8, 27.3, 33.8]  # Schumann harmonics
        self.current_target_idx = 0
        self.resonance_window = 0.5  # Hz tolerance
        self.adaptation_rate = 0.1  # How quickly to adjust frequency
        
        # State
        self.sensor_history: List[Dict] = []
        self.frequency_history: List[float] = []
        self.last_tone_freq = None
    
    def get_audio_spectrum(self) -> Optional[Dict]:
        """
        Get audio spectrum from Phyphox.
        
        Returns:
            Dictionary with frequency spectrum data
        """
        try:
            endpoint = f"{self.phyphox_url}/get?audio"
            response = requests.get(endpoint, timeout=2.0)
            response.raise_for_status()
            data = response.json()
            
            # Extract audio buffer
            buffer = data.get('buffer', {}).get('audio', [])
            if not buffer or len(buffer) < 64:
                return None
            
            # Convert to numpy array for FFT
            audio_data = np.array(buffer, dtype=np.float32)
            
            # Compute FFT
            fft = np.fft.rfft(audio_data)
            frequencies = np.fft.rfftfreq(len(audio_data), d=1.0/44100)  # Assuming 44.1 kHz
            magnitudes = np.abs(fft)
            
            # Find dominant frequency
            dominant_idx = np.argmax(magnitudes[1:]) + 1  # Skip DC component
            dominant_freq = frequencies[dominant_idx]
            
            return {
                'frequencies': frequencies.tolist(),
                'magnitudes': magnitudes.tolist(),
                'dominant_frequency': float(dominant_freq),
                'amplitude': float(np.max(magnitudes)),
                'raw_buffer': buffer[:100]  # First 100 samples for logging
            }
        except Exception as e:
            print(f"Error getting audio spectrum: {e}")
            return None
    
    def compute_coherence(self, spectrum_data: Dict) -> float:
        """
        Compute coherence score from spectrum.
        
        Higher coherence = stronger resonance at target frequency.
        """
        if not spectrum_data:
            return 0.0
        
        target_freq = self.target_frequencies[self.current_target_idx]
        dominant_freq = spectrum_data.get('dominant_frequency', 0)
        
        # Coherence is inverse of frequency error
        freq_error = abs(dominant_freq - target_freq)
        if freq_error < self.resonance_window:
            coherence = 1.0 - (freq_error / self.resonance_window)
        else:
            coherence = 0.0
        
        return coherence
    
    def resonance_seeking_logic(self, spectrum_data: Dict) -> Tuple[str, Optional[float]]:
        """
        Resonance seeking logic: adjust tone to maximize coherence.
        
        Returns:
            Tuple (action_description, tone_frequency)
        """
        if not spectrum_data:
            return "no_data", None
        
        target_freq = self.target_frequencies[self.current_target_idx]
        dominant_freq = spectrum_data.get('dominant_frequency', 0)
        coherence = self.compute_coherence(spectrum_data)
        
        # Resonance seeking: if we're not at target, adjust tone
        freq_error = dominant_freq - target_freq
        
        if abs(freq_error) > self.resonance_window:
            # Adjust tone frequency toward target
            if self.last_tone_freq is None:
                new_tone_freq = target_freq
            else:
                # Adaptive adjustment
                adjustment = freq_error * self.adaptation_rate
                new_tone_freq = self.last_tone_freq + adjustment
                # Clamp to reasonable range
                new_tone_freq = max(20.0, min(200.0, new_tone_freq))
            
            action = f"adjusting_toward_resonance_error_{freq_error:.2f}Hz"
            return action, new_tone_freq
        else:
            # At resonance - maintain or explore next target
            if coherence > 0.8:
                # Strong resonance - cycle to next target
                self.current_target_idx = (self.current_target_idx + 1) % len(self.target_frequencies)
                action = f"resonance_achieved_moving_to_{self.target_frequencies[self.current_target_idx]:.2f}Hz"
                return action, self.target_frequencies[self.current_target_idx]
            else:
                # Maintain current frequency
                action = "maintaining_resonance"
                return action, target_freq
    
    def send_tone(self, frequency: float, amplitude: float = 0.5):
        """
        Send tone control command to Phyphox.
        
        Args:
            frequency: Tone frequency in Hz
            amplitude: Tone amplitude [0, 1]
        """
        try:
            # Phyphox tone generator API
            endpoint = f"{self.phyphox_url}/control"
            payload = {
                'tone': {
                    'frequency': frequency,
                    'amplitude': amplitude,
                    'duration': 0.0  # Continuous
                }
            }
            
            response = requests.post(endpoint, json=payload, timeout=1.0)
            response.raise_for_status()
            self.last_tone_freq = frequency
        except Exception as e:
            print(f"Warning: Could not control tone: {e}")
    
    def log_data(self, spectrum_data: Dict, action: str, tone_freq: Optional[float]):
        """Log data to CSV."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        if spectrum_data:
            dominant_freq = spectrum_data.get('dominant_frequency', 0)
            amplitude = spectrum_data.get('amplitude', 0)
            coherence = self.compute_coherence(spectrum_data)
            target_freq = self.target_frequencies[self.current_target_idx]
            resonance_error = abs(dominant_freq - target_freq)
        else:
            dominant_freq = 0
            amplitude = 0
            coherence = 0
            target_freq = self.target_frequencies[self.current_target_idx]
            resonance_error = 0
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp, 'audio_spectrum', amplitude, dominant_freq,
                coherence, target_freq, tone_freq if tone_freq else '',
                action, resonance_error
            ])
    
    def run(self, duration_seconds: int = 3600, poll_interval: float = 0.1):
        """
        Run autonomous modulation loop.
        
        Args:
            duration_seconds: Total duration in seconds
            poll_interval: Polling interval in seconds
        """
        print(f"Starting autonomous modulation loop...")
        print(f"Target frequencies: {self.target_frequencies}")
        print(f"Logging to: {self.log_file}")
        print(f"Duration: {duration_seconds} seconds")
        print("Press Ctrl+C to stop early\n")
        
        start_time = time.time()
        iteration = 0
        
        try:
            while time.time() - start_time < duration_seconds:
                iteration += 1
                
                # Get audio spectrum
                spectrum_data = self.get_audio_spectrum()
                
                # Compute resonance seeking action
                action, tone_freq = self.resonance_seeking_logic(spectrum_data)
                
                # Send tone command
                if tone_freq:
                    self.send_tone(tone_freq, amplitude=0.5)
                
                # Log data
                self.log_data(spectrum_data, action, tone_freq)
                
                # Print status every 10 iterations
                if iteration % 10 == 0:
                    if spectrum_data:
                        print(f"[{iteration}] Dominant: {spectrum_data.get('dominant_frequency', 0):.2f} Hz | "
                              f"Target: {self.target_frequencies[self.current_target_idx]:.2f} Hz | "
                              f"Action: {action}")
                
                time.sleep(poll_interval)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        print(f"\n✓ Loop complete. Logged {iteration} iterations to {self.log_file}")


def main():
    parser = argparse.ArgumentParser(description="Phyphox Autonomous Modulation Loop")
    parser.add_argument("--phyphox-url", required=True, help="Phyphox API URL (e.g., http://192.168.1.5:8080)")
    parser.add_argument("--output-dir", default="./logs", help="Output directory for logs")
    parser.add_argument("--duration", type=int, default=3600, help="Duration in seconds (default: 3600 = 1 hour)")
    parser.add_argument("--poll-interval", type=float, default=0.1, help="Polling interval in seconds (default: 0.1)")
    
    args = parser.parse_args()
    
    loop = AutonomousModulationLoop(
        phyphox_url=args.phyphox_url,
        output_dir=Path(args.output_dir)
    )
    
    loop.run(duration_seconds=args.duration, poll_interval=args.poll_interval)


if __name__ == "__main__":
    main()
