# Agent Guidelines: Live Audio Translator

This document provides essential information for AI agents working on this repository.

## Project Overview
A real-time, cross-platform audio translation CLI for macOS (optimized for M1) and Windows. It utilizes `faster-whisper` for local inference and `deep-translator` as a fallback for specific languages like Thai. The goal is to provide a low-latency, "native-feel" translation experience directly in the terminal using a Rich-based TUI.

## Build and Environment

### Python Environment
- **Version**: Python 3.10+ (standardized on 3.10).
- **Virtual Environment**: 
  - macOS: `live_translator/venv/`
  - Windows: `live_translator/venv/`
  - Always use the interpreter from these locations for script execution.

### Dependencies
- **Runtime**: `faster-whisper`, `sounddevice`, `numpy`, `rich`, `deep-translator`, `sentencepiece`.
- **System**: `ffmpeg` (required for audio decoding).
- **macOS**: `BlackHole` (optional, for system audio loopback).
- **Windows**: `Stereo Mix` or `VoiceMeeter` (optional, for system audio loopback).
- **Development**: `pytest`, `ruff`.

### Essential Commands
- **Install Runtime Deps**: 
  - macOS: `./live_translator/setup.sh`
  - Windows: `.\live_translator\setup.bat`
- **Install Dev Tools**: `pip install pytest ruff` (inside venv).
- **Run Application**: 
  - macOS: `./live_translator/run.sh`
  - Windows: `live_translator\run.bat`
- **List Audio Devices**: `./live_translator/run.sh --list-devices`
- **Linting**: `./live_translator/venv/bin/ruff check live_translator/`
- **Format Code**: `./live_translator/venv/bin/ruff format live_translator/`
- **Testing**: `./live_translator/venv/bin/pytest`
- **Run Single Test**: `./live_translator/venv/bin/pytest tests/test_audio.py::test_chunk_processing`
- **Testing with Coverage**: `pytest --cov=live_translator tests/`
- **Fast Linting**: `ruff check .`

## Code Style Guidelines

### 1. General Principles
- **Performance First**: Real-time audio processing is time-sensitive. Avoid blocking the main thread or the audio callback.
- **Local Inference**: Prioritize on-device AI. Only use external APIs (via `deep-translator`) when local models are insufficient (e.g., Thai translation quality or model size constraints).
- **M1 Optimization**: Use `compute_type="int8"` for Whisper on Apple Silicon to balance speed and accuracy without requiring a discrete GPU.

### 2. Formatting and Naming
- **Standards**: Adhere to PEP 8. Use `ruff` for linting and formatting.
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
- Buffers data in `self.buffer` (numpy array) to provide consistent chunks (e.g., 7-second windows) to the engine.

### `translator_engine.py` (AI Logic)
- Encapsulates `WhisperModel` from `faster-whisper`.
- Logic for `task="translate"` (to English) vs `task="transcribe"` (local language).
- Handles the "Thai Fallback" logic: if target is `th`, it transcribes locally then uses `GoogleTranslator` from `deep-translator`.
- Maintains a context buffer (`previous_text`) to improve translation consistency across chunks.

### `main.py` (CLI & Orchestration)
- Handles CLI arguments using `argparse`.
- Displays a configuration summary (table) on startup to confirm active settings.
- Orchestrates the TUI (Terminal User Interface) using `rich.live` and `rich.layout`.
- Contains the main processing loop: `get_audio_chunk()` -> `translate_audio()` -> `live.update()`.

## Concurrency and Threading
- **Audio Thread**: The `sounddevice` callback runs in a dedicated high-priority thread managed by PortAudio. Keep this callback minimal (just copying data to a queue).
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
- Use `refresh_per_second=2` to keep the UI responsive without over-consuming CPU.
- When adding new panels, ensure they handle text wrapping correctly to avoid breaking the layout on small terminals.
- Prefer `Panel` with `expand=True` for history displays to ensure they fill the available space.
- The "Current Translation" panel uses centered, bold text to maximize readability (simulating a larger font).

## Testing Guidelines
- Create tests in the `tests/` directory at the project root.
- Use `unittest.mock` to simulate:
  - Audio input queues with pre-recorded `numpy` arrays.
  - Model transcription results to verify TUI state updates.
- Focus tests on `AudioRecorder.get_audio_chunk` logic and `TranslatorEngine.translate_audio` state transitions.

## Model Management and Quantization
- **Quantization**: 
  - **CPU**: Uses `int8` by default. This is highly optimized for Apple Silicon (M1/M2) and modern x86 CPUs.
  - **GPU**: Uses `float16` by default when `--engine cuda` is specified. This is the preferred mode for NVIDIA GPUs to maximize throughput and minimize latency.
- **VAD (Voice Activity Detection)**: Uses the `Silero VAD` model integrated into `faster-whisper`. Configured via `vad_parameters` in `TranslatorEngine.translate_audio`.
- **Initial Prompts**: The last 200 characters of `previous_text` are passed as an `initial_prompt` to Whisper to maintain context.

## Environment Variables
- `OMP_NUM_THREADS`: Set to `4` (default in `run.sh`/`run.bat`) to prevent Whisper from consuming all CPU cores, which causes TUI lag.
- `PYTHONPATH`: Ensure the root directory is in the path.

## Cursor and Copilot Rules
*No project-specific .cursorrules or .github/copilot-instructions.md were found. Follow the guidelines in this document for all AI-assisted development.*

## Common Pitfalls
- **Microphone Permissions**: On macOS, terminals need permission in System Settings > Privacy & Security > Microphone.
- **PortAudio Errors**: Ensure no other application is locking the audio device.
- **Memory Usage**: Whisper `medium` or `large` models can consume 2GB+ of RAM.
- **VAD Hangs**: In silent environments, VAD might return empty segments; handle these to avoid UI flickering.
- **Encoding**: Ensure UTF-8 for all terminal output to support international characters.
