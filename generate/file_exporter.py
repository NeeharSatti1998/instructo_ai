import os
import json
import streamlit as st
import re

def sanitize_filename(name):
    # Remove characters
    return re.sub(r'[<>:"/\\|?*]', '', name)


def export_storyboard(storyboard, topic):
    topic_safe = sanitize_filename(topic)
    output_path = os.path.join("examples", topic_safe)
    os.makedirs(output_path, exist_ok=True)

    txt_path = os.path.join(output_path, f"{topic_safe}.txt")
    json_path = os.path.join(output_path, f"{topic_safe}.json")

    with open(txt_path, "w", encoding="utf-8") as f:
        for scene in storyboard:
            f.write(f"Scene {scene['scene_number']}: {scene['scene_title']}\n")
            f.write(scene['full_output'] + "\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2)

    return txt_path, json_path

def get_download_buttons(txt_file: str, json_file: str):
    """
    Adds Streamlit download buttons to the app UI.
    """
    # Read content
    with open(txt_file, "r", encoding="utf-8") as f:
        txt_content = f.read()

    with open(json_file, "r", encoding="utf-8") as f:
        json_content = f.read()

    # Display buttons
    st.download_button(" Download Script (.txt)", txt_content, file_name="script.txt")
    st.download_button(" Download Storyboard (.json)", json_content, file_name="storyboard.json")
