# Live Audio Translator

A native-feel CLI application for macOS (optimized for M1) and Windows that performs real-time audio translation using local AI models.

## Features

- **Local Inference**: Uses `faster-whisper` for high-performance, on-device audio processing.
- **System Audio Capture**: Supports capturing audio directly from system output (via BlackHole on macOS or Stereo Mix/VoiceMeeter on Windows) or microphone.
- **Thai Language Support**: Can translate any supported language into English or Thai.
- **Modern CLI UI**: Features a live-updating dashboard with translation history and a configuration summary on startup.
- **Cross-Platform**: Works on macOS (optimized for Apple Silicon) and Windows.

## Prerequisites

### macOS
1.  **Python 3.10**: Recommended for compatibility with AI libraries.
2.  **FFmpeg**: Required for audio processing.
    ```bash
    brew install ffmpeg
    ```
3.  **BlackHole (Optional)**: Required for capturing system output.
    ```bash
    brew install blackhole-16ch
    ```

### Windows
1.  **Python 3.10**: Install from [python.org](https://www.python.org/downloads/).
2.  **FFmpeg**: Install via `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.
3.  **Loopback Device (Optional)**: Enable "Stereo Mix" in Sound Settings or install [VB-Audio VoiceMeeter](https://vb-audio.com/Voicemeeter/).

## Installation

1.  Clone the repository and navigate to the directory.
2.  **macOS**:
    ```bash
    cd live_translator
    chmod +x setup.sh
    ./setup.sh
    ```
3.  **Windows**:
    ```cmd
    cd live_translator
    setup.bat
    ```

## Usage

### macOS
Run the application using the provided script:
```bash
./run.sh [options]
```

### Windows
Run the application using the provided batch file:
```cmd
run.bat [options]
```

### Common Commands

**1. Default (Listen to System Audio & Translate to English)**
```bash
./run.sh  # macOS
run.bat   # Windows
```

**2. Listen to Japanese System Audio & Translate to Thai**
```bash
./run.sh --lang ja --target th
```

**3. Higher Accuracy & Performance (using 'medium' model on GPU)**
```bash
./run.sh --model medium --engine cuda --chunk 10
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
- `--model <size>`: Whisper model size. Options: `tiny`, `base`, `small`, `medium` (default), `large-v3`.
- `--engine <device>`: AI inference device. `cpu` (default) or `cuda` (for NVIDIA GPUs).
- `--chunk <seconds>`: Duration of audio to process at once. Default is `7`.
- `--list-devices`: Show available audio input devices.
- `--device <index>`: Manually select an audio input device index.

## Improving Accuracy

If you find the translation is not accurate enough, try the following:

1.  **Use a Larger Model**: The `medium` or `large-v3` models provide significantly better accuracy.
    ```bash
    ./run.sh --model medium
    ```
2.  **Increase Chunk Duration**: Longer chunks (e.g., 7-10 seconds) allow the model to hear full sentences before translating.
    ```bash
    ./run.sh --model medium --chunk 8
    ```
3.  **Specify Source Language**: Skipping the auto-detection phase by providing the language code reduces errors.
    ```bash
    ./run.sh --lang ja --target th
    ```
4.  **Hardware Note**: Running larger models (`medium`, `large-v3`) will consume more RAM and CPU/GPU resources. On an M1 Mac, `medium` (default) is the recommended "sweet spot" for real-time performance and high accuracy.

### Setting up System Audio Capture

#### macOS (BlackHole)
1.  Open **Audio MIDI Setup**.
2.  Create a **Multi-Output Device**.
3.  Select both your **Speakers** and **BlackHole 16ch**.
4.  Set your system sound output to this new Multi-Output Device.
5.  Run the app; it will automatically detect and use BlackHole.

#### Windows (Stereo Mix)
1.  Right-click the speaker icon in the taskbar and select **Sound Settings**.
2.  Go to **Input** and click **Manage sound devices**.
3.  If **Stereo Mix** is disabled, enable it.
4.  Run the app; it will automatically detect and use Stereo Mix if available.

## Development

### Running Tests
Tests are located in the `tests/` directory at the project root.
```bash
./live_translator/venv/bin/pip install pytest
./live_translator/venv/bin/pytest
```

### Linting
```bash
./live_translator/venv/bin/pip install ruff
./live_translator/venv/bin/ruff check .
```

## License

MIT
