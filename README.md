# AutoDocumentary – InstructoAI

This project generates fully narrated educational videos, using local LLMs via Ollama, CPU-based ComfyUI image generation, and realistic voice synthesis via Coqui TTS.

---

##  Features

- Scene-by-scene topic breakdown using local LLMs (Ollama)
- Narration + visual description generation
- TTS voice generation with [Jenny VITS model](https://github.com/dioco-group/jenny-tts-dataset)
- ComfyUI-based image generation using CPU
- Automatic video creation (image + narration stitched)
- Streamlit frontend for seamless usage

---

##  Folder Structure

```
AutoDocumentary/
├── app.py                       # Main Streamlit app
├── run_image_pipeline.py       # ComfyUI image generation bridge
├── comfyui/
│   └── scene_template.json     # ComfyUI CPU workflow
├── agent/
│   ├── scene_planner.py        # LLM scene planning
│   ├── script_writer.py        # LLM narration & visuals
├── generate/
│   ├── story_builder.py        # Builds storyboard
│   ├── file_exporter.py        # Exports TXT & JSON
├── tts_audio/                  # Auto-generated audio files
├── images/                     # Auto-generated scene images
├── requirements.txt
├── .gitignore
└── README.md
```

---

##  Setup Instructions

### 1. Python Setup (CPU ONLY)

Coqui TTS requires Python 3.10. Install with:
```bash
pyenv install 3.10.13
pyenv local 3.10.13
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

If you face `torch not compiled with CUDA` errors, force CPU with:
```python
TTS(model_name="tts_models/en/jenny/jenny", gpu=False)
```

---

##  Run the App
```bash
streamlit run app.py
```

---

##  Known Limitations

- **Image generation is CPU-based**, which may produce less detailed or repetitive visuals. GPU inference with better models is recommended.
- **Voice quality** is improved using `jenny` model, but may still break under long scenes. Use fade-in/out smoothing.
- Ollama's model (e.g., Mistral) may occasionally hallucinate or drift — future improvements may involve prompt tuning or LLM replacement.

---

##  Improvements

- Replace CPU with GPU inference in ComfyUI (e.g., install on CUDA device)
- Add Whisper for auto-subtitles
- Animate scenes via Deforum/AnimateDiff (next milestone)
