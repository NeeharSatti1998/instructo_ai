from TTS.api import TTS
import os

narrations = [
    """Imagine a giant ball of hot, glowing gas, lighting up the entire sky. That's what we're talking about - our star, the sun!
    Let's dive into the fascinating world of our nearest celestial neighbor and explore its incredible secrets."""
]

output_dir = "tts_audio"
os.makedirs(output_dir, exist_ok=True)

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

for idx, narration in enumerate(narrations, 1):
    file_path = os.path.join(output_dir, f"scene_{idx}.wav")
    tts.tts_to_file(text=narration, file_path=file_path)
    print(f"Audio saved: {file_path}")
