import json
import requests
import os
import time
import sys
from copy import deepcopy
import re


TOPIC = sys.argv[1] if len(sys.argv) > 1 else "the_black_death"
TOPIC_DIR = f"examples/{TOPIC.lower().replace(' ', '_')}"

STORYBOARD_PATH = os.path.join(TOPIC_DIR, "storyboard.json")
WORKFLOW_TEMPLATE_PATH = "comfyui/prompt_to_img.json"
OUTPUT_DIR = os.path.join("assets/images", TOPIC.lower().replace(' ', '_'))
COMFYUI_API_URL = "http://localhost:8188/prompt"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_storyboard(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_workflow_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def inject_prompt(workflow, prompt_text):
    modified = deepcopy(workflow)
    for node in modified["nodes"]:
        if node["type"] == "CLIPTextEncode":
            node["inputs"]["text"] = prompt_text
    return modified

def send_to_comfyui(workflow):
    try:
        response = requests.post(COMFYUI_API_URL, json={"prompt": workflow})
        response.raise_for_status()
        result = response.json()
        return result.get("prompt_id")
    except Exception as e:
        print(" ComfyUI error:", e)
        return None

def wait_for_image(prompt_id):
    status_url = f"http://localhost:8188/history/{prompt_id}"
    for _ in range(30):
        time.sleep(1.5)
        try:
            r = requests.get(status_url)
            r.raise_for_status()
            output = r.json()
            images = output.get("outputs", [])[0].get("images", [])
            if images:
                return images[0]["filename"]
        except:
            continue
    return None

def download_image(filename, output_path):
    image_url = f"http://localhost:8188/view?filename={filename}"
    r = requests.get(image_url)
    with open(output_path, "wb") as f:
        f.write(r.content)

def main():
    storyboard = load_storyboard(STORYBOARD_PATH)
    workflow_template = load_workflow_template(WORKFLOW_TEMPLATE_PATH)

    for scene in storyboard:
        scene_number = scene["scene_number"]
        scene_title = scene["scene_title"]

        #  Use regex to extract the full visual description
        match = re.search(r"--- Visual Description ---\s*(.*)", scene["full_output"], re.DOTALL)
        visual_prompt = match.group(1).strip() if match else ""

        if not visual_prompt:
            print(f"Skipping scene {scene_number} (no visual description)")
            continue

        print(f" Generating image for Scene {scene_number}: {scene_title}")
        workflow = inject_prompt(workflow_template, visual_prompt)
        prompt_id = send_to_comfyui(workflow)

        if not prompt_id:
            print(f" Failed to submit prompt for scene {scene_number}")
            continue

        filename = wait_for_image(prompt_id)
        if not filename:
            print(f" Timed out waiting for image for scene {scene_number}")
            continue

        output_path = os.path.join(OUTPUT_DIR, f"scene_{scene_number:02}.png")
        download_image(filename, output_path)
        print(f" Saved: {output_path}")

if __name__ == "__main__":
    main()
