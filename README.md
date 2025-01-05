# RPi5 Assistant

A simple voice-controlled assistant that combines speech recognition, OpenAI ChatGPT, and text-to-speech capabilities, designed for Raspberry Pi 5.

## Features

- Speech recognition for hands-free interaction
- Integration with OpenAI ChatGPT API
- Text-to-speech output using gTTS
- Optimized for Raspberry Pi 5

## Prerequisites

- Python 3.x
- Working microphone
- Internet connection
- OpenAI API key
- Raspberry Pi 5 (recommended) or other compatible system

## Setup

1. **Clone the repository**
   ```bash
   git clone git@github.com:TaraJura/rpi5-assistant.git
   cd rpi5-assistant
   ```

2. **Create and activate virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   # Or on Windows:
   # .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the assistant**
   - Create a copy of `config.example.py` as `config.py`
   - Add your OpenAI API key to `config.py`
   ```python
   OPENAI_API_KEY = 'your-api-key-here'
   ```

5. **Run the assistant**
   ```bash
   python3 main.py
   ```

## Usage

1. The assistant will start listening for voice input when launched
2. Speak clearly into your microphone
3. Wait for the ChatGPT response and audio playback
4. The conversation will continue until you stop the program

## Configuration Options

- Adjust microphone sensitivity in `config.py`
- Modify TTS voice settings
- Configure ChatGPT model parameters
- Customize wake word/phrase (if implemented)

## Troubleshooting

- Ensure your microphone is properly connected and recognized
- Check your internet connection for TTS and ChatGPT functionality
- Verify your OpenAI API key is valid and has sufficient credits
- Run `python3 test_audio.py` to verify audio input/output setup

## Project Structure

```
rpi5-assistant/
├── main.py              # Main application file
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── test_audio.py       # Audio testing utility
└── output/             # TTS output directory
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## .gitignore

```
# Virtual environment
venv/

# Python cache
__pycache__/
*.pyc

# Output folder
output/

# Configuration
config.py

# OS-specific
.DS_Store
Thumbs.db
```

## Acknowledgments

- OpenAI for ChatGPT API
- Google Text-to-Speech (gTTS)
- Speech Recognition library contributors
- Raspberry Pi Foundation