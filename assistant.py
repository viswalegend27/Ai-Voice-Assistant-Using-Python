from dotenv import load_dotenv
from google import genai
import speech_recognition as sr
import pyttsx3
import time
from prompts import INSTRUCTIONS
import tools

load_dotenv()
client = genai.Client()
model = "gemini-2.0-flash-exp"

# Initialize TTS
try:
    import win32com.client
    engine = win32com.client.Dispatch("SAPI.SpVoice")
    _use_sapi = True
except:
    engine = pyttsx3.init()
    _use_sapi = False

# Initialize speech recognizer
recognizer = sr.Recognizer()

def speak(text):
    print(f"🤖 Assistant: {text}")
    if _use_sapi:
        engine.Speak(text)
    else:
        engine.say(text)
        engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except:
            speak("Sorry, I didn't catch that")
            return ""

def chat_with_gemini(query, retries=3):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model, contents=query)
            return response.text.replace('*', '').replace('#', '')
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                time.sleep(2 ** attempt)
                continue
            return "I couldn't get a response right now"
    return "Service temporarily unavailable"

def generate_response(action, command):
    prompt = f'{INSTRUCTIONS}\nUser said: "{command}". You just: {action}. Respond briefly.'
    return chat_with_gemini(prompt) or "Done, Boss."

def run_assistant():
    commands = {
        "time": tools.handle_time,
        "open youtube": tools.handle_open_youtube,
        "open google": tools.handle_open_google,
        "stop": tools.handle_exit,
        "exit": tools.handle_exit
    }
    
    speak("Hello Boss, I'm online and ready to assist.")
    
    while True:
        command = listen()
        if not command:
            continue
            
        # Check for specific commands
        handler = None
        for key in commands:
            if key in command:
                handler = commands[key]
                break
                
        if handler:
            if handler(command, speak, generate_response) is False:
                break
        else:
            # General query
            speak("Let me check on that for you, Boss.")
            speak(chat_with_gemini(command))

if __name__ == "__main__":
    run_assistant()