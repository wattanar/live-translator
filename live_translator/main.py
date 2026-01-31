import time
import signal
import sys
import argparse
import platform
import numpy as np
import sounddevice as sd
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table

from audio_utils import AudioRecorder
from translator_engine import TranslatorEngine

console = Console()

def list_audio_devices():
    console.print("\n[bold cyan]Available Audio Input Devices:[/bold cyan]")
    devices = sd.query_devices()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Index")
    table.add_column("Name")
    table.add_column("Channels (In/Out)")
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            table.add_row(str(i), dev['name'], f"{dev['max_input_channels']}/{dev['max_output_channels']}")
    
    console.print(table)
    if platform.system() == "Darwin":
        console.print("\n[yellow]To use system output, select a loopback device like 'BlackHole'.[/yellow]")
    elif platform.system() == "Windows":
        console.print("\n[yellow]To use system output, enable 'Stereo Mix' in Sound Settings or use 'VB-Audio VoiceMeeter'.[/yellow]")
    else:
        console.print("\n[yellow]To use system output, ensure you have a loopback device configured.[/yellow]")

class LiveTranslatorApp:
    def __init__(self, device_index=None, source_lang=None, target_lang="en", model_size="small", chunk_duration=7):
        self.recorder = AudioRecorder(chunk_duration=chunk_duration, device_index=device_index)
        self.engine = TranslatorEngine(model_size=model_size)
        self.engine.set_target_lang(target_lang)
        self.history = []
        self.max_history = 10
        self.running = True
        self.source_lang = source_lang
        self.target_lang = target_lang

    def generate_layout(self, current_text, language):
        layout = Layout()
        layout.split(
            Layout(name="history", ratio=3),
            Layout(name="current", ratio=1)
        )
        
        # History Table
        table = Table(show_header=False, box=None, expand=True)
        for h in self.history[-self.max_history:]:
            table.add_row(f"[white]{h}[/white]")
            
        layout["history"].update(
            Panel(table, title="Translation History", border_style="blue")
        )
        
        # Current status
        if self.source_lang:
            src_str = self.source_lang.upper()
        else:
            src_str = "Auto" if not language else language.upper()
            
        target_str = self.target_lang.upper()
            
        layout["current"].update(
            Panel(
                f"[bold green]{current_text or 'Listening...'}[/bold green]", 
                title=f"Live Translation ({src_str} → {target_str})", 
                border_style="green"
            )
        )
        return layout

    def signal_handler(self, sig, frame):
        self.running = False

    def run(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        
        console.print("[bold cyan]Starting Live Audio Translator...[/bold cyan]")
        console.print("Press Ctrl+C to stop.")
        
        self.recorder.start_recording()
        
        current_text = ""
        last_lang = ""
        
        with Live(self.generate_layout("", ""), refresh_per_second=4, screen=True) as live:
            try:
                while self.running:
                    chunk = self.recorder.get_audio_chunk()
                    if chunk is not None:
                        # Perform translation
                        translated_text, lang = self.engine.translate_audio(
                            chunk, 
                            source_lang=self.source_lang
                        )
                        
                        if translated_text.strip():
                            # If it's a new thought or significant enough
                            if len(current_text) > 0 and translated_text != current_text:
                                self.history.append(translated_text)
                            current_text = translated_text
                            last_lang = lang
                        
                        live.update(self.generate_layout(current_text, last_lang))
                    
                    time.sleep(0.1)
            except Exception as e:
                # We can't print easily inside Live, but it will be caught
                raise e
            finally:
                self.recorder.stop_recording()

def find_loopback_device_index():
    devices = sd.query_devices()
    # Common loopback device keywords
    keywords = ["BlackHole", "Stereo Mix", "VoiceMeeter", "Loopback", "Virtual Audio"]
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            for kw in keywords:
                if kw.lower() in dev['name'].lower():
                    return i
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Audio Translator")
    parser.add_argument("--list-devices", action="store_true", help="List available audio devices and exit")
    parser.add_argument("--device", type=int, help="Audio device index to use")
    parser.add_argument("--lang", type=str, help="Source language code (e.g., 'ja', 'zh', 'fr'). Default is auto-detect.")
    parser.add_argument("--target", type=str, default="en", help="Target language code ('en' or 'th'). Default is 'en'.")
    parser.add_argument("--model", type=str, default="small", choices=["tiny", "base", "small", "medium", "large-v3"], 
                        help="Whisper model size. 'small' or 'medium' are recommended for better accuracy.")
    parser.add_argument("--chunk", type=int, default=7, help="Audio chunk duration in seconds. Longer chunks provide better context.")
    args = parser.parse_args()

    if args.list_devices:
        list_audio_devices()
        sys.exit(0)

    device_idx = args.device
    if device_idx is None:
        device_idx = find_loopback_device_index()
        if device_idx is not None:
            loopback_name = sd.query_devices(device_idx)['name']
            console.print(f"[green]Automatically selected {loopback_name} (index {device_idx}) for system audio.[/green]")
        else:
            console.print("[yellow]No loopback device found. Using default microphone.[/yellow]")

    try:
        app = LiveTranslatorApp(
            device_index=device_idx, 
            source_lang=args.lang, 
            target_lang=args.target,
            model_size=args.model,
            chunk_duration=args.chunk
        )
        app.run()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Stopped by user.[/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
