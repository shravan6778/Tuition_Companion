import re

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,30}$")
PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def normalize_username(value: str) -> str:
    value = value.strip().lower()
    if not USERNAME_RE.match(value):
        raise ValueError("Username must be 3-30 characters: lowercase letters, numbers, underscore only")
    return value


def username_to_email(username: str) -> str:
    """SuperTokens' EmailPassword recipe is email-based, so map the username to a
    hidden email. Must match usernameToEmail() in the frontend."""
    return f"{username}@user.tuition-companion.app"


def normalize_phone(value: str) -> str:
    value = re.sub(r"[\s\-()]", "", value)
    if not PHONE_RE.match(value):
        raise ValueError("Enter a valid phone number")
    return value