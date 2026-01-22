import os
import sys
from pathlib import Path
 
def detect_app_name() -> str:
    try:
        entry = Path(sys.argv[0]).stem
        if entry and entry not in {"python", "ipython"}:
            return entry
    except Exception:
        pass
 
    try:
        cwd_name = Path.cwd().name
        if cwd_name:
            return cwd_name
    except Exception:
        pass
 
    return "sify-client-app"