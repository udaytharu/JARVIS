# ===================== Imports and Setup =====================
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextTOScreen,
    TempDirectoryPath,
    AnswerModifier,
    QueryModifier,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Automation import nav as navigator
from Backend.auth.recoganize import AuthenticateFace  # Import face recognition
import pyautogui
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageGeneration import GenerateImages
from dotenv import dotenv_values
from asyncio import run
from time import sleep, time, localtime
import subprocess
import threading
import json
import os
import logging
import sys
import pyaudio
import numpy as np
import platform
import pygame

# ===================== Logging and Environment =====================
env_vars = dotenv_values(".env")
USERNAME = env_vars.get("Username", "User")
ASSISTANT_NAME = env_vars.get("Assistantname", "Assistant")
DEFAULT_MESSAGE = f'''{USERNAME} 😄: Hello {ASSISTANT_NAME} 🌟, How are you?\n{ASSISTANT_NAME} 🤖: Welcome {USERNAME} 🎉, I am doing well. How may I help you today? 😊'''
subprocesses = []
FUNCTIONS = ["open", "close", "play", "system", "content", "google search", "youtube search", "write", "create presentation", 
             "scroll", "swipe", "pdf", "youtube", "web", "zoom", "page", "home", "end", "next", "previous", "up", "down", 
             "enter", "escape", "tab", "backspace", "delete", "select", "copy", "paste", "cut", "undo", "redo", "save", 
             "find", "replace", "refresh", "fullscreen", "voice type", "type", "screenshot", "take screenshot", "read clipboard",
             "copy to clipboard", "write to clipboard", "minimize window", "maximize window", "switch window", "create file",
             "read file", "screen info", "get screen info", "analyze screen", "screen analysis", "read screen", "read screen text",
             "find text", "click on", "observe screen", "what's on screen"]
os.makedirs("Data", exist_ok=True)
os.makedirs(os.path.join("Frontend", "Files"), exist_ok=True)
last_interaction_time = time()

# ===================== Utility Functions =====================
def play_audio_file(file_path: str) -> bool:
    """Play an audio file using pygame."""
    try:
        if not os.path.exists(file_path):
            logging.warning(f"Audio file not found: {file_path}")
            return False
        
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        logging.info(f"Played audio file: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error playing audio file {file_path}: {e}")
        try:
            pygame.mixer.quit()
        except:
            pass
        return False

def detect_clap():
    """Detect a clap sound using the microphone."""
    CHUNK = 1024
    RATE = 44100
    THRESHOLD = 3000
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
        data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.float32)
        stream.stop_stream()
        stream.close()
        p.terminate()
        amplitude = np.abs(np.max(data))
        logging.debug(f"Clap detection: Amplitude = {amplitude}, Threshold = {THRESHOLD}")
        return amplitude > THRESHOLD
    except Exception as e:
        logging.error(f"Error in clap detection: {e}")
        return False

def show_default_chat_if_no_chats():
    """Show default chat if no previous chats exist."""
    chat_log_path = r"Data\ChatLog.json"
    try:
        with open(chat_log_path, "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                    file.write(DEFAULT_MESSAGE)
    except FileNotFoundError:
        with open(chat_log_path, "w", encoding='utf-8') as file:
            json.dump([], file)
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DEFAULT_MESSAGE)

def read_chat_log_json():
    """Read chat log from JSON file."""
    chat_log_path = r"Data\ChatLog.json"
    try:
        with open(chat_log_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_to_chat_log(user_message: str, assistant_message: str):
    """Save user and assistant messages to ChatLog.json."""
    chat_log_path = r"Data\ChatLog.json"
    try:
        # Read existing chat history
        chat_history = read_chat_log_json()
        
        # Ensure it's a list
        if not isinstance(chat_history, list):
            chat_history = []
        
        # Append new messages
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": assistant_message})
        
        # Save to file
        with open(chat_log_path, 'w', encoding='utf-8') as file:
            json.dump(chat_history, file, indent=4, ensure_ascii=False)
        
        logging.info(f"Saved chat history: {len(chat_history)} messages")
        
        # Update GUI display
        chat_log_integration()
        show_chats_on_gui()
        
    except Exception as e:
        logging.error(f"Error saving to chat log: {e}")

def chat_log_integration():
    """Integrate chat log for display."""
    json_data = read_chat_log_json()
    formatted_chatlog = ""
    for entry in json_data:
        if entry.get("role") == "user":
            formatted_chatlog += f"{USERNAME}: {entry.get('content', '')} 😄\n"
        elif entry.get("role") == "assistant":
            formatted_chatlog += f"{ASSISTANT_NAME}: {entry.get('content', '')} 🌟\n"
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def show_chats_on_gui():
    """Display chats on the GUI."""
    with open(TempDirectoryPath('Database.data'), 'r', encoding='utf-8') as file:
        data = file.read()
    if data:
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(data)

def greet_user_by_time():
    """Greet the user based on the current time."""
    # play_audio_file(r"Frontend/audio/start_sound.mp3") # This line is removed as per the edit hint
    current_hour = localtime().tm_hour
    if 5 <= current_hour < 12:
        greeting = f"Good morning, boss! welcome back I'm {ASSISTANT_NAME}, your personal AI assistant. How can I help to improve your productivity?"
    elif 12 <= current_hour < 17:
        greeting = f"Good afternoon, boss! I'm {ASSISTANT_NAME}, your personal AI assistant. welcome back How can I help you today?"
    else:
        greeting = f"Good evening, boss! I'm {ASSISTANT_NAME}, your personal AI assistant. welcome back Ready to assist you."
    ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: {greeting}")
    TextToSpeech(greeting)
    sleep(0.5)

def check_system():
    """Check if all required system components exist."""
    components = ["Backend", "Frontend", "Data", "Backend/auth"]
    for component in components:
        if not os.path.isdir(component):
            ShowTextTOScreen(f"{ASSISTANT_NAME}: Error - {component} directory missing! 🚫")
            TextToSpeech(f"Error - {component} directory missing")
            return False
    return True

# ===================== Main Assistant Functions =====================
def initial_execution():
    """Run initial setup and greetings with face authentication."""
    global last_interaction_time
    
    # Play startup sound
    startup_sound_path = os.path.join("Frontend", "audio", "start_sound.mp3")
    if os.path.exists(startup_sound_path):
        threading.Thread(target=play_audio_file, args=(startup_sound_path,), daemon=True).start()
    
    ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Initializing face authentication...")
    TextToSpeech("Initializing face authentication")
    sleep(0.5)
    
    # Perform face authentication
    if not AuthenticateFace():
        ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Face authentication failed. Shutting down.")
        TextToSpeech("Face authentication failed. Shutting down.")
        sleep(1)
        sys.exit(1)
    
    ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Face authentication successful. Initializing system...")
    TextToSpeech("Face authentication successful. Initializing system.")
    sleep(0.5)
    
    if not check_system():
        ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Initialization failed. Please fix issues and restart.")
        TextToSpeech("Initialization failed. Please fix issues and restart.")
        sys.exit(1)
    show_default_chat_if_no_chats()
    chat_log_integration()
    show_chats_on_gui()
    greet_user_by_time()
    SetAssistantStatus("Available... ✅")
    last_interaction_time = time()

initial_execution()

def goodbye():
    """Graceful shutdown with immediate termination after greeting."""
    try:
        # Terminate all subprocesses
        for p in subprocesses:
            try:
                if p.poll() is None:  # Check if process is still running
                    p.terminate()
                    p.wait(timeout=5)
            except Exception:
                try:
                    p.kill()  # Force kill if terminate fails
                except Exception:
                    pass
        SetAssistantStatus("Shutting down... 🔚")
        ShowTextTOScreen(f"{ASSISTANT_NAME}: System shutdown complete. See you next time, {USERNAME}!")
        TextToSpeech("System shutdown complete. See you next time!")
        sleep(0.5)  # Brief pause to ensure message is displayed/spoken
        # Kill the terminal
        if platform.system() == "Windows":
            os.system("taskkill /IM cmd.exe /F")
        else:
            os.system("kill -9 $$")
        os._exit(0)  # Forcefully terminate all threads and exit
    except Exception as e:
        logging.error(f"Error during shutdown: {e}")
        SetAssistantStatus("Error during shutdown!")
        ShowTextTOScreen(f"{ASSISTANT_NAME}: Error during shutdown: {e}")
        TextToSpeech("An error occurred during shutdown. Please try again or close the program manually.")
        os._exit(1)  # Force exit even on error

def main_execution():
    """Main user interaction and task execution loop."""
    global last_interaction_time
    SetAssistantStatus("Listening... 👂")
    query, q_error = SpeechRecognition()  # PATCHED: expect (result, error)
    if q_error:
        ShowTextTOScreen(f"Speech recognition error: {q_error}")
        return
    if not query or not query.strip():
        return  # Do nothing if no user input
    last_interaction_time = time()
    ShowTextTOScreen(f"{USERNAME}: {query} 😄")
    SetAssistantStatus("Thinking... 🤔")
    decision, dmm_error = FirstLayerDMM(query)
    if dmm_error:
        ShowTextTOScreen(f"DMM Error: {dmm_error}")
        return
    logging.info(f"Decision: {decision}")
    image_execution = any("generate image" in q for q in decision)
    task_execution = any(any(q.startswith(func) for func in FUNCTIONS) for q in decision)
    merged_query = " and ".join([" ".join(q.split()[1:]) for q in decision if q.startswith("general") or q.startswith("realtime")])
    # Image generation
    if image_execution:
        ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Generating image...")
        threading.Thread(target=TextToSpeech, args=("Generating image",), daemon=True).start()
        with open(r"Frontend\Files\ImageGeneration.data", 'w') as file:
            file.write(f"{query}, True")
        try:
            p1 = subprocess.Popen(
                ['python', r'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
            sleep(1)
            SetAssistantStatus("Available... ✅")
            success_msg = "Image generated successfully!"
            ShowTextTOScreen(f"{ASSISTANT_NAME}: {success_msg} 🎉")
            save_to_chat_log(query, success_msg)
            threading.Thread(target=TextToSpeech, args=("Image generated!",), daemon=True).start()
        except Exception as e:
            logging.error(f"Error starting ImageGeneration.py: {e}")
            error_msg = f"Image generation failed: {str(e)}"
            ShowTextTOScreen(f"{ASSISTANT_NAME}: {error_msg} 😞")
            save_to_chat_log(query, error_msg)
            threading.Thread(target=TextToSpeech, args=("Image generation failed. Please retry.",), daemon=True).start()
        return True
    # Navigation execution
    navigation_commands = [q for q in decision if any(
        q.startswith(nav) or nav in q for nav in [
            "scroll", "swipe", "pdf", "youtube", "web", "zoom", "page", "home", "end", "next", "previous",
            "up", "down", "enter", "escape", "tab", "backspace", "delete", "select", "copy", "paste",
            "cut", "undo", "redo", "save", "find", "replace", "refresh", "fullscreen"
        ])]
    if navigation_commands:
        SetAssistantStatus("Navigating... 🧭")
        def run_navigation_new():
            try:
                nav_results = navigator.run(*navigation_commands) # nav.run returns list of bools
                SetAssistantStatus("Available... ✅")
                if nav_results and all(nav_results):
                    success_msg = "Navigation completed!"
                    ShowTextTOScreen(f"{ASSISTANT_NAME}: {success_msg} 🎉")
                    save_to_chat_log(query, success_msg)
                    threading.Thread(target=TextToSpeech, args=(success_msg,), daemon=True).start()
                else:
                    partial_msg = "Navigation completed with some issues."
                    ShowTextTOScreen(f"{ASSISTANT_NAME}: {partial_msg} 😞")
                    save_to_chat_log(query, partial_msg)
                    threading.Thread(target=TextToSpeech, args=(partial_msg,), daemon=True).start()
            except Exception as e:
                logging.error(f"Navigation execution error: {e}")
                SetAssistantStatus("Available... ✅")
                error_msg = f"Navigation failed: {str(e)}"
                ShowTextTOScreen(f"{ASSISTANT_NAME}: {error_msg} 😞")
                save_to_chat_log(query, error_msg)
                threading.Thread(target=TextToSpeech, args=("Navigation failed. Please try again.",), daemon=True).start()
        threading.Thread(target=run_navigation_new, daemon=True).start()
        return True
    # Task execution (non-navigation)
    automation_commands = [q for q in decision if any(q.startswith(func) for func in [
        "open", "close", "play", "system", "content", "google search", "youtube search", "write", "create presentation",
        "voice type", "type", "screenshot", "take screenshot", "read clipboard", "copy to clipboard", "write to clipboard",
        "minimize window", "maximize window", "switch window", "create file", "read file", "screen info", "get screen info",
        "analyze screen", "screen analysis", "read screen", "read screen text", "find text", "click on", "observe screen",
        "what's on screen", "send mail"
    ])]
    if automation_commands:
        SetAssistantStatus("Executing... 🚀")
        def run_automation():
            from asyncio import run as asyncio_run
            try:
                result, auto_error = asyncio_run(Automation(automation_commands))
                SetAssistantStatus("Available... ✅")
                if auto_error:
                    error_msg = f"Some commands had issues: {auto_error}" if result else f"Command error: {auto_error}"
                    response_msg = f"{ASSISTANT_NAME}: {error_msg} ⚠️"
                    ShowTextTOScreen(response_msg)
                    save_to_chat_log(query, error_msg)
                    threading.Thread(target=TextToSpeech, args=(error_msg,), daemon=True).start()
                elif result:
                    success_msg = "Command completed successfully!"
                    response_msg = f"{ASSISTANT_NAME}: {success_msg} 🎉"
                    ShowTextTOScreen(response_msg)
                    save_to_chat_log(query, success_msg)
                    threading.Thread(target=TextToSpeech, args=(success_msg,), daemon=True).start()
                else:
                    fail_msg = "Command failed. Please try again."
                    response_msg = f"{ASSISTANT_NAME}: {fail_msg} 😞"
                    ShowTextTOScreen(response_msg)
                    save_to_chat_log(query, fail_msg)
                    threading.Thread(target=TextToSpeech, args=(fail_msg,), daemon=True).start()
            except Exception as e:
                logging.error(f"Automation execution error: {e}")
                SetAssistantStatus("Available... ✅")
                error_msg = f"Automation error: {str(e)}"
                response_msg = f"{ASSISTANT_NAME}: {error_msg} ❌"
                ShowTextTOScreen(response_msg)
                save_to_chat_log(query, error_msg)
                threading.Thread(target=TextToSpeech, args=("An error occurred during automation.",), daemon=True).start()
        threading.Thread(target=run_automation, daemon=True).start()
        return True
    # Realtime/general queries
    if any(q.startswith("realtime") for q in decision):
        SetAssistantStatus("Searching... 🔍")
        ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: Searching for your query... 🔍")
        threading.Thread(target=TextToSpeech, args=("Searching for your query",), daemon=True).start()
        def run_realtime():
            answer, rt_error = RealtimeSearchEngine(QueryModifier(merged_query))
            if rt_error:
                ShowTextTOScreen(f"Realtime error: {rt_error}")
            ShowTextTOScreen(f"{ASSISTANT_NAME}: {answer} 🌐")
            SetAssistantStatus("Answering... 💬")
            # RealtimeSearchEngine already saves to ChatLog.json, so we just update the GUI
            if not rt_error:
                chat_log_integration()
                show_chats_on_gui()
            threading.Thread(target=TextToSpeech, args=(answer,), daemon=True).start()
        threading.Thread(target=run_realtime, daemon=True).start()
        return True
    for q in decision:
        if "general" in q:
            SetAssistantStatus("Thinking... 🤔")
            def run_general():
                answer, cb_error = ChatBot(QueryModifier(q.replace("general ", "")))
                if cb_error:
                    ShowTextTOScreen(f"Chatbot error: {cb_error}")
                ShowTextTOScreen(f"{ASSISTANT_NAME}: {answer} 🌟")
                SetAssistantStatus("Answering... 💬")
                # ChatBot already saves to ChatLog.json, so we just update the GUI
                if not cb_error:
                    chat_log_integration()
                    show_chats_on_gui()
                threading.Thread(target=TextToSpeech, args=(answer,), daemon=True).start()
            threading.Thread(target=run_general, daemon=True).start()
            return True
        elif any(word in q.lower() for word in ["exit", "bye", "goodbye"]):
            if goodbye():
                sys.exit(0)
            return True
    
    # Add a small delay after processing to prevent rapid feedback
    sleep(0.5)

def sleep_assistant():
    """Put the assistant into sleep state until user says 'wake up' or 'get up'."""
    SetAssistantStatus("Sleeping... 😴")
    ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: I am now sleeping. Say 'wake up' or 'get up' to continue.")
    TextToSpeech("I am now sleeping. Say wake up or get up to continue.")
    while True:
        query = SpeechRecognition()
        if query and any(phrase in query.lower() for phrase in ["wake up", "get up"]):
            SetAssistantStatus("Available... ✅")
            ShowTextTOScreen(f"{ASSISTANT_NAME} 🤖: I'm back and ready to help!")
            TextToSpeech("I'm back and ready to help!")
            break
        sleep(0.5)

# ===================== Threaded Main Loop =====================
def first_thread():
    global last_interaction_time
    while True:
        current_time = time()
        if (current_time - last_interaction_time) > 60:
            sleep_assistant()
            last_interaction_time = time()
        else:
            main_execution()
        # Add a small delay to prevent rapid feedback and improve performance
        sleep(0.2)

def second_thread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread1 = threading.Thread(target=first_thread, daemon=True)
    thread1.start()
    second_thread()