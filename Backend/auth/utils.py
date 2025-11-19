import os
from dotenv import dotenv_values

# Load environment variables once
_ENV_VARS = dotenv_values('.env')
ASSISTANT_NAME = _ENV_VARS.get('Assistantname', 'Assistant')
USERNAME = _ENV_VARS.get('Username', 'User')

# Utilities

def AnswerModifier(answer):
    """Clean and format answer text."""
    lines = answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query):
    """Format query with proper punctuation."""
    new_query = query.lower().strip()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"
    ]
    if any(word in new_query for word in question_words):
        if not new_query.endswith('?'):
            new_query += "?"
    else:
        if not new_query.endswith('.'): 
            new_query += "."
    return new_query.capitalize()

# Directory helpers (relative to project root)
CURRENT_DIR = os.getcwd()
TempDirPath = os.path.join(CURRENT_DIR, "Frontend", "Files")
GraphicsDirPath = os.path.join(CURRENT_DIR, "Frontend", "Graphics")

def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)

def GraphicDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)

def SetAssistantStatus(status):
    try:
        with open(os.path.join(TempDirPath, 'Status.data'), "w", encoding='utf-8') as file:
            file.write(status)
    except Exception as e:
        print(f"Error setting assistant status: {e}")

def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, 'Status.data'), "r", encoding='utf-8') as file:
            return file.read().strip()
    except Exception:
        return "Ready! 🚀"
