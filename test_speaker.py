#!/usr/bin/env python3
"""Simple test script to verify speaker playback works on this RPi 5."""

import tempfile
import subprocess
import os
import sys
from gtts import gTTS


def test_playback():
    print("Generating test TTS audio...")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        filename = f.name

    tts = gTTS(text="Test reproduktoru. Pokud mě slyšíš, vše funguje.", lang="cs")
    tts.save(filename)

    print(f"Playing audio from {filename} ...")
    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filename],
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("Playback timed out.")
    except KeyboardInterrupt:
        print("Interrupted.")

    os.remove(filename)
    print("Done.")


if __name__ == "__main__":
    test_playback()
