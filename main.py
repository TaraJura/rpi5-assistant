import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import os
from dotenv import load_dotenv
import tempfile
from pydub import AudioSegment
from pydub.playback import play
import warnings
from utils.error_suppressor import SuppressAlsaOutput
import cv2
import base64
import time

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
        raise IOError("No active camera found.")
    
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise IOError(f"Cannot open camera {cam_index}")
    
    time.sleep(2)  # let camera warm up
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise IOError("Failed to capture image")
        
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def analyze_image(base64_image, client):
    system_prompt = "1. Jsi AI asistent se jménem Ninuška. 2. Všechen input i output bude v Českém jazyce. 3. Co je na tomto obrázku? 4. Všechny tvoje odpovědi musí být krátké, maximálně jedna věta."
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image: {e}"

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
    sestem_prompt = "1.Jsi AI asistent se jménem Ninuška. 2. Všechen input i output bude v Českém jazyce. 3. Všechny tvoje odpovědi musí být krátké, maximálně jedna věta."
    try:
        print("Odesílám text OpenAI API...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": sestem_prompt},
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
    recognizer.energy_threshold = 5000
    recognizer.pause_threshold = 1

    print("Kalibrace mikrofonu...")
    play_text_cz("Kalibrace mikrofonu")
    with SuppressAlsaOutput(), sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=3)
        print("Kalibrace dokončena...")
        play_text_cz("Kalibrace dokončena.")
        play_text_cz("Jsem Ninuška, Jak ti mohu pomoci? Řekni 'podívej se' pro analýzu obrazu z kamery.")

    while True:
        try:
            print("Poslouchám...")
            play_text_cz("Poslouchám.")

            with SuppressAlsaOutput(), sr.Microphone() as source:
                audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio, language='cs-CZ')
            print("Řekl jsi:", text)

            # Check for vision command
            if "podívej" in text.lower() or "koukni" in text.lower():
                print("Zachycuji obraz z kamery...")
                play_text_cz("Zachycuji obraz z kamery.")
                base64_image = capture_webcam_image()
                print("Analyzuji obraz...")
                play_text_cz("Analyzuji obraz.")
                response = analyze_image(base64_image, client)
            else:
                # Get regular AI response
                response = get_response_from_openai(text)
            
            print("Odpověď OpenAI:", response)
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
