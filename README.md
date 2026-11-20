# Raahbar (V4)

Flask ka personal AI assistant. Chat, live call, VPS status aur approvals.

## Setup

1. `pip install -r requirements.txt`
2. `.env.example` ko `.env` mein copy karein, aur values daalein.
3. VAULT_KEY banayein:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
4. `python app.py`, phir `http://localhost:8080` kholein.

Replit par: Secrets mein same keys daalein, aur Run dabaayein.

## Features

- **Chat:** DeepSeek se jawab. `@` se pichli baat mention karein. `+` se image, audio ya video upload karein.
- **Live call:** Hold to talk (ElevenLabs STT, DeepSeek, ElevenLabs TTS). Mute, camera, aur snapshot ka option.
- **VPS:** add/remove. Key encrypted save hoti hai. `/status <id>` read-only hai.
- **Commands:** `/run <vps_id> <command>` pehle approval maangti hai. Blocked commands kabhi nahi chalte.
- **Approvals:** har write action ke liye popup. Timeout settings mein.
- **History:** pichla 1 ghanta, 1 din, ya sab delete.
- **Settings:** DeepSeek, Gemini, ElevenLabs models aur voice.
- **Audit log:** har important action ka record.
- **Browser:** `/browse <url>` page ka text nikalta hai (read-only). `/act <url> | click | <selector>` ya `/act <url> | type | <selector> | <text>` har step ke liye approval maangta hai. Password fields par agent kaam nahi karta, login aap khud karein.
- **Scheduled tasks:** `/schedule add <minutes> <command>`, `/schedule list`, `/schedule remove <id>`. Ya Scheduled tasks tab se. Sirf read-only kaam schedule hote hain.
- **Hands-free live call:** Live Call mein "Hands-free" on karein. Awaaz ruk jaye to message khud bheja jaata hai (simple VAD).
- **PWA:** browser mein "Add to Home Screen" karke app ki tarah khul sakta hai (manifest aur service worker).

## Playwright setup (browse ke liye)

```
pip install playwright
playwright install chromium
```

## Sahi istemaal ke liye

- Credentials kabhi chat mein na likhein. Passwords ke liye popup mein khud daalein.
- VPS par alag user banaein jiske paas sirf zaroori permissions hon.
- Replit free plan par app sleep ho sakti hai, is liye lamba kaam VPS par chalana behtar hai.
- Repo ko private rakhein, aur data/ aur .env kabhi commit na karein.

## Abhi kya adhoora hai

- Live call full-duplex nahi hai. Hands-free simple VAD hai, real-time streaming nahi.
- Browser automation ek step ek approval se chalta hai. Multi-step flow aur screenshot approval card ka kaam agle version mein.
- Browser profile (cookies) data/browser_profile mein rehti hai. Ise Replit par persist karne ke liye Replit storage ka dhyan rakhein.
- Gemini "live" mode ka real-time streaming abhi shamil nahi.
- Video ko frames mein tod kar analyze karna abhi nahi hai. Chhoti video seedha Gemini ko jaati hai (20MB tak).
- Ye code sirf lokal test hua hai, aur is session mein packages install nahi ho sake, is liye pehli baar chalane par error aa sakta hai.
