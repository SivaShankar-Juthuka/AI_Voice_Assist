import os
import speech_recognition as sr # type: ignore
from openai import OpenAI  # type: ignore
from elevenlabs import play  # type: ignore
from dotenv import load_dotenv  # type: ignore
from google import genai
from google.genai.types import Content, Part # type: ignore
from deep_translator import GoogleTranslator  # type: ignore
from elevenlabs.client import ElevenLabs  # type: ignore
from Errors import exceptions

# Load environment variables
load_dotenv()

class VoiceAssistant:
    def __init__(self, target_language):
        """Initialize API clients and settings."""
        self.target_language = target_language
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.elevenlabs_model = os.getenv("ELEVENLABS_MODEL")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.translator = GoogleTranslator()
        self.transcript_history = [ ]

    def record_audio(self, filename="recorded_audio.wav", silence_timeout=3):
        """Record audio from the microphone."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            print("Listening... Speak now!")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=silence_timeout)
            except sr.WaitTimeoutError:
                print("No speech detected. Try again.")
                return None

        with open(filename, "wb") as file:
            file.write(audio.get_wav_data())
        return filename

    def text_to_speech(self, text):
        """Convert text to speech using ElevenLabs."""
        if not text.strip():
            raise ValueError("Input text cannot be empty")
        try:
            audio = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=self.elevenlabs_voice_id,
                model_id=self.elevenlabs_model
            )
            play(audio)
        except Exception as e:
            raise exceptions.TextToSpeechError("Text-to-speech conversion failed") from e

    def speech_to_text(self, audio):
        """Convert speech to text using Whisper."""
        try:
            with open(audio, "rb") as audio_file:  # Open in binary mode
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            print(f"Transcription: {transcription.text} ")
            return transcription.text
        except Exception as e:
            raise exceptions.SpeechToTextError("Speech-to-text conversion failed") from e


    def get_ai_response(self, text):
        """Generate AI response from Gemini model."""
        self.transcript_history.append({"role": "user", "content": text})

        try:
            # Convert messages to Content format
            contents = [Content(role=msg["role"], parts=[Part(text=msg["content"])]) for msg in self.transcript_history]

            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=contents
            )

            ai_response = response.text
            self.transcript_history.append({"role": "model", "content": ai_response})  # Use 'model' instead of 'system'
            return ai_response
        except Exception as e:
            raise exceptions.GeminiError("Gemini model failed") from e


    def translate_text(self, text, src_lang, dest_lang):
        return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)


def main():
    # Language selection
    language_map = {"1": "en", "2": "hi"}
    lang_choice = input("Select your language:\n1. English (en)\n2. Hindi (hi)\nEnter the number corresponding to your choice: ")
    selected_language = language_map.get(lang_choice, "en")

    # Initialize Assistant with language preference
    assistant = VoiceAssistant(selected_language)

    # Welcome messages in respective languages
    welcome_messages = {
        "en": "Welcome! How can I assist you today?",
        "hi": "स्वागत है! मैं आज आपकी कैसे मदद कर सकता हूँ?"
    }
    
    welcome_text = welcome_messages[selected_language]
    print(f"AI: {welcome_text}")
    assistant.text_to_speech(welcome_text)

    while True: # Loop to keep the conversation going
        audio_file = assistant.record_audio()
    
        if not audio_file:
            print("AI: Sorry, I couldn't hear you. Please try again.")
            assistant.text_to_speech("Sorry, I couldn't hear you. Please try again.")
            continue

        # Convert speech to text
        text = assistant.speech_to_text(audio_file)

        if not text.strip():
            print("AI: Couldn't understand. Please speak again.")
            assistant.text_to_speech("Couldn't understand. Please speak again.")
            continue


        if selected_language != "en":
            text = assistant.translate_text(text, src_lang=selected_language, dest_lang="en")

         # Get AI response
        if len(assistant.transcript_history) == 0:
            # First turn: Include system prompt
            system_prompt = "You are a helpful AI assistant for customer support. Keep responses short, relevant, and conversational and also help them to book appointments if they need. "
            response = assistant.get_ai_response(system_prompt + text)
        else:
            # Subsequent turns: No system prompt needed
            response = assistant.get_ai_response(text)

        # Exit condition
        exit_commands = {
            "en": ["exit", "quit", "bye"],
            "hi": ["बंद करो", "नमस्ते", "अलविदा"]
        }

        if any(cmd in text.lower() for cmd in exit_commands["en"] + exit_commands["hi"]):
            exit_message = {
                "en": "Thank you for choosing the service. Have a good time.",
                "hi": "सेवा चुनने के लिए धन्यवाद। आपका समय अच्छा रहे।"
            }
            print(f"AI: {exit_message[selected_language]}")
            assistant.text_to_speech(exit_message[selected_language])
            break

        # Get AI response
        response = assistant.get_ai_response(text)

        # Translate back to user's language if needed
        if selected_language != "en":
            response = assistant.translate_text(response, src_lang="en", dest_lang=selected_language)

        print(f"AI: {response}")
        assistant.text_to_speech(response)


if __name__ == "__main__":
    main()

