import requests
import json

OLLAMA_MODEL = "llama3"  
OLLAMA_API_URL = "http://localhost:11434/api/generate"

SYSTEM_PROMPT_PATH = "agent/system_prompt.txt"


def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r") as file:
        return file.read()


def generate_scene_plan(topic: str, num_scenes: int = 6):
    system_prompt = load_system_prompt()
    user_prompt = (
        f"Your task is to break down the topic '{topic}' into approximately {num_scenes} logical scenes "
        "that would be used to create an engaging, Kurzgesagt-style educational video. "
        "List each scene with a short title and 1-line summary of what it will cover."
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt}\n",
        "stream": False
    }

    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to get response from Ollama: {response.text}")

    return response.json()["response"]
