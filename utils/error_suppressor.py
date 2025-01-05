import os
import logging

# Configure logging
logging.getLogger('alsa').setLevel(logging.ERROR)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

class SuppressAlsaOutput:
    """Context manager to suppress ALSA output messages."""
    def __enter__(self):
        self.stderr = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)

    def __exit__(self, *args):
        os.dup2(self.stderr, 2)
        os.close(self.stderr)
        os.close(self.devnull)