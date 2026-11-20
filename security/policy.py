"""Har command ko teen levels mein classify karta hai.

read      -> bina poochhe chalega (status, list, cat)
write     -> aap ki approval ke baad chalega
blocked   -> kabhi nahi chalega
"""

READ_COMMANDS = {"uptime", "df", "free", "ls", "cat", "whoami", "ps", "du", "tail", "head"}

BLOCKED_PATTERNS = [
    "rm -rf /",
    "mkfs",
    "shutdown",
    "reboot",
    "dd if=",
    ":(){",
    "> /dev/sd",
]


def classify(command):
    lowered = command.strip().lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            return "blocked"
    first_word = lowered.split()[0] if lowered else ""
    if first_word in READ_COMMANDS and ";" not in lowered and "&&" not in lowered:
        return "read"
    return "write"
