from TTS.utils.manage import ModelManager

model_name = "tts_models/en/jenny/jenny"
manager = ModelManager()
model_path, config_path, model_item = manager.download_model(model_name)

vocoder_name = model_item["default_vocoder"]
vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

print("Paths:")
print("Model Path:", model_path)
print("Config Path:", config_path)
print("Vocoder Path:", vocoder_path)
print("Vocoder Config Path:", vocoder_config_path)