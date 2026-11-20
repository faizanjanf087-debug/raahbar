import base64

import requests

import config
from memory import store


def analyze(data, mime_type, prompt, model):
    """Image, audio ya video (chhota file) ko Gemini se samjhane ke liye."""
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY set nahi hai")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": base64.b64encode(data).decode(),
                        }
                    },
                ]
            }
        ]
    }
    response = requests.post(
        url,
        params={"key": config.GEMINI_API_KEY},
        json=body,
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()
    meta = data.get("usageMetadata") or {}
    store.log_usage("gemini", model, meta.get("promptTokenCount", 0), meta.get("candidatesTokenCount", 0))
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(part.get("text", "") for part in parts)
