import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import os
from dotenv import load_dotenv
import tempfile

# pydub imports
from pydub import AudioSegment
from pydub.playback import play

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def play_text_cz(text):
    """Generate Czech TTS using gTTS and play via pydub."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmpfile:
        filename = tmpfile.name
    tts = gTTS(text=text, lang="cs")
    tts.save(filename)

    # Load and play via pydub
    audio = AudioSegment.from_file(filename, format="mp3")
    audio = audio.set_frame_rate(44100)
    play(audio)

    # Clean up
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
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Kalibrace dokončena. Poslouchám...")

        while True:
            try:
                print("Poslouchám...")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio, language='cs-CZ')
                print("Řekl jsi:", text)

                # Send recognized text to OpenAI
                response = get_response_from_openai(text)
                print("Odpověď OpenAI:", response)

                # Play TTS response
                play_text_cz(response)

            except sr.UnknownValueError:
                print("Nerozuměl jsem.")
            except sr.RequestError as e:
                print(f"Chyba při požadavku; {e}")
            except Exception as ex:
                print(f"Nastala chyba: {ex}")

if __name__ == "__main__":
    listen_and_respond()
