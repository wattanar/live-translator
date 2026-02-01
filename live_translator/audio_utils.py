import numpy as np
import sounddevice as sd
import queue
import sys

class AudioRecorder:
    def __init__(self, sample_rate=16000, chunk_duration=10, device_index=None):
        """
        sample_rate: 16000Hz is what Whisper expects.
        chunk_duration: Duration of each audio chunk to process in seconds.
        device_index: Optional index of the input device.
        """
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration)
        self.audio_queue = queue.Queue()
        self.buffer = np.zeros(0, dtype=np.float32)
        self.device_index = device_index

    def _callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        # Add the audio to our queue
        self.audio_queue.put(indata.copy())

    def start_recording(self):
        """Starts the audio stream."""
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                callback=self._callback,
                dtype=np.float32,
                device=self.device_index
            )
            self.stream.start()
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            if self.device_index is not None:
                print(f"Failed to open device index {self.device_index}.")
            print("Make sure your terminal has Microphone permissions.")
            sys.exit(1)

    def stop_recording(self):
        """Stops the audio stream."""
        self.stream.stop()
        self.stream.close()

    def get_audio_chunk(self):
        """
        Accumulates data from the queue and returns a chunk when it reaches 
        the desired duration. Returns None if not enough data.
        """
        while not self.audio_queue.empty():
            data = self.audio_queue.get()
            self.buffer = np.append(self.buffer, data.flatten())
        
        if len(self.buffer) >= self.chunk_size:
            chunk = self.buffer[:self.chunk_size]
            # Keep the overlap or just clear? 
            # For translation, we want some overlap or just clear. 
            # Let's clear for now but keep a small tail to avoid cutting words.
            self.buffer = self.buffer[self.chunk_size:]
            return chunk
        
        return None
