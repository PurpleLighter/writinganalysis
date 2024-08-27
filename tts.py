# tts.py
import pyttsx3

def text_to_speech(text):
    try:
        engine = pyttsx3.init()  # Initialize the text-to-speech engine
        engine.say(text)         # Queue the text to be spoken
        engine.runAndWait()      # Block while processing all the currently queued commands
    except Exception as e:
        print(f"An error occurred in text-to-speech: {e}")