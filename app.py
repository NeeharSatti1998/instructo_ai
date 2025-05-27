import streamlit as st
from agent.scene_planner import generate_scene_plan
from agent.script_writer import generate_script_and_visual
from generate.story_builder import build_storyboard
from generate.file_exporter import export_storyboard, get_download_buttons
from run_image_pipeline import generate_image_from_prompt
from TTS.api import TTS
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_normalize, audio_fadein, audio_fadeout
import os
import re


# Setup
st.set_page_config(page_title="AutoDocumentary – KurzAIzt", layout="wide")
st.title(" AutoDocumentary – KurzAIzt")
st.subheader("Create educational videos with a single click")

# Initialize TTS
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
audio_output_dir = "tts_audio"
image_output_dir = "images"
video_output_path = "final_video.mp4"

os.makedirs(audio_output_dir, exist_ok=True)
os.makedirs(image_output_dir, exist_ok=True)

# User input
topic = st.text_input(" Enter a topic:", placeholder="e.g., The Black Death, Nuclear Fusion, Aliens")

if st.button(" Generate Storyboard") and topic:
    with st.spinner("Planning scenes..."):
        scene_plan_raw = generate_scene_plan(topic)

    st.markdown("## Scene Plan")
    st.markdown(scene_plan_raw, unsafe_allow_html=True)

    scenes = []
    for line in scene_plan_raw.strip().split("\n"):
        if line.strip() and ":" in line:
            title, summary = line.split(":", 1)
            scenes.append((title.strip(), summary.strip()))

    with st.spinner("Generating full storyboard..."):
        full_storyboard = build_storyboard(scenes, generate_script_and_visual)

    st.markdown("---")
    st.markdown("## Narration & Visuals")

    failed_scenes = []
    for scene in full_storyboard:
        scene_num = scene['scene_number']
        st.markdown(f"### Scene {scene_num}: {scene['scene_title']}")
        st.markdown(f"**Summary:** {scene['summary']}")

        narration_match = re.search(r"--- Narration ---\n(.*?)(?:\n---|$)", scene['full_output'], re.DOTALL)
        visual_match = re.search(r"--- Visual Description ---\n(.*?)(?:\n---|$)", scene['full_output'], re.DOTALL)

        if narration_match:
            narration = narration_match.group(1).strip()
            st.markdown(f"**Narration:** {narration}")
            audio_path = os.path.join(audio_output_dir, f"scene_{scene_num}.wav")
            if not os.path.exists(audio_path):
                try:
                    tts.tts_to_file(text=narration, file_path=audio_path)
                except Exception as e:
                    failed_scenes.append(scene_num)
                    st.warning(f"TTS failed for Scene {scene_num}: {e}")
            if os.path.exists(audio_path):
                st.audio(audio_path)

        if visual_match:
            visual_prompt = visual_match.group(1).strip()
            st.markdown(f"**Visual Description:** {visual_prompt}")
            with st.spinner(f"Generating image for Scene {scene_num}..."):
                try:
                    image_path = generate_image_from_prompt(visual_prompt, scene_num)
                    st.image(image_path, caption=f"Scene {scene_num} Image")
                except Exception as e:
                    failed_scenes.append(scene_num)
                    st.warning(f"Image failed for Scene {scene_num}: {e}")

    # Export storyboard
    st.markdown("---")
    st.markdown("## Export Your Storyboard")
    txt_file, json_file = export_storyboard(full_storyboard, topic)
    get_download_buttons(txt_file, json_file)
    st.success("Export complete!")

    # Video generation
    st.markdown("---")
    st.markdown("## Final Video")

    
    def generate_video_from_scenes(image_dir="images", audio_dir="tts_audio", output_video="final_video.mp4"):
        clips = []
        audio_files = sorted(f for f in os.listdir(audio_dir) if f.endswith(".wav"))

        for audio_file in audio_files:
            scene_id = int(audio_file.split("_")[1].split(".")[0])
            image_path = os.path.join(image_dir, f"scene_{scene_id}.png")
            audio_path = os.path.join(audio_dir, audio_file)

            if os.path.exists(image_path):
                try:
                    audio = AudioFileClip(audio_path).fx(audio_normalize).set_fps(44100)
                    audio = audio.fx(audio_fadein, 0.2).fx(audio_fadeout, 0.2)

                    img_clip = ImageClip(image_path).set_duration(audio.duration).set_audio(audio)
                    img_clip = img_clip.set_fps(24).resize(height=720)
                    clips.append(img_clip)
                except Exception as e:
                    st.warning(f"Failed to process scene {scene_id}: {e}")

        if not clips:
            raise RuntimeError("No valid scenes with both image and audio found.")

        final_clip = concatenate_videoclips(clips, method="compose")

        try:
            output_path = os.path.abspath(video_output_path)
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)
            return output_path
        except Exception as e:
            st.error(f"Video export failed: {e}")
            return None


    with st.spinner("Stitching scenes into final video..."):
        try:
            video_file = generate_video_from_scenes()
            if video_file and os.path.exists(video_file):
                st.success("Final video generated successfully!")
                st.video(video_file)
            else:
                st.warning("Video not found after generation.")
        except Exception as e:
            st.error(f"Video generation failed: {e}")