# app/utils/normalize.py
from typing import Any


def diet_to_string(value: Any) -> str | None:
    """
    Normalize dietary_restrictions to a string for API responses and UI.
    Accepts: None, string, dict (e.g. {"note": "Vegetarian"}), anything else.
    """
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    if isinstance(value, dict):
        note = value.get("note")
        if note is None:
            return None
        s = str(note).strip()
        return s if s else None
    s = str(value).strip()
    return s if s else None


def diet_to_db(value: Any) -> dict | None:
    """
    Normalize inbound values for DB storage as JSON object: {"note": "<string>"}.
    Keeps your DB flexible without migrations.
    """
    s = diet_to_string(value)
    if not s:
        return None
    return {"note": s}
