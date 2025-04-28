import json
from typing import Any, Dict

FALLBACK: Dict[str, Any] = {"success": False}

def safe_json(text: str) -> Dict[str, Any]:
    """
    Parse an LLM-generated string that *should* be JSON.
    Returns a dict; on any failure, returns {"success": False}.
    """
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return FALLBACK.copy()