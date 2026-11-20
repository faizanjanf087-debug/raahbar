"""Voice generation (text se MP3) aur voice cloning (consent ke saath)."""
import os
import time

import config
from providers import elevenlabs
from security import audit
from settings_store import load as load_settings

AUDIO_DIR = os.path.join(config.DATA_DIR, "audio")
MAX_CHARS = 2000
MAX_SAMPLES = 5
MAX_SAMPLE_BYTES = 10 * 1024 * 1024


def generate(text):
    """Text ko MP3 banata hai aur file ka naam wapas deta hai."""
    text = (text or "").strip()
    if not text:
        raise ValueError("text khali hai")
    settings = load_settings()
    if not settings["elevenlabs_voice_id"]:
        raise ValueError("Settings mein voice select karein")
    audio = elevenlabs.tts(text[:MAX_CHARS], settings["elevenlabs_voice_id"], settings["elevenlabs_model"])
    os.makedirs(AUDIO_DIR, exist_ok=True)
    name = f"voice-{int(time.time())}.mp3"
    with open(os.path.join(AUDIO_DIR, name), "wb") as f:
        f.write(audio)
    audit.log("voice_generated", file=name, chars=len(text))
    return name


def clone(name, samples, consent):
    """samples: [(filename, bytes, mime_type), ...]. Consent ke bina nahi chalega."""
    if not consent:
        raise PermissionError(
            "clone ke liye consent zaroori hai: sirf apni awaaz ya us shakhs ki jis ki likhit ijazat ho"
        )
    if not samples:
        raise ValueError("kam az kam ek audio sample chahiye")
    if len(samples) > MAX_SAMPLES:
        raise ValueError(f"zyada se zyada {MAX_SAMPLES} samples")
    for _, data, _ in samples:
        if len(data) > MAX_SAMPLE_BYTES:
            raise ValueError("har sample 10MB se chhota hona chahiye")
    voice_id = elevenlabs.add_voice(name or "Cloned voice", samples)
    audit.log("voice_cloned", name=name, voice_id=voice_id, samples=len(samples))
    return voice_id
