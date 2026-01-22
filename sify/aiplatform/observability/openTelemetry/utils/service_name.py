# utils/app_detection.py
import os
import sys
from pathlib import Path
from typing import Optional

INVALID_ENTRY_NAMES = {
    "python",
    "ipython",
    "gunicorn",
    "uvicorn",
    "pytest",
}

def detect_app_name(default: str = "sify-client-app") -> str:
    service = os.getenv("OTEL_SERVICE_NAME")
    if service:
        return service


    # 2. Entrypoint
    try:
        entry = Path(sys.argv[0]).stem.lower()
        if entry and entry not in INVALID_ENTRY_NAMES:
            return entry
    except Exception:
        pass

    # 3. Current working directory
    try:
        cwd = Path.cwd().name.lower()
        if cwd:
            return cwd
    except Exception:
        pass

    # 4. Final fallback
    return default
