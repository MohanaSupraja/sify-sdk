# import os
# import sys
# from pathlib import Path
 
# def detect_app_name() -> str:
 
 
#     # if os.getenv("OTEL_SERVICE_NAME"):
#     #     return os.getenv("OTEL_SERVICE_NAME")
 
#     # try:
#     #     entry = Path(sys.argv[0]).stem
#     #     if entry and entry not in {"python", "ipython"}:
#     #         return entry
#     # except Exception:
#     #     pass
 
#     # try:
#     #     cwd_name = Path.cwd().name
#     #     if cwd_name:
#     #         return cwd_name
#     # except Exception:
#     #     pass
 
#     return "sify-client-app"


# sify_monitoring_sdk/app_detection.py

import sys
from pathlib import Path

INVALID_ENTRY_NAMES = {
    "python",
    "ipython",
    "gunicorn",
    "uvicorn",
    "pytest",
}


# def _from_entrypoint() -> str | None:
#     """
#     Detect app name from entry-point script.
#     Example:
#         python order_service.py -> order_service
#     """
#     try:
#         entry = Path(sys.argv[0]).stem.lower()
#         if entry and entry not in INVALID_ENTRY_NAMES:
#             return entry
#     except Exception:
#         pass
#     return "unknown entrypoint app"


# def _from_pyproject() -> str | None:
#     """
#     Detect app name from pyproject.toml
#     """
#     path = Path.cwd() / "pyproject.toml"
#     if not path.exists():
#         return "no path"

#     try:
#         import tomllib  # Python 3.11+
#         data = tomllib.loads(path.read_text())
#         return data.get("project", {}).get("name")
#     except Exception:
#         return "unknown pyproject app"


# def _from_setup_cfg() -> str | None:
#     """
#     Detect app name from setup.cfg
#     """
#     path = Path.cwd() / "setup.cfg"
#     if not path.exists():
#         return "no path"

#     try:
#         for line in path.read_text().splitlines():
#             if line.strip().startswith("name"):
#                 return line.split("=")[1].strip()
#     except Exception:
#         pass
#     return "unknown setup cfg app"


def _from_cwd() -> str | None:
    """
    Detect app name from project directory
    """
    try:
        return Path.cwd().name.lower()
    except Exception:
        return "unknown cwd app"


def detect_app_name(default: str = "unknown-python-app") -> str:
    """
    Final detection order
    """
    return (
        # _from_entrypoint()
        # or _from_pyproject()
        # or _from_setup_cfg()
        # or _from_cwd()
        _from_cwd()
        or default
    )
