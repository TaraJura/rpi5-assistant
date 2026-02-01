# Ninuška v2 — Claude Code Voice Assistant

## What this is
A Czech-language voice assistant named **Ninuška** running on a Raspberry Pi 5.
It uses **Claude Code CLI** (`--dangerously-skip-permissions`) as the AI backend,
with full system access (files, commands, hardware).

## Hardware
- Raspberry Pi 5 (4 cores, 4 GB RAM)
- USB audio device (Realtek, card 2) — speaker + microphone
- USB/CSI webcam

## Architecture
```
Microphone → Google Speech Recognition (Czech) → claude CLI → TTS summary → Speaker (aplay)
                                                     ↑
                                            webcam image (optional, via --add-file)
```

## Files
| File | Purpose |
|------|---------|
| `main.py` | Main assistant loop: listen, call claude, speak response |
| `utils/error_suppressor.py` | ALSA stderr suppression context manager |
| `requirements.txt` | Python dependencies (no openai, no pyttsx3) |
| `~/run_robot.sh` | Launcher script — sets up venv, checks deps, runs main.py |
| `/etc/systemd/system/ai-assistant.service` | Systemd service for auto-start on boot |

## Development principles
- **Keep it simple**: Prefer simple, standard solutions over clever hacks. Follow established conventions (PEP 8, standard library patterns, well-known packages). Simple code is easier to debug, maintain, and scale.
- **Minimal changes**: Only modify what is necessary. Do not refactor, add abstractions, or "improve" unrelated code.
- **Standards-based**: Use widely adopted libraries and protocols. Avoid reinventing what already exists in the Python ecosystem.

## Critical rules
1. **Audio playback**: Uses `gTTS` → `ffplay -nodisp -autoexit -loglevel quiet` via `subprocess.run()`. Do NOT use `pydub.playback.play()` — it hangs and ignores Ctrl+C. Do NOT wrap playback in `SuppressAlsaOutput` — it breaks subprocess audio.
2. **Signal handling**: `os._exit(0)` on SIGINT/SIGTERM. Regular `sys.exit()` does not work because audio subprocesses trap signals.
3. **Claude CLI invocation**: `claude -p "<prompt>" --dangerously-skip-permissions --output-format json`. Claude is already authenticated on this system — no API keys needed.
4. **Camera**: Say "podívej" or "koukni" to trigger webcam capture. Image saved to `/tmp/ninuska_cam.jpg` and passed via `--add-file`.
5. **TTS summarization**: If Claude's response exceeds 200 chars, a second Claude call summarizes it to one Czech sentence before speaking.
6. **Microphone**: Uses `SpeechRecognition` with Google Speech API, Czech language (`cs-CZ`). Calibration runs once at startup. Wrap microphone operations in `SuppressAlsaOutput` to hide ALSA enumeration spam.
7. **SuppressAlsaOutput**: Only use around microphone operations. Never around playback — it redirects fd 2 which breaks subprocess audio.
8. **System dependencies**: `ffmpeg`, `aplay` (alsa-utils), `claude` CLI must be installed.
9. **USB audio volume**: The USB audio card has its own mixer (`amixer -c 2 set 'Headphone' 175`). PipeWire Master volume alone is not enough.
10. **ALWAYS TEST after changes**: After ANY code modification, you MUST verify the program still works end-to-end: microphone captures speech, Claude responds, and audio plays through the speaker. Never assume changes are safe — run the program and confirm.

## How to run
```bash
# Manual
cd ~/rpi5-assistant && source venv/bin/activate && python3 main.py

# Via launcher
~/run_robot.sh

# Via systemd
sudo systemctl restart ai-assistant
journalctl -u ai-assistant -f  # view logs
```

## How to stop
- Ctrl+C (signal handler kills immediately)
- `pkill -f "python3 main.py"`
- `sudo systemctl stop ai-assistant`
