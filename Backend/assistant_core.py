import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
import Backend.Automation as Automation
from Backend.ImageGeneration import GenerateImages
import asyncio
from Backend.utils import AnswerModifier, QueryModifier, TempDirectoryPath, SetAssistantStatus, GetAssistantStatus

def process_input(user_input):
    output_lines = []
    image_paths = []
    dmm_result, dmm_error = FirstLayerDMM(user_input)
    output_lines.append(f"Decision Model Output: {dmm_result}")
    if dmm_error:
        output_lines.append(f"[DMM Error] {dmm_error}")
        return '\n'.join(output_lines), image_paths
    if not dmm_result or not isinstance(dmm_result, list):
        output_lines.append("Sorry, I couldn't understand your request.")
        return '\n'.join(output_lines), image_paths
    is_command = any(not (item.startswith("general") or item.startswith("realtime")) for item in dmm_result)
    is_realtime = any(item.startswith("realtime") for item in dmm_result)
    if is_command:
        commands = [item for item in dmm_result if not item.startswith("general") and not item.startswith("realtime")]
        for cmd in commands:
            if cmd.startswith("generate image"):
                prompt = cmd[len("generate image"):].strip(" ()")
                output_lines.append(f"[Image Generation] Generating images for: {prompt}")
                success, img_error = GenerateImages(prompt)
                if img_error:
                    output_lines.append(f"[Image Error] {img_error}")
                if success:
                    for i in range(1, 5):
                        img_path = os.path.join("Data", f"{prompt.replace(' ', '_')}{i}.jpg")
                        if os.path.exists(img_path):
                            image_paths.append(img_path)
                            output_lines.append(f"[Image] {img_path}")
                    output_lines.append("Image generation completed.")
                else:
                    output_lines.append("Image generation failed.")
            else:
                output_lines.append(f"[Automation] Executing command: {cmd}")
                try:
                    result, auto_error = asyncio.run(Automation.Automation([cmd]))
                    if auto_error:
                        output_lines.append(f"[Automation Error] {auto_error}")
                    output_lines.append("Command executed." if result else "Command failed.")
                except Exception as e:
                    output_lines.append(f"Command error: {e}")
    elif is_realtime:
        try:
            realtime_query = next(item[9:].strip() for item in dmm_result if item.startswith("realtime"))
            output_lines.append(f"[Realtime] Calling RealtimeSearchEngine with: {realtime_query}")
            answer, rt_error = RealtimeSearchEngine(realtime_query)
            output_lines.append(f"RealtimeSearchEngine answer: {answer}")
            if rt_error:
                output_lines.append(f"[Realtime Error] {rt_error}")
                # fallback to chatbot if desired
            if not answer or (isinstance(answer, str) and 'error' in answer.lower()):
                output_lines.append("Realtime info unavailable, falling back to ChatBot...")
                answer, cb_error = ChatBot(user_input)
                if cb_error:
                    output_lines.append(f"[ChatBot Error] {cb_error}")
                output_lines.append(answer)
            else:
                output_lines.append(answer)
        except Exception as e:
            output_lines.append(f"Realtime info error: {e}")
            answer, cb_error = ChatBot(user_input)
            if cb_error:
                output_lines.append(f"[ChatBot Error] {cb_error}")
            output_lines.append(answer)
    else:
        output_lines.append("[Chat] Calling ChatBot...")
        answer, cb_error = ChatBot(user_input)
        if cb_error:
            output_lines.append(f"[ChatBot Error] {cb_error}")
        output_lines.append(answer)
    return '\n'.join(output_lines), image_paths 