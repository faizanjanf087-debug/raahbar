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


PROFILE_DIR = os.path.join(config.DATA_DIR, "browser_profile")
ALLOWED_ACTIONS = {"click", "type"}


def _check_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("sirf http:// ya https:// URL chalega")


def check_url(url):
    _check_url(url)


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


def run_actions(url, actions):
    """Approval ke baad hi chalta hai. Har step: click ya type.

    Password fields par ye kaam nahi karta. Login aap khud karein.
    Browser profile data/browser_profile mein rehti hai (cookies wahan save hoti hain).
    """
    _check_url(url)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("playwright install karein") from exc

    os.makedirs(PROFILE_DIR, exist_ok=True)
    steps = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(PROFILE_DIR, headless=True)
        try:
            page = ctx.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            for act in actions:
                kind = act.get("action", "")
                selector = act.get("selector", "")
                if kind not in ALLOWED_ACTIONS:
                    raise ValueError(f"action '{kind}' allowed nahi")
                if not selector:
                    raise ValueError("selector khali hai")
                el = page.locator(selector).first
                if el.count() == 0:
                    raise ValueError(f"element nahi mila: {selector}")
                input_type = (el.get_attribute("type") or "").lower()
                if input_type == "password" or "password" in selector.lower():
                    raise PermissionError("password fields par agent kaam nahi karta, khud daalein")
                if kind == "click":
                    el.click(timeout=10000)
                else:
                    el.fill(act.get("text", ""), timeout=10000)
                steps.append(f"{kind} ok: {selector}")
            page.wait_for_load_state("domcontentloaded")
            title = page.title()
            text = page.inner_text("body")[:MAX_TEXT]
        finally:
            ctx.close()

    audit.log("browser_actions", url=url, steps=len(steps))
    return {"title": title, "text": text, "steps": steps}
