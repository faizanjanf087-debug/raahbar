"""Auto mode: DeepSeek khud decide karta hai ke ye message kis model se jaye.

general   -> deepseek-flash (tez, sasta, roz ke kaam)
code      -> deepseek-flash (coder ka alag model 2026-11 mein maujood nahi)
reasoning -> deepseek-v4-pro (mushkil logic, tajziya, plan)

Model IDs docs se check kiye gaye hain. Badle to config.py mein update karein.
"""
from providers import deepseek

ROUTES = {
    "general": "deepseek-flash",
    "code": "deepseek-flash",
    "reasoning": "deepseek-v4-pro",
}

ROUTER_PROMPT = (
    "Neeche user ka message hai. Sirf ek lafz jawab do: general, code, ya reasoning.\n"
    "code: programming, debugging, scripts, commands.\n"
    "reasoning: mushkil logic, math, detailed tajziya, step-by-step plan.\n"
    "general: baaki sab, jaise baat-cheet, likhna, sawalon ke seedhe jawab."
)


def pick(text, chat_setting):
    """chat_setting 'auto' ho to message dekh kar model chuno, warna wahi model."""
    if chat_setting != "auto":
        return chat_setting
    try:
        answer = deepseek.chat(
            [
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": text[:2000]},
            ],
            ROUTES["general"],
        ).strip().lower()
    except Exception:
        return ROUTES["general"]
    for key in ("code", "reasoning", "general"):
        if key in answer:
            return ROUTES[key]
    return ROUTES["general"]
