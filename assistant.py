import datetime
import webbrowser
from dotenv import load_dotenv 
from google import genai
from google.genai import errors as genai_errors 
import time, random
import pyttsx3
import speech_recognition as sr
from prompts import INSTRUCTIONS 
import tools 

load_dotenv() 
client = genai.Client()
model =  "gemini-2.0-flash-exp"

# Inititalizing our Python text-to-speech
engine = pyttsx3.init()

# Function to convert text into speech
def speak(text):
    print("🤖 Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    
    # Capture input from the microphone
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    
    try:
        # Recognize speech and store the command
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    
    except sr.UnknownValueError:
        # Handles case when speech was not understood
        speak("Sorry, I didn't catch that")
        return ""
    
    except sr.RequestError:
        # Handles case when the speech recognition service is unavailable
        speak("Speech service is not working")
        return ""    
# model = "gemini-2.0-flash-exp"
def chat_with_gemini(query):
    try:
        response = client.models.generate_content(
            model=model,
            contents=query
        )
        # Extract text safely (Gemini response objects may vary)
        return getattr(response, "text", "No response text available")
    except Exception as e:
        print("Gemini Error ⚠️", e)
        return "I couldn't get a response from Gemini right now"

# Function to set limitations to models and show the expected error
# Loops through our code and returns content or Show our the RuntimeError
def gen_backoff(c, model, contents, max_retries=5, base=1, max_delay=30):
    for i in range(max_retries):
        try:
          # Calling gemini api 
            return c.models.generate_content(model=model, contents=contents)
        except genai_errors.ClientError as e:
            if getattr(e, "status_code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e).upper():
                t = min(max_delay, base * (2 ** i)) + random.random()
                print(f"429 retry {i+1}, sleeping {t:.1f}s") 
                time.sleep(t) 
                continue
            raise
    raise RuntimeError("exhausted retries (429)")
  
def generate_response(action_description, user_command):
    # (This function stays exactly the same as in the previous example)
    prompt = f"""{INSTRUCTIONS}
    
    Context: The user said "{user_command}".
    As the AI assistant, you have just performed the following action: {action_description}.
    
    Now, generate a brief, natural response to inform the user that you've completed their request.
    """
    try:
        response = gen_backoff(client, model, prompt)
        return getattr(response, "text", "Got it, Boss.")
    except Exception as e:
        print(f"Error generating dynamic response: {e}")
        return "Done, Boss."

def handle_general_query(command):
    speak("Let me check on that for you, Boss.")
    answer = chat_with_gemini(command)
    speak(answer)
    
def run_assistant():
    # Map command strings to the functions imported from tools.py
    commands = {
        "time": tools.handle_time,
        "open youtube": tools.handle_open_youtube,
        "open google": tools.handle_open_google,
        "stop": tools.handle_exit,
        "exit": tools.handle_exit
    }

    speak("Hello Boss, I'm online and ready to assist.")
    
    running = True
    while running:
        command = listen()
        if not command:
            continue
        triggered_command = None
        for key in commands.keys():
            if key in command:
                triggered_command = key
                break
        
        if triggered_command:
            # Get the function from the dictionary
            handler_function = commands[triggered_command]
            
            if handler_function(command, speak, generate_response) is False:
                running = False
        else:
            handle_general_query(command)

if __name__ == "__main__":
    run_assistant()