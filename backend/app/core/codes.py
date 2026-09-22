import secrets
from typing import Callable

# No 0/O/1/I so codes are easy to read aloud and type on a phone.
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def generate_unique_code(exists: Callable[[str], bool], length: int = 6, attempts: int = 10) -> str:
    for _ in range(attempts):
        code = generate_code(length)
        if not exists(code):
            return code
    raise RuntimeError("Could not generate a unique code")