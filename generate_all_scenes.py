import re
from run_image_pipeline import generate_image_from_prompt

def extract_scene_prompts(text):
    pattern = r'--- Visual Description ---\n(.*?)\n(?=Scene|\Z)'
    return re.findall(pattern, text, re.DOTALL)

def main():
    with open("scene_plan.txt", "r", encoding="utf-8") as f:
        content = f.read()

    visual_descriptions = extract_scene_prompts(content)
    print(f"[INFO] Found {len(visual_descriptions)} scenes.")

    for idx, desc in enumerate(visual_descriptions, 1):
        prompt = desc.strip().replace("\n", " ")
        print(f"\n[Scene {idx}] Generating image...")
        try:
            path = generate_image_from_prompt(prompt, idx)
            print(f"Scene {idx} saved to: {path}")
        except Exception as e:
            print(f"Scene {idx} failed: {e}")

if __name__ == "__main__":
    main()
