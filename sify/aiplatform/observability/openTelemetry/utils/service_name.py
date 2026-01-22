import os
import sys
from pathlib import Path
import __main__

INVALID_ENTRY_NAMES = {
    "python",
    "ipython",
    "uvicorn",
    "gunicorn",
    "celery",
    "pytest",
}

def detect_app_name() -> str:
    # 1. __main__ file (BEST for `python app.py`)
    try:
        main_file = getattr(__main__, "__file__", None)
        if main_file:
            name = Path(main_file).stem.lower()
            if name and name not in INVALID_ENTRY_NAMES:
                return name
    except Exception:
        pass

    # 2. sys.argv fallback
    try:
        entry = Path(sys.argv[0]).stem.lower()
        if entry and entry not in INVALID_ENTRY_NAMES:
            return entry
    except Exception:
        pass

    # 3. working directory
    try:
        cwd = Path.cwd().name.lower()
        if cwd:
            return cwd
    except Exception:
        pass

    return "No service"
