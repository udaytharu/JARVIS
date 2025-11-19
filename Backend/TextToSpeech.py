import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pygame
import random
import asyncio
import edge_tts
from dotenv import dotenv_values
from Backend.utils import ASSISTANT_NAME

env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

async def TextToAudioFile(text) -> (bool, str):
    file_path = r"Data\speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)
    try:
        Communicate = edge_tts.Communicate(text, AssistantVoice, pitch='-5Hz', rate='+15%')
        await Communicate.save(r"Data\speech.mp3")
        return True, None
    except Exception as e:
        return False, str(e)

def TTS(Text, func=lambda r=None: True):
    try:
        result, err = asyncio.run(TextToAudioFile(Text))
        if not result:
            return False, err
        pygame.mixer.init()
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)
        return True, None
    except Exception as e:
        return False, f"Error in TTS: {e}"
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data) > 4 and len(Text) >= 250:
        return TTS("".join(Text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        return TTS(Text, func)

if __name__ == "__main__":
    while True:
        text = input("Enter the text: ")
        result, err = TextToSpeech(text)
        print("Success:", result, "Error:", err)

