import sys
import os
# Patch sys.path for flexible direct script execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import requests
import datetime
import json
from dotenv import dotenv_values
from groq import Groq
from Backend.utils import AnswerModifier, TempDirectoryPath

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
Google_API_KEY = env_vars.get("Google_API_KEY")
CSE_ID = env_vars.get("CSE_ID")

# Catch missing API keys gracefully
if not GroqAPIKey or not Google_API_KEY:
    print("[yellow]RealtimeSearchEngine missing Groq or Google API keys!\nCheck your .env.[/yellow]")
    # Deliberately do NOT raise anymore!
    GroqAPIKey = None
    Google_API_KEY = None

# Initialize Groq Client (if possible)
client = None
if GroqAPIKey:
    try:
        client = Groq(api_key=GroqAPIKey)
    except Exception as e:
        print(f"[red]Groq client init error: {e}[/red]")

CHAT_LOG_PATH = "Data/ChatLog.json"
os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)

# Load chat history
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []

System = f"""Hello, I am {Username}, You are a very accurate AI chatbot named {Assistantname} with real-time web search.\n*** Always search the internet first before answering. ***\n*** Provide professional and well-structured answers using correct grammar. ***\n*** Never say \"I don't know\"—always attempt to find relevant information. ***"""

def GoogleSearch(query):
    if not Google_API_KEY or not CSE_ID:
        return f"⚠️ Google Search unavailable (missing API key or CSE_ID)", ""
    try:
        print("🔎 Searching Google for:", query)
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={Google_API_KEY}&cx={CSE_ID}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("items", [])
        if not results:
            return "⚠️ No relevant search results found.", ""
        search_summary = f"🔎 **Search results for:** `{query}`\n\n"
        extracted_texts = []
        for result in results[:5]:
            title = result.get("title", "No Title")
            snippet = result.get("snippet", "No Description Available.")
            link = result.get("link", "#")
            extracted_texts.append(f"{title}: {snippet}")
            search_summary += f"🔹 **{title}**\n📄 {snippet}\n🔗 [Read more]({link})\n\n"
        return search_summary.strip(), "\n".join(extracted_texts)
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error fetching search results: {e}", ""

def SystemInformation():
    now = datetime.datetime.now()
    return f"""🕒 **Real-time Information**\n- Day: {now.strftime('%A')}\n- Date: {now.strftime('%d %B %Y')}\n- Time: {now.strftime('%H:%M:%S')}\n"""

def RealtimeSearchEngine(prompt):
    """
    Returns (answer_string, error_message_or_None)
    """
    global messages
    if client is None or not GroqAPIKey:
        msg = "Groq API unavailable for realtime search."
        print(f"[yellow]{msg}[/yellow]")
        return "Realtime search is unavailable.", msg

    messages.append({"role": "user", "content": prompt})
    search_summary, extracted_search_text = GoogleSearch(prompt)
    # If Google API failed, surface that error for the UI
    if search_summary.startswith("⚠️"):
        print(f"[yellow]GoogleSearch: {search_summary}[/yellow]")

    system_context = [
        {"role": "system", "content": System},
        {"role": "system", "content": SystemInformation()},
        {"role": "system", "content": search_summary},
        {"role": "system", "content": f"Relevant search data:\n{extracted_search_text}"}
    ]

    try:
        print("🧠 Processing AI response...")
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=system_context + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )
        answer = "".join(chunk.choices[0].delta.content for chunk in completion if chunk.choices[0].delta.content).strip()
        error = None
    except Exception as e:
        answer = f"⚠️ AI system error: {e}"
        error = str(e)
        print(f"[red]{answer}[/red]")
    messages.append({"role": "assistant", "content": answer})
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f, indent=4)
    return AnswerModifier(answer), error

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        result, err = RealtimeSearchEngine(prompt)
        print(result, "Error:", err)