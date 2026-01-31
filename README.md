# Live Audio Translator

A native-feel CLI application for macOS (optimized for M1) that performs real-time audio translation using local AI models.

## Features

- **Local Inference**: Uses `faster-whisper` for high-performance, on-device audio processing.
- **System Audio Capture**: Supports capturing audio directly from system output (via BlackHole) or microphone.
- **Thai Language Support**: Can translate any supported language into English or Thai.
- **Modern CLI UI**: Features a live-updating dashboard with translation history.
- **M1 Optimized**: Configured for Apple Silicon with hardware acceleration.

## Prerequisites

1.  **Python 3.10**: Recommended for compatibility with AI libraries.
2.  **FFmpeg**: Required for audio processing.
    ```bash
    brew install ffmpeg
    ```
3.  **BlackHole (Optional)**: Required for capturing system output (e.g., from browser or video player).
    ```bash
    brew install blackhole-16ch
    ```

## Installation

1.  Clone the repository and navigate to the directory.
2.  The setup script will handle the virtual environment and dependencies.

## Usage

Run the application using the provided script:

```bash
cd live_translator
./run.sh [options]
```

### Common Commands

**1. Default (Listen to System Audio & Translate to English)**
```bash
./run.sh
```

**2. Listen to Japanese System Audio & Translate to Thai**
```bash
./run.sh --lang ja --target th
```

**3. Higher Accuracy (using 'medium' model)**
```bash
./run.sh --model medium --chunk 10
```

**4. Translate Microphone input instead of System Audio**
First, find your microphone index:
```bash
./run.sh --list-devices
```
Then run with the index (e.g., index 0):
```bash
./run.sh --device 0
```

### Options

- `--target th`: Translate into Thai (default is English).
- `--lang <code>`: Specify source language (e.g., `ja`, `zh`, `ko`) to skip auto-detection.
- `--model <size>`: Whisper model size. Options: `tiny`, `base`, `small` (default), `medium`, `large-v3`.
- `--chunk <seconds>`: Duration of audio to process at once. Default is `7`.
- `--list-devices`: Show available audio input devices.
- `--device <index>`: Manually select an audio input device index.

## Improving Accuracy

If you find the translation is not accurate enough, try the following:

1.  **Use a Larger Model**: The `small` or `medium` models provide significantly better accuracy than `base`.
    ```bash
    ./run.sh --model small
    ```
2.  **Increase Chunk Duration**: Longer chunks (e.g., 7-10 seconds) allow the model to hear full sentences before translating.
    ```bash
    ./run.sh --model small --chunk 8
    ```
3.  **Specify Source Language**: Skipping the auto-detection phase by providing the language code reduces errors.
    ```bash
    ./run.sh --lang ja --target th
    ```
4.  **Hardware Note**: Running larger models (`medium`, `large-v3`) will consume more RAM and CPU/GPU resources. On an M1 Mac, `small` is usually the "sweet spot" for real-time performance and high accuracy.

### Setting up System Audio Capture (BlackHole)

To translate audio coming from your computer (YouTube, Zoom, etc.):
1.  Open **Audio MIDI Setup**.
2.  Create a **Multi-Output Device**.
3.  Select both your **Speakers** and **BlackHole 16ch**.
4.  Set your system sound output to this new Multi-Output Device.
5.  Run the app; it will automatically detect and use BlackHole.

## License

MIT
