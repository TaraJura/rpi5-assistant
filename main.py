#!/usr/bin/env python3
"""Ninuška v2 — Czech voice assistant powered by Claude Code on Raspberry Pi 5."""

import speech_recognition as sr
from gtts import gTTS
import os
import sys
import signal
import subprocess
import json
import tempfile
import warnings
from utils.error_suppressor import SuppressAlsaOutput
import cv2

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "Jsi hlasový AI asistent Ninuška na Raspberry Pi. "
    "Odpovídej VŽDY česky. "
    "KRITICKÉ: Odpovědi musí být co nejkratší — maximálně 1-2 věty. "
    "Žádné formátování, žádný markdown, žádné backticky. "
    "Pokud uživatel chce provést příkaz, proveď ho a vrať pouze výsledek."
)

# ---------------------------------------------------------------------------
# Signal handling
# ---------------------------------------------------------------------------
def _signal_handler(sig, frame):
    print("\nUkončuji Ninušku...")
    os._exit(0)

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


# ---------------------------------------------------------------------------
# Audio playback — identical to original working code
# ---------------------------------------------------------------------------
def play_text_cz(text):
    """Generate Czech TTS using gTTS and play via ffplay."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
        filename = tmpfile.name
    tts = gTTS(text=text, lang="cs")
    tts.save(filename)

    try:
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filename],
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("Playback timed out.")
    finally:
        os.remove(filename)


# ---------------------------------------------------------------------------
# Claude Code integration
# ---------------------------------------------------------------------------
def run_claude(prompt, image_path=None):
    """Send a prompt to claude CLI and return the response text."""
    full_cmd = [
        "claude", "-p", prompt,
        "--system-prompt", SYSTEM_PROMPT,
        "--dangerously-skip-permissions",
        "--output-format", "json",
    ]
    if image_path:
        full_cmd.extend(["--add-dir", os.path.dirname(image_path)])
        prompt = f"{prompt}\n\nAnalyzuj obrázek: {image_path}"

    print(f"Claude prompt: {prompt[:100]}")
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            print(f"Claude error: {result.stderr[:300]}")
            return f"Chyba při volání Claude: {result.stderr[:200]}"

        try:
            data = json.loads(result.stdout)
            response = data.get("result", result.stdout)
        except json.JSONDecodeError:
            response = result.stdout.strip()

        print(f"Claude response ({len(response)} chars): {response}")
        return response

    except subprocess.TimeoutExpired:
        return "Claude neodpověděl včas."
    except Exception as e:
        return f"Chyba: {e}"


def summarize_for_speech(text):
    """If text is too long for TTS, ask Claude to summarize in one Czech sentence."""
    if len(text) <= 200:
        return text
    print("Summarizing long response for TTS...")
    summary = run_claude(
        f"Shrň následující text do jedné krátké české věty:\n\n{text}"
    )
    return summary if len(summary) <= 300 else summary[:300]


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
def get_first_active_camera(max_devices=3):
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            cap.release()
            return i
    return None


def capture_webcam_image():
    cam_index = get_first_active_camera()
    if cam_index is None:
        raise IOError("Nebyla nalezena žádná kamera.")
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise IOError(f"Nelze otevřít kameru {cam_index}")
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise IOError("Nepodařilo se zachytit obrázek")
    path = "/tmp/ninuska_cam.jpg"
    cv2.imwrite(path, frame)
    return path


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def listen_and_respond():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 5000
    recognizer.pause_threshold = 1

    print("Kalibrace mikrofonu...")
    with SuppressAlsaOutput(), sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Kalibrace dokončena.")
    play_text_cz("Jsem Ninuška s mozkem Claude. Jak ti mohu pomoci?")
    play_text_cz("Řekni 'podívej se' pro analýzu obrazu z kamery.")

    while True:
        try:
            print("Poslouchám...")
            play_text_cz("Poslouchám.")

            with SuppressAlsaOutput(), sr.Microphone() as source:
                audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio, language="cs-CZ")
            print(f"Rozpoznáno: {text}")

            if "podívej" in text.lower() or "koukni" in text.lower():
                play_text_cz("Zachycuji obraz z kamery.")
                image_path = capture_webcam_image()
                play_text_cz("Analyzuji obraz.")
                response = run_claude(text, image_path=image_path)
            else:
                play_text_cz("Zpracovávám.")
                response = run_claude(text)

            spoken = summarize_for_speech(response)
            print(f"TTS: {spoken}")
            play_text_cz(spoken)

        except sr.UnknownValueError:
            print("Nerozuměl jsem.")
            play_text_cz("Nerozuměl jsem.")
        except sr.RequestError as e:
            msg = f"Chyba při rozpoznávání řeči: {e}"
            print(msg)
            play_text_cz(msg)
        except Exception as ex:
            msg = f"Nastala chyba: {ex}"
            print(msg)
            play_text_cz(msg)


if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        listen_and_respond()
