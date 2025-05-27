import json
import requests
import uuid
import os
import time
import random
from collections import defaultdict

FALLBACK_OUTPUT_DIR = r"C:\Users\neeha\Downloads\ComfyUI\output"
COMFYUI_API_URL = "http://127.0.0.1:8188"
WORKFLOW_TEMPLATE_PATH = "comfyui/scene_template.json"
OUTPUT_IMAGE_PATH = "images/scene_{scene_id}.png"

def load_workflow_template():
    with open(WORKFLOW_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def convert_to_prompt_format(workflow_raw):
    prompt = {}

    for node in workflow_raw["nodes"]:
        node_id = str(node["id"])
        class_type = node["type"]
        prompt[node_id] = {
            "class_type": class_type,
            "inputs": {}
        }

        widget_values = node.get("widgets_values", [])

        if class_type == "SaveImage":
            prompt[node_id]["inputs"]["filename_prefix"] = widget_values[0] if widget_values else "AutoDocScene"
        elif class_type == "EmptyLatentImage":
            prompt[node_id]["inputs"]["width"] = widget_values[0]
            prompt[node_id]["inputs"]["height"] = widget_values[1]
            prompt[node_id]["inputs"]["batch_size"] = widget_values[2]
        elif class_type == "CLIPTextEncode":
            prompt[node_id]["inputs"]["text"] = widget_values[0]
        elif class_type == "KSampler":
            prompt[node_id]["inputs"]["seed"] = widget_values[0]
            prompt[node_id]["inputs"]["steps"] = widget_values[2]
            prompt[node_id]["inputs"]["cfg"] = widget_values[3]
            prompt[node_id]["inputs"]["sampler_name"] = widget_values[4]
            prompt[node_id]["inputs"]["scheduler"] = widget_values[5]
            prompt[node_id]["inputs"]["denoise"] = widget_values[6]
        elif class_type == "LoraLoader":
            prompt[node_id]["inputs"]["lora_name"] = widget_values[0]
            prompt[node_id]["inputs"]["strength_model"] = widget_values[1]
            prompt[node_id]["inputs"]["strength_clip"] = widget_values[2]
        elif class_type == "CheckpointLoaderSimple":
            prompt[node_id]["inputs"]["ckpt_name"] = widget_values[0]

    
    port_counters = defaultdict(int)

    for link in workflow_raw["links"]:
        _, from_node_id, from_output_index, to_node_id, _, input_name = link
        from_id = str(from_node_id)
        to_id = str(to_node_id)
        class_type = prompt[to_id]["class_type"]

        mapped_name = input_name
        if class_type == "SaveImage" and input_name.upper() == "IMAGE":
            mapped_name = "images"
        elif class_type == "VAEDecode":
            mapped_name = {"LATENT": "samples", "VAE": "vae"}.get(input_name.upper(), input_name)
        elif class_type == "KSampler":
            if input_name == "MODEL":
                mapped_name = "model"
            elif input_name == "LATENT":
                mapped_name = "latent_image"
            elif input_name == "CONDITIONING":
                mapped_name = "positive" if port_counters[to_id] == 0 else "negative"
                port_counters[to_id] += 1
        elif class_type == "LoraLoader":
            mapped_name = input_name.lower()
        elif class_type == "CLIPTextEncode" and input_name == "CLIP":
            mapped_name = "clip"

        prompt[to_id]["inputs"][mapped_name] = [from_id, from_output_index]

    return prompt

def simplify_prompt(text):
    import re
    text = re.sub(r'\([^)]*\)', '', text)  
    keywords = []

    for line in text.split('.'):
        line = line.strip()
        if any(word in line.lower() for word in ["show", "illustrate", "depict", "visualize", "imagine"]):
            keywords.append(line)
        elif "background" in line.lower() or "foreground" in line.lower():
            keywords.append(line)
        elif len(line.split()) < 15:
            keywords.append(line)

    return ", ".join(keywords)

def modify_workflow_prompt(prompt_data, prompt_text, seed=None):
    simplified = simplify_prompt(prompt_text)
    enriched = f"{simplified}, ultra-detailed, cinematic, 2D digital painting, sharp focus, highly realistic, volumetric lighting"

    for node in prompt_data.values():
        if node["class_type"] == "CLIPTextEncode":
            node["inputs"]["text"] = enriched
        elif node["class_type"] == "KSampler" and seed is not None:
            node["inputs"]["seed"] = seed

    return prompt_data

def trigger_comfyui_workflow(prompt_data):
    prompt_id = str(uuid.uuid4())
    payload = {
        "prompt": prompt_data,
        "prompt_id": prompt_id
    }

    print("===== DEBUG PAYLOAD SENT TO COMFYUI =====")
    print(json.dumps(payload, indent=2))

    response = requests.post(f"{COMFYUI_API_URL}/prompt", json=payload)
    if response.status_code != 200:
        print("ERROR DETAILS:")
        print(response.text)
        raise RuntimeError(f"ComfyUI request failed with prompt_id={prompt_id}")
    return prompt_id

def fetch_output_image_path(prompt_id):
    history_url = f"{COMFYUI_API_URL}/history/{prompt_id}"
    print("[INFO] Waiting for ComfyUI to render image...")
    for _ in range(300):
        response = requests.get(history_url)
        if response.status_code == 200:
            data = response.json()
            if prompt_id in data:
                for output in data[prompt_id]["outputs"].values():
                    for image in output.get("images", []):
                        filename = image.get("filename")
                        subfolder = image.get("subfolder")
                        path = os.path.join(FALLBACK_OUTPUT_DIR, subfolder, filename) if subfolder else os.path.join(FALLBACK_OUTPUT_DIR, filename)
                        if os.path.exists(path):
                            return path
        time.sleep(1)

    print("[WARNING] Using fallback: last modified image from output/")
    all_images = [os.path.join(FALLBACK_OUTPUT_DIR, f) for f in os.listdir(FALLBACK_OUTPUT_DIR) if f.endswith(".png")]
    if not all_images:
        raise TimeoutError("No images found in fallback path either.")
    return max(all_images, key=os.path.getctime)

def generate_image_from_prompt(prompt_text, scene_id):
    seed = random.randint(1000000, 9999999)
    workflow_raw = load_workflow_template()
    prompt_data = convert_to_prompt_format(workflow_raw)
    prompt_data = modify_workflow_prompt(prompt_data, prompt_text, seed)

    print(f"[INFO] Sending prompt to ComfyUI with seed {seed}...")
    prompt_id = trigger_comfyui_workflow(prompt_data)

    image_path = fetch_output_image_path(prompt_id)

    output_path = OUTPUT_IMAGE_PATH.format(scene_id=scene_id)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(image_path, output_path)
    print("Saved image:", output_path)
    return output_path

if __name__ == "__main__":
    test_prompt = "A medieval city square with bustling merchants and plague doctors walking past terrified villagers."
    scene_id = 1
    img_path = generate_image_from_prompt(test_prompt, scene_id)
