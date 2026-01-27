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
# service_name.py

import os
import sys
from pathlib import Path

INVALID_ENTRY_NAMES = {
    "python",
    "ipython",
    "gunicorn",
    "pytest",
}


# def from_otel_env(default: str = "sify-client-app") -> str:
#     """Read OpenTelemetry standard environment variable"""
#     return os.getenv("OTEL_SERVICE_NAME", default)


# def from_entrypoint() -> str | None:
#     """Detect service name from entry-point script"""
#     try:
#         entry = Path(sys.argv[0]).stem.lower()
#         if entry and entry not in INVALID_ENTRY_NAMES:
#             return entry
#     except Exception:
#         pass
#     return None


# def from_asgi_app():
#     for module in sys.modules.values():
#         if getattr(module, "__file__", None):
#             if module.__file__.endswith(".py"):
#                 return Path(module.__file__).stem.lower()
#     return None


def from_cwd() -> str | None:
    """Detect service name from current working directory"""
    try:
        return Path.cwd().name.lower()
    except Exception:
        pass
    return None


def detect_service_name(default: str = "unknown-python-app") -> str:
    """
    Final detection order (short-circuiting):
    1. OTEL_SERVICE_NAME
    2. Entrypoint
    3. CWD
    4. Default
    """
    return (
        # from_entrypoint()
        # from_asgi_app()
        from_cwd()
        or default
    )
