# Agent Guidelines: Live Audio Translator

This document provides essential information for AI agents working on this repository.

## Project Overview
A real-time, cross-platform audio translation CLI for macOS (optimized for M1) and Windows. It utilizes `faster-whisper` for local inference and `deep-translator` as a fallback for specific languages like Thai. The goal is to provide a low-latency, "native-feel" translation experience directly in the terminal.

## Build and Environment

### Python Environment
- **Version**: Python 3.10+ (standardized on 3.10).
- **Virtual Environment**: 
  - macOS: `live_translator/venv/`
  - Windows: `live_translator/venv/`
  - Always use the interpreter from these locations for script execution.

### Dependencies
- Core: `faster-whisper`, `sounddevice`, `numpy`, `rich`, `deep-translator`, `sentencepiece`.
- System: `ffmpeg` (required for audio decoding).
- macOS: `BlackHole` (optional, for system audio loopback).
- Windows: `Stereo Mix` or `VoiceMeeter` (optional, for system audio loopback).

### Entry Points
- **macOS**: `live_translator/run.sh`
- **Windows**: `live_translator/run.bat`
- **Direct**: `python live_translator/main.py` (after activating venv).

### Essential Commands
- **Install Dependencies**: 
  - macOS: `./live_translator/venv/bin/pip install -r live_translator/requirements.txt`
  - Windows: `.\live_translator\venv\Scripts\pip install -r live_translator\requirements.txt`
- **Run Application**: 
  - macOS: `./live_translator/run.sh`
  - Windows: `live_translator\run.bat`
- **List Audio Devices**: `./live_translator/run.sh --list-devices`
- **Linting**: `./live_translator/venv/bin/ruff check live_translator/`
- **Testing**: `./live_translator/venv/bin/pytest`
- **Run Single Test**: `./live_translator/venv/bin/pytest tests/test_audio.py::test_chunk_processing`

## Code Style Guidelines

### 1. General Principles
- **Performance First**: Real-time audio processing is time-sensitive. Avoid blocking the main thread or the audio callback.
- **Local Inference**: Prioritize on-device AI. Only use external APIs (via `deep-translator`) when local models are insufficient (e.g., Thai translation quality or model size constraints).
- **M1 Optimization**: Use `compute_type="int8"` for Whisper on Apple Silicon to balance speed and accuracy without requiring a discrete GPU.

### 2. Formatting and Naming
- **Standards**: Adhere to PEP 8.
- **Naming**: 
  - Functions/Variables: `snake_case`.
  - Classes: `PascalCase`.
  - Constants: `SCREAMING_SNAKE_CASE`.
- **Strings**: Use f-strings for all formatting. Prefer single quotes (`'`) unless double quotes are required for nesting.
- **Indentation**: 4 spaces.

### 3. Imports
Follow this order, separated by a single newline:
1. **Standard Library**: `os`, `sys`, `time`, `queue`, `signal`, `argparse`.
2. **Third-Party**: `numpy`, `sounddevice`, `faster_whisper`, `rich`.
3. **Local**: `from audio_utils import ...`.
Avoid wildcard imports (`from module import *`).

### 4. Typing
- **Type Hints**: Mandatory for all function signatures and class methods.
- **Syntax**: Use Python 3.10+ syntax (e.g., `str | None` instead of `Optional[str]`).
- **Example**:
  ```python
  def process_audio(self, data: np.ndarray, sample_rate: int = 16000) -> str:
      ...
  ```

### 5. Error Handling
- **IO Operations**: Wrap audio stream initialization and network calls in `try...except` blocks.
- **User Feedback**: Use `rich.console` to provide styled, readable error messages.
- **Non-Fatal Errors**: Log to `sys.stderr` or use `console.print(style="bold red")`.
- **Fatal Errors**: Use `sys.exit(1)` with a clear explanation of why the CLI is terminating.

## Architecture

### `audio_utils.py` (Audio Capture)
- Handles low-level interaction with `sounddevice`.
- Uses a non-blocking `InputStream` callback to push raw audio frames into a `queue.Queue`.
- Buffers data to provide consistent chunks (e.g., 7-second windows) to the engine.

### `translator_engine.py` (AI Logic)
- Encapsulates `WhisperModel`.
- Logic for `task="translate"` (to English) vs `task="transcribe"` (local language).
- Handles the "Thai Fallback" logic using `GoogleTranslator` from `deep-translator`.
- Maintains a small context buffer (`previous_text`) to improve translation consistency across chunks.

### `main.py` (CLI & Orchestration)
- Handles CLI arguments using `argparse`.
- Orchestrates the TUI (Terminal User Interface) using `rich.live` and `rich.layout`.
- Contains the main processing loop that bridges the recorder and the engine.

## Concurrency and Threading
- **Audio Thread**: The `sounddevice` callback runs in a dedicated high-priority thread. Keep this callback minimal (just copying data to a queue).
- **Main Thread**: Handles the CLI loop, model inference (which is CPU/GPU intensive), and TUI updates.
- **Synchronization**: Use `queue.Queue` for thread-safe communication between the audio callback and the main loop.

## Development Workflow

### Adding a New Source Language
1. Verify if `faster-whisper` supports the language code.
2. Update the `TranslatorEngine.translate_audio` method if special handling or a different fallback is needed.
3. Test with a 7-10 second audio clip to ensure the VAD (Voice Activity Detection) filter works correctly.

### Modifying the UI
- Use `rich.layout` to define sections.
- Ensure the `Live` context manager in `main.py` is properly handled during exceptions to prevent terminal corruption.
- Test UI responsiveness on different terminal sizes.

## Testing Guidelines
- Since real-time audio is hard to test deterministically, use `unittest.mock` to simulate:
  - Audio input queues with pre-recorded `numpy` arrays.
  - Model transcription results to verify TUI state updates.
- Focus tests on `AudioRecorder.get_audio_chunk` logic and `TranslatorEngine.translate_audio` state transitions.

## Model Management and Quantization
- **Quantization**: Always use `int8` for CPU-based inference to reduce memory footprint and latency. On machines with NVIDIA GPUs, `float16` with `device="cuda"` is preferred.
- **VAD (Voice Activity Detection)**: The project uses the `Silero VAD` model integrated into `faster-whisper`. Configuration is passed via `vad_parameters` in `TranslatorEngine.translate_audio`.
- **Initial Prompts**: To maintain context between audio chunks, the last 200 characters of the `previous_text` are passed as an `initial_prompt` to the Whisper model. This helps with proper noun consistency and sentence completion.

## Environment Variables
- `OMP_NUM_THREADS`: Set to `4` (default in `run.sh`/`run.bat`) to prevent Whisper from consuming all CPU cores, which can cause TUI stuttering.
- `PYTHONPATH`: Ensure the root directory is in the path if running scripts from subdirectories.

## Cursor and Copilot Rules
*No project-specific .cursorrules or .github/copilot-instructions.md were found. Follow the guidelines in this document for all AI-assisted development.*

## Common Pitfalls
- **Microphone Permissions**: On macOS, terminals often need explicit permission in System Settings > Privacy & Security > Microphone.
- **PortAudio Errors**: Ensure no other application is locking the audio device at the same sample rate. If you see "Device unavailable", check for competing recording software.
- **Memory Usage**: Whisper `medium` or `large` models can consume 2GB+ of RAM. Monitor memory during long sessions, especially on 8GB RAM machines.
- **VAD Hangs**: If `vad_filter=True` is used, very quiet environments might result in empty segments; handle these gracefully to avoid UI flickering.
- **Encoding Issues**: Always ensure text being printed to the terminal is UTF-8 encoded to support international characters.
