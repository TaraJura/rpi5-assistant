import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import os
from dotenv import load_dotenv
import tempfile
from pydub import AudioSegment
from pydub.playback import play
import warnings
from utils.error_suppressor import SuppressAlsaOutput  # Import the class

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def play_text_cz(text):
    """Generate Czech TTS using gTTS and play via pydub (44.1 kHz)."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
        filename = tmpfile.name
    tts = gTTS(text=text, lang="cs")
    tts.save(filename)

    with SuppressAlsaOutput():
        audio = AudioSegment.from_file(filename, format="mp3").set_frame_rate(44100)
        play(audio)

    os.remove(filename)

def get_response_from_openai(prompt):
    try:
        print("Odesílám text OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Chyba při komunikaci s OpenAI API: {e}")
        return "Omlouvám se, ale došlo k chybě při komunikaci s OpenAI API."

def listen_and_respond():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 4000
    recognizer.pause_threshold = 0.8

    print("Kalibrace mikrofonu...")
    play_text_cz("Kalibrace mikrofonu")
    with SuppressAlsaOutput(), sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Kalibrace dokončena...")
        play_text_cz("Kalibrace dokončena")
        play_text_cz("Jsem Ninuška, tvůj asistent. Jak ti mohu pomoci?")
    while True:
        try:
            print("Poslouchám...")
            play_text_cz("Poslouchám.")

            with SuppressAlsaOutput(), sr.Microphone() as source:
                audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio, language='cs-CZ')
            print("Řekl jsi:", text)

            # Get AI response
            response = get_response_from_openai(text)
            print("Odpověď OpenAI:", response)

            # Speak AI response
            play_text_cz(response)

        except sr.UnknownValueError:
            print("Nerozuměl jsem.")
            play_text_cz("Nerozuměl jsem.")
        except sr.RequestError as e:
            msg = f"Chyba při požadavku; {e}"
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
