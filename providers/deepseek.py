import requests

import config
from memory import store

URL = "https://api.deepseek.com/chat/completions"


def chat(messages, model):
    if not config.DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY set nahi hai")
    response = requests.post(
        URL,
        headers={"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"},
        json={"model": model, "messages": messages},
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    usage = data.get("usage") or {}
    store.log_usage("deepseek", model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
    return data["choices"][0]["message"]["content"]
