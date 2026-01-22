import sys
from pathlib import Path

INVALID_ENTRY_NAMES = {"python", "ipython", "gunicorn", "uvicorn", "pytest"}

def detect_app_name(default="sify-client-app"):
    try:
        entry = Path(sys.argv[0]).stem.lower()
        if entry and entry not in INVALID_ENTRY_NAMES:
            return entry
    except Exception:
        pass

    try:
        return Path.cwd().name.lower()
    except Exception:
        return default
