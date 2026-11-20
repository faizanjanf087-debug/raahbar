"""Read-only browser tool (Playwright).

Sirf ye kaam hote hain: page kholna, text nikalna, screenshot lena.
Click, type, login ya form submit ye tool KHUD nahi karta. Aisi
cheezein aap ke khud karne ke liye hain, ya approval flow mein aayengi.
"""
import os
import time
from urllib.parse import urlparse

import config
from security import audit

SHOTS_DIR = os.path.join(config.DATA_DIR, "screenshots")
MAX_TEXT = 4000


def _check_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("sirf http:// ya https:// URL chalega")


def read_page(url, screenshot=False):
    _check_url(url)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("playwright install karein: pip install playwright && playwright install chromium") from exc

    os.makedirs(SHOTS_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            title = page.title()
            text = page.inner_text("body")[:MAX_TEXT]
            shot_path = None
            if screenshot:
                shot_path = os.path.join(SHOTS_DIR, f"shot-{int(time.time())}.png")
                page.screenshot(path=shot_path, full_page=False)
        finally:
            browser.close()

    audit.log("browse_read", url=url, screenshot=bool(shot_path))
    return {"title": title, "text": text, "screenshot": shot_path}
