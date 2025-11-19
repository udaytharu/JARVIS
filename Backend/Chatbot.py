import sys
import os
# Patch sys.path for standalone script dev use
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from Backend.utils import AnswerModifier

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = None
if GroqAPIKey:
    try:
        client = Groq(api_key=GroqAPIKey)
    except Exception as api_error:
        print(f"[red]Groq initialization error: {api_error}[/red]")

messages = []
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.\n*** Do not tell time until I ask, do not talk too much, just answer the question.***\n*** Reply in only English, even if the question is in Hindi, reply in English.***\n*** Do not provide notes in the output, just answer the question and never mention your training data. ***\n"""
SystemChatBot = [{"role": "system", "content": System}]

chat_log_path = "Data/ChatLog.json"
os.makedirs(os.path.dirname(chat_log_path), exist_ok=True)

# ---
def ChatBot(query):
    """
    Query Groq chatbot for an answer. Returns (answer_string, error_message_or_None)
    """
    global messages
    if client is None:
        msg = "Groqkey missing or initialization failed."
        print(f"[yellow]{msg}[/yellow]")
        return "Sorry, chatbot is unavailable right now.", msg
    try:
        messages.append({"role": "user", "content": query})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": answer})
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)
        return AnswerModifier(answer), None
    except Exception as e:
        msg = f"Groq chatbot error: {e}"
        print(f"[red]{msg}[/red]")
        return "Sorry, I couldn't answer due to an internal error.", msg

if __name__ == "__main__":
    while True:
        response, err = ChatBot(input("Enter Your Question: "))
        print(response, "Error:", err)
