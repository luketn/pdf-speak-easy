#!/usr/bin/env python3
"""
Coordinator: PDF to Speech process runner
Runs model_to_text.py and tts_and_play.py in correct sequence.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

def wait_for_file(filepath, timeout=30, interval=0.5):
    """Wait up to timeout seconds for the file to appear."""
    start = time.time()
    while not Path(filepath).exists():
        if time.time() - start > timeout:
            print(f"Timeout waiting for {filepath}")
            sys.exit(1)
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Convert PDF to speech (Coordinator)")
    parser.add_argument("pdf_path", help="Path to PDF file")
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    txt_path = str(pdf_path) + ".txt"

    # Start the model output streaming process
    print("[pdf_to_speech] Extracting text from PDF...")
    model_proc = subprocess.Popen(
        [sys.executable, "model_to_text.py", str(pdf_path)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    # Start the TTS/playback process after file appears (or immediately for streaming)
    wait_for_file(txt_path, timeout=60)
    print("[pdf_to_speech] Starting speech synthesis and playback...")

    tts_proc = subprocess.Popen(
        [sys.executable, "tts_and_play.py", txt_path],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    # Forward output from both subprocesses
    while True:
        model_out = model_proc.stdout.readline() if not model_proc.poll() else ""
        tts_out = tts_proc.stdout.readline() if not tts_proc.poll() else ""

        if model_out:
            print("[model_to_text]", model_out, end="")
        if tts_out:
            print("[tts_and_play]", tts_out, end="")

        if model_proc.poll() is not None and tts_proc.poll() is not None:
            print("[pdf_to_speech] All done.")
            break

        time.sleep(0.1)

if __name__ == "__main__":
    main()