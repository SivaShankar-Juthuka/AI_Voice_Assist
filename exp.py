import os
import speech_recognition as sr # type: ignore
from openai import OpenAI # type: ignore
from elevenlabs import play # type: ignore
from dotenv import load_dotenv # type: ignore 
from google import genai # type: ignore
from google.genai.types import Content, Part # type: ignore
from deep_translator import GoogleTranslator # type: ignore
from elevenlabs.client import ElevenLabs # type: ignore
from Errors import exceptions # type: ignore
from flask import Flask, render_template, request, jsonify, send_from_directory # type: ignore

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="webpage/static", template_folder="webpage")

class VoiceAssistant:
    def __init__(self, target_language="en"):
        """Initialize API clients and settings."""
        self.target_language = target_language
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.elevenlabs_model = os.getenv("ELEVENLABS_MODEL")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.translator = GoogleTranslator()
        # Store conversation history
        self.conversation_history = []


    def record_audio(self, filename="webpage/static/recorded_audio.wav", silence_timeout=3):
        """Record audio from the microphone."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=silence_timeout)
            except sr.WaitTimeoutError:
                return None

        with open(filename, "wb") as file:
            file.write(audio.get_wav_data())
        return filename

    def speech_to_text(self, audio):
        """Convert speech to text using Whisper."""
        try:
            with open(audio, "rb") as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            return transcription.text
        except Exception as e:
            raise exceptions.SpeechToTextError("Speech-to-text conversion failed") from e

    def get_ai_response(self, text):
        """Generate AI response from Gemini model and store history."""
        self.conversation_history.append({"role": "user", "content": text})

        try:
            contents = [Content(role=msg["role"], parts=[Part(text=msg["content"])]) for msg in self.conversation_history]
            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=contents
            )

            ai_response = response.text
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            return ai_response
        except Exception as e:
            raise exceptions.GeminiError("Gemini model failed") from e

    def translate_text(self, text, src_lang, dest_lang):
        return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)

    def text_to_speech(self, text):
        """Convert text to speech and return the audio URL."""
        if not text.strip():
            raise ValueError("Input text cannot be empty")
        try:
            audio = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=self.elevenlabs_voice_id,
                model_id=self.elevenlabs_model
            )

            audio_path = "webpage/static/output.mp3"
            with open(audio_path, "wb") as audio_file:
                audio_file.write(audio)

            return "/static/output.mp3"
        except Exception as e:
            raise exceptions.TextToSpeechError("Text-to-speech conversion failed") from e
@app.route("/")
def home():
    return render_template("web_page.html")

@app.route("/assistant")
def assistant():
    return render_template("assistant.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/record", methods=["POST"])
def record():
    assistant = VoiceAssistant()
    audio_file = assistant.record_audio()
    
    if not audio_file:
        return jsonify({"error": "No speech detected"}), 400
    
    text = assistant.speech_to_text(audio_file)
    
    return jsonify({"text": text})

@app.route("/respond", methods=["POST"])
def respond():
    data = request.get_json()
    user_text = data.get("text", "").strip()
    language = data.get("language", "en")

    assistant = VoiceAssistant(language)
    response_text = assistant.get_ai_response(user_text)

    if language != "en":
        response_text = assistant.translate_text(response_text, src_lang="en", dest_lang=language)

    return jsonify({
        "response": response_text,
        "history": assistant.conversation_history  # Return full conversation
    })


@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "").strip()

    assistant = VoiceAssistant()
    audio_path = assistant.text_to_speech(text)

    return jsonify({"status": "Speech generated", "audio_url": audio_path})

if __name__ == "__main__":
    app.run(debug=True)