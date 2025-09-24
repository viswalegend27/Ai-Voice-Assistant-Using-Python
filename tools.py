import webbrowser
import datetime


def handle_time(command, speak, generate_response):
    """Gets the current time and speaks it out."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    response_text = generate_response(f"I found the current time, it is {now}.", command)
    speak(response_text)
    return True # Keep running

def handle_open_youtube(command, speak, generate_response):
    """Opens YouTube in the web browser."""
    webbrowser.open("https://www.youtube.com")
    response_text = generate_response("I opened YouTube in the web browser.", command)
    speak(response_text)
    return True # Keep running

def handle_open_google(command, speak, generate_response):
    """Opens Google in the web browser."""
    webbrowser.open("https://www.google.com")
    response_text = generate_response("I opened Google in the web browser.", command)
    speak(response_text)
    return True # Keep running

def handle_exit(command, speak, generate_response):
    """Handles the exit command and signals the loop to stop."""
    response_text = generate_response("I am shutting down.", command)
    speak(response_text)
    return False # Return False to signal the loop to stop