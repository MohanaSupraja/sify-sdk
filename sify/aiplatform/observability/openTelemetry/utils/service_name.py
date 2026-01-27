import os
import sys
from pathlib import Path
 
INVALID = {
    "uvicorn",
    "gunicorn",
    "python",
    "__main__",
}
 
def detect_app_name() -> str:
    if os.getenv("SIFY_APP_NAME"):
        return os.getenv("SIFY_APP_NAME")
 
    # 1️⃣ uvicorn module:app (Windows-safe)
    for arg in sys.argv:
        # must look like module:attr (not a path like C:\...)
        if ":" in arg and "\\" not in arg and "/" not in arg:
            module = arg.split(":", 1)[0]
            name = module.split(".")[-1]
            if name and name not in INVALID:
                return name
 
    try:
        entry = Path(sys.argv[0]).stem
        if entry and entry not in INVALID:
            return entry
    except Exception:
        pass
 
    return "unknown_app"

# import os
# import sys
# from pathlib import Path

# INVALID_ENTRY_NAMES = {
#     "python",
#     "ipython",
#     "gunicorn",
#     "pytest",
#     "uvicorn"
# }


# # def from_otel_env(default: str = "sify-client-app") -> str:
# #     """Read OpenTelemetry standard environment variable"""
# #     return os.getenv("OTEL_SERVICE_NAME", default)


# # def from_entrypoint() -> str | None:
# #     """Detect service name from entry-point script"""
# #     try:
# #         entry = Path(sys.argv[0]).stem.lower()
# #         if entry and entry not in INVALID_ENTRY_NAMES:
# #             return entry
# #     except Exception:
# #         pass
# #     return None


# # def from_asgi_app():
# #     for module in sys.modules.values():
# #         if getattr(module, "__file__", None):
# #             if module.__file__.endswith(".py"):
# #                 return Path(module.__file__).stem.lower()
# #     return None

# def path():
#     exe_name = os.path.basename(sys.executable)
#     if exe_name:
#         return exe_name 
#     return None

# # def from_cwd() -> str | None:
# #     """Detect service name from current working directory"""
# #     try:
# #         return Path.cwd().name.lower()
# #     except Exception:
# #         pass
# #     return None


# def detect_service_name(default: str = "unknown-python-app") -> str:
#     """
#     Final detection order (short-circuiting):
#     1. OTEL_SERVICE_NAME
#     2. Entrypoint
#     3. CWD
#     4. Default
#     """
#     return (
#         # from_entrypoint()
#         # from_asgi_app()
#         # from_cwd()
#         path()
#         or default
#     )
