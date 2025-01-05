import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Text-to-Speech with Google TTS
def text_to_speech_cz_local(text, filename="output.mp3"):
    tts = gTTS(text=text, lang="cs")  # "cs" = Czech
    os.makedirs("output", exist_ok=True)
    tts.save(filename)
    print(f"Audio saved as {filename}")

# Function to Send Text to OpenAI Chat API
def get_response_from_openai(prompt):
    try:
        print("Odesílám text OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",  # or 'gpt-3.5-turbo'
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Chyba při komunikaci s OpenAI API: {e}")
        return "Omlouvám se, ale došlo k chybě při komunikaci s OpenAI API."

# Speech-to-Text and Continuous Processing
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

                # Generate MP3 from the API response
                filename = "output/output.mp3"
                text_to_speech_cz_local(response, filename)

            except sr.UnknownValueError:
                print("Nerozuměl jsem.")
            except sr.RequestError as e:
                print(f"Chyba při požadavku; {e}")
            except Exception as ex:
                print(f"Nastala chyba: {ex}")

if __name__ == "__main__":
    listen_and_respond()
