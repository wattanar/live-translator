import numpy as np
import pytest
import sys
import os

# Add live_translator to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'live_translator')))

from audio_utils import AudioRecorder

def test_chunk_processing():
    # Initialize recorder with 1 second chunk for easy testing
    sample_rate = 16000
    chunk_duration = 1
    recorder = AudioRecorder(sample_rate=sample_rate, chunk_duration=chunk_duration)
    
    # Simulate adding audio data
    # 0.5 seconds of data
    half_second_data = np.zeros((int(sample_rate * 0.5), 1), dtype=np.float32)
    recorder.audio_queue.put(half_second_data)
    
    # Should be None as it's not enough data
    assert recorder.get_audio_chunk() is None
    
    # Add another 0.6 seconds of data (total 1.1s)
    more_data = np.zeros((int(sample_rate * 0.6), 1), dtype=np.float32)
    recorder.audio_queue.put(more_data)
    
    # Should return a chunk of 1.0s
    chunk = recorder.get_audio_chunk()
    assert chunk is not None
    assert len(chunk) == sample_rate * chunk_duration
    
    # The remaining 0.1s should stay in the buffer
    assert len(recorder.buffer) == int(sample_rate * 0.1)
    
    # Should be None now
    assert recorder.get_audio_chunk() is None
