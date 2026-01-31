# Agent Guidelines: Live Audio Translator

This document provides essential information for agents working on this repository.

## Project Overview
A real-time audio translation CLI for macOS, optimized for M1, using `faster-whisper` and `deep-translator`.

## Build and Environment
- **Python Version**: 3.10 is the primary supported version.
- **Virtual Environment**: Located at `live_translator/venv/`. Always use the interpreter from this venv for any script execution or dependency management.
- **Dependencies**: Listed in `live_translator/requirements.txt`. Key libraries include `faster-whisper`, `sounddevice`, `numpy`, `rich`, and `deep-translator`.
- **Entry Point**: `live_translator/main.py`.
- **Execution**: Use `live_translator/run.sh` to run with the correct environment variables (`OMP_NUM_THREADS`) and venv activation.

### Essential Commands
- **Install Dependencies**: `./live_translator/venv/bin/pip install -r live_translator/requirements.txt`
- **Run Application**: `./live_translator/run.sh`
- **List Audio Devices**: `./live_translator/run.sh --list-devices`
- **Linting (Recommended)**: `./live_translator/venv/bin/pip install ruff && ./live_translator/venv/bin/ruff check live_translator/`
- **Testing (Recommended)**: `./live_translator/venv/bin/pip install pytest && ./live_translator/venv/bin/pytest`
- **Run Single Test**: `./live_translator/venv/bin/pytest tests/test_file.py::test_name`

## Code Style Guidelines

### 1. General Principles
- **Conciseness**: Keep functions small and focused on a single task.
- **Local-First**: Prioritize on-device AI processing. External APIs (like Google Translate via `deep-translator`) should only be used as fallbacks or for languages where local models are too large for real-time CLI usage (e.g., Thai).
- **M1 Optimization**: Always prefer `int8` quantization for `ctranslate2` models to ensure high performance on Apple Silicon without requiring a GPU.
- **Streaming Logic**: Real-time audio processing should use non-blocking callbacks and thread-safe queues.

### 2. Formatting and Naming
- **Naming**: Use `snake_case` for variables, functions, and file names. Use `PascalCase` for classes.
- **Indentation**: 4 spaces (standard PEP 8).
- **Strings**: Use f-strings for formatting. Prefer single quotes for strings unless double quotes are needed for nesting.

### 3. Imports
Order imports as follows:
1. Standard library imports (e.g., `import os`, `import sys`).
2. Third-party library imports (e.g., `import numpy as np`, `import sounddevice as sd`).
3. Local application imports (e.g., `from audio_utils import AudioRecorder`).
Avoid `from module import *`.

### 4. Typing
- Use Python 3.10+ type hints where possible to improve code clarity and catch bugs early.
- Example: `def translate_audio(self, audio_data: np.ndarray, source_lang: str | None = None) -> tuple[str, str]:`
- Use `| None` instead of `Optional` from the `typing` module.

### 5. Error Handling
- Use `try...except` blocks around external I/O (microphone, audio MIDI, networking).
- Provide user-friendly error messages via `rich.console`.
- For fatal CLI errors, use `sys.exit(1)`.
- Log non-fatal errors to `sys.stderr` or use `console.print(..., style="bold red")`.

### 6. Architecture
- **audio_utils.py**: Low-level audio capture logic. Uses `sounddevice.InputStream` with a callback to push data into a `queue.Queue`.
- **translator_engine.py**: Core AI logic. Encapsulates `WhisperModel` from `faster-whisper`. Handles logic for `task="translate"` (to English) vs `task="transcribe"` (for other targets).
- **main.py**: CLI interface using `argparse`. Orchestrates the live dashboard using `rich.live` and `rich.layout`. Manages the main processing loop which pulls from `AudioRecorder` and pushes to `TranslatorEngine`.

## Rules and Instructions
*Currently no Cursor or Copilot rules are defined in this repository.*

## Adding New Features
1. **Verify System Dependencies**: Check if new features require system-level packages (like FFmpeg or BlackHole).
2. **Modular Implementation**: Implement core logic in `audio_utils` or `translator_engine` before touching the UI.
3. **CLI Exposure**: Update `main.py` to expose the feature via new CLI arguments.
4. **Documentation**: Update `README.md` with usage examples for the new feature.
5. **Entry Point**: Ensure `run.sh` remains the primary entry point and correctly forwards arguments to `main.py` using `"$@"`.
