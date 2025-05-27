import requests

OLLAMA_MODEL = "llama3"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
SYSTEM_PROMPT_PATH = "agent/system_prompt.txt"


def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r") as file:
        return file.read()


def generate_script_and_visual(scene_title: str, scene_summary: str):
    system_prompt = load_system_prompt()

    user_prompt = f"""
You are working on an educational video in the style of Kurzgesagt.
You are currently writing one scene.

Scene Title: {scene_title}
Scene Summary: {scene_summary}

Please generate:
1. A voiceover narration (2–5 sentences, clear, curious, and factual)
2. A visual description for this scene formatted specifically to help an image generation AI (running on CPU) better understand and produce the correct illustration.

Be explicit. Include:
- Main subject and setting (e.g. “a medieval town square”)
- Art style (e.g. “2D digital painting” or “flat vector art”)
- Lighting and mood (e.g. “warm, glowing light”, “eerie and dark”)
- Composition hints (e.g. “focus on foreground doctor, blurred crowd in background”)
- Key objects or symbolic elements (e.g. “red arrows indicating trade routes”)
Return in this format:

--- Narration ---
<your narration here>

--- Visual Description ---
<your visual description here>
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"<|system|>\n{system_prompt}\n<|user|>\n{user_prompt.strip()}\n",
        "stream": False
    }

    response = requests.post(OLLAMA_API_URL, json=payload)
    if response.status_code != 200:
        raise RuntimeError(f"Ollama generation failed: {response.text}")

    return response.json()["response"].strip()
