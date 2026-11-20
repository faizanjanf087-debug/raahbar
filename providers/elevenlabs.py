import requests

import config

BASE = "https://api.elevenlabs.io/v1"


def _headers():
    if not config.ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY set nahi hai")
    return {"xi-api-key": config.ELEVENLABS_API_KEY}


def list_voices():
    response = requests.get(f"{BASE}/voices", headers=_headers(), timeout=30)
    response.raise_for_status()
    return [
        {"id": v["voice_id"], "name": v["name"]}
        for v in response.json().get("voices", [])
    ]


def tts(text, voice_id, model_id):
    response = requests.post(
        f"{BASE}/text-to-speech/{voice_id}",
        headers={**_headers(), "Accept": "audio/mpeg"},
        json={"text": text, "model_id": model_id},
        timeout=120,
    )
    response.raise_for_status()
    return response.content


def stt(audio_bytes, filename, mime_type):
    response = requests.post(
        f"{BASE}/speech-to-text",
        headers=_headers(),
        data={"model_id": "scribe_v1"},
        files={"file": (filename, audio_bytes, mime_type)},
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("text", "")
