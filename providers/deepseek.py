import requests

import config

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
    return response.json()["choices"][0]["message"]["content"]
