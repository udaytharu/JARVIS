import sys
import os
# Patch sys.path for flexible direct script testing
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import logging
from time import sleep
from Backend.utils import TempDirectoryPath

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def open_images(prompt):
    """Open generated images."""
    folder_path = r"Data"
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            logging.info(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError as e:
            logging.error(f"Error opening image {image_path}: {e}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_API_KEY = get_key('.env', 'HuggingFaceAPIKey')
if not HF_API_KEY:
    logging.error("HuggingFaceAPIKey not found in .env")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

async def query(payload):
    """Query the Hugging Face API for image generation."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"API query failed: {e}")
        return None

async def generate_images(prompt: str):
    """Generate multiple images concurrently."""
    os.makedirs("Data", exist_ok=True)
    tasks = []
    for i in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(1, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:
            file_path = f"Data/{prompt.replace(' ', '_')}{i+1}.jpg"
            try:
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                logging.debug(f"Image saved: {file_path}")
            except Exception as e:
                logging.error(f"Failed to save image {file_path}: {e}")

def GenerateImages(prompt: str):
    """
    Generate and open images for the given prompt. Returns (success, error_msg_or_None)
    """
    if not HF_API_KEY:
        logging.error("HuggingFaceAPIKey not found in .env")
        return False, "HuggingFace API key missing"
    try:
        asyncio.run(generate_images(prompt))
        open_images(prompt)
        return True, None
    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        return False, str(e)

def main():
    """Monitor ImageGeneration.data and generate images when triggered."""
    data_file = r"C:\Users\Dell\OneDrive\Desktop\my coding practices\python practice\JARVIS-AI 2.0\Frontend\Files\ImageGeneration.data"
    ensure_file_exists(data_file, "None,False")  # Ensure file exists initially

    while True:
        try:
            with open(data_file, "r") as f:
                data = f.read().strip()
            if not data:
                logging.debug("No data in ImageGeneration.data, waiting...")
                sleep(1)
                continue

            prompt, status = data.split(",", 1)
            status = status.strip()

            if status.lower() == "true":
                logging.info(f"Generating images for prompt: {prompt}")
                success, err = GenerateImages(prompt)
                with open(data_file, "w") as f:
                    f.write(f"{prompt},False" if success else "None,False")
                logging.info("Image generation completed" if success else "Image generation failed")
                break  # Exit after one successful run (adjust as needed)
            else:
                logging.debug(f"Status is {status}, waiting...")
                sleep(1)

        except FileNotFoundError:
            logging.warning(f"{data_file} not found, creating it")
            ensure_file_exists(data_file, "None,False")
            sleep(1)
        except Exception as e:
            logging.error(f"Error in image generation loop: {e}")
            sleep(1)

def ensure_file_exists(path, default_content=""):
    """Create file and directory if they don’t exist."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(default_content)
    except Exception as e:
        logging.error(f"Failed to ensure file exists at {path}: {e}")

if __name__ == "__main__":
    prompt = input("Enter prompt for image generation: ")
    result, err = GenerateImages(prompt)
    print("Success:", result, "Error:", err)