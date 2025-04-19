
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open("ai_assistant.log", "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
