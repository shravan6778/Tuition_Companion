import re

PHONE_RE = re.compile(r"^\+?[0-9]{10,15}$")


def normalize_phone(value: str) -> str:
    value = re.sub(r"[\s\-()]", "", value)
    if not PHONE_RE.match(value):
        raise ValueError("Enter a valid phone number")
    return value


def phone_to_email(phone: str) -> str:
    """SuperTokens' EmailPassword recipe is email-based, so map the phone to a
    hidden email. Must match phoneToEmail() in the frontend."""
    return f"{phone.lstrip('+')}@phone.tuition-companion.app"