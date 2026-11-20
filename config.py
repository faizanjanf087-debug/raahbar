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

# Model IDs ko provider ki official docs se verify karke yahan update karein.
DEEPSEEK_MODELS = ["deepseek-v4-flash", "deepseek-chat", "deepseek-reasoner"]
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
ELEVENLABS_MODELS = ["eleven_multilingual_v2", "eleven_turbo_v2_5"]
