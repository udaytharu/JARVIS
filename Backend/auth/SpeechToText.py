import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt
from Backend.utils import TempDirectoryPath, SetAssistantStatus, QueryModifier

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

HtmlCode = str(HtmlCode).replace("recognition.lang= '';", f"recognition.lang = '{InputLanguage}';")

with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()

Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chorme/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    driver = None
    driver_error = str(e)

def UniversalTranslator(Text):
    try:
        english_translation = mt.translate(Text, "en", "auto")
        if not english_translation:
            return "", "Translation failed or returned empty."
        return english_translation.capitalize(), None
    except Exception as e:
        return "", str(e)

def SpeechRecognition():
    if driver is None:
        return "", f"Selenium WebDriver failed to start: {driver_error}"
    try:
        driver.get("file:///" + Link)
        driver.find_element(by=By.ID, value="start").click()
    except Exception as e:
        return "", f"Could not load speech recognition HTML: {e}"
    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text
            if Text:
                driver.find_element(by=By.ID, value="end").click()
                if InputLanguage and (InputLanguage.lower() == "en" or "en" in InputLanguage.lower()):
                    return QueryModifier(Text), None
                else:
                    SetAssistantStatus("Translating...")
                    translation, err = UniversalTranslator(Text)
                    return QueryModifier(translation), err
        except Exception as e:
            # Instead of silence, return the error if fails too often (or break if driver closed)
            continue

if __name__ == "__main__":
    while True:
        result, err = SpeechRecognition()
        print("Result:", result, "Error:", err)
            