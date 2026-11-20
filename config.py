import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Secrets: .env (local) ya Replit Secrets (Replit par) mein rakhein. Kabhi GitHub par nahi.
OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "")
FLASK_SECRET = os.getenv("FLASK_SECRET", "change-me-please")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
VAULT_KEY = os.getenv("VAULT_KEY", "")  # Fernet key, VAULT_KEY ke liye: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

DB_PATH = os.path.join(DATA_DIR, "memory.db")
VPS_PATH = os.path.join(DATA_DIR, "vps.json")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
AUDIT_PATH = os.path.join(DATA_DIR, "audit.log")

# Model IDs: official docs se 2026-11 mein check kiye gaye (api-docs.deepseek.com, ai.google.dev).
# deepseek-chat, deepseek-reasoner aur deepseek-coder band ho chuke hain, is liye list mein nahi.
# Naye model aane par yahin update karein.
DEEPSEEK_MODELS = ["deepseek-flash", "deepseek-v4-pro"]
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-4-argon"]
GEMINI_IMAGE_MODELS = ["gemini-3.1-flash-image", "gemini-3-pro-image", "gemini-nano-banana-2.1"]
ELEVENLABS_MODELS = ["eleven_multilingual_v2", "eleven_turbo_v2_5"]  # ye bhi docs se verify karein
