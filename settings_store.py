import json
import os

import config

DEFAULTS = {
    "profile_name": "Owner",
    "chat_model": "auto",  # "auto" ya koi DeepSeek model ID
    "gemini_model": config.GEMINI_MODELS[0],
    "elevenlabs_model": config.ELEVENLABS_MODELS[0],
    "elevenlabs_voice_id": "",
    "approval_timeout": 300,
    "live_auto_speak": True,
}


def load():
    data = dict(DEFAULTS)
    if os.path.exists(config.SETTINGS_PATH):
        with open(config.SETTINGS_PATH, "r", encoding="utf-8") as f:
            data.update(json.load(f))
    return data


def save(updates):
    current = load()
    for key, value in updates.items():
        if key in DEFAULTS:
            current[key] = value
    with open(config.SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    return current
