"""
Service name auto-detection for Sify OpenTelemetry SDK.

Detection order (highest → lowest priority):
1. Environment variables (infra-level, not user code)
2. Framework metadata (Flask / FastAPI, if provided)
3. Python runtime module/package
4. Safe fallback

This guarantees:
- No filename-based collisions (app.py problem)
- Stable identity across environments
- Zero required user configuration
"""

import os
import __main__
import logging

logger = logging.getLogger(__name__)


def detect_service_name(framework_app=None) -> str:
    """
    Detect application service name without explicit user input.

    :param framework_app: Optional framework app instance (e.g., Flask app)
    :return: service.name string
    """

    # ------------------------------------------------------------------
    # 1️⃣ Environment variables (BEST & industry standard)
    # ------------------------------------------------------------------
    service_name = (
        os.getenv("OTEL_SERVICE_NAME")
        or os.getenv("SERVICE_NAME")
        or os.getenv("APP_NAME")
    )
    if service_name:
        logger.debug("Service name detected from environment: %s", service_name)
        return service_name

    # ------------------------------------------------------------------
    # 2️⃣ Framework-level detection (Flask, FastAPI, etc.)
    # ------------------------------------------------------------------
    if framework_app is not None:
        import_name = getattr(framework_app, "import_name", None)
        if import_name and import_name != "__main__":
            logger.debug("Service name detected from framework: %s", import_name)
            return import_name

    # ------------------------------------------------------------------
    # 3️⃣ Python runtime module/package
    # ------------------------------------------------------------------
    package = getattr(__main__, "__package__", None)
    if package:
        logger.debug("Service name detected from __main__.__package__: %s", package)
        return package

    module = getattr(__main__, "__name__", None)
    if module and module != "__main__":
        logger.debug("Service name detected from __main__.__name__: %s", module)
        return module

    # ------------------------------------------------------------------
    # 4️⃣ Absolute fallback (never empty)
    # ------------------------------------------------------------------
    logger.warning(
        "Unable to auto-detect service.name. "
        "Defaulting to 'unknown-service'. "
        "Consider setting OTEL_SERVICE_NAME."
    )
    return "unknown-service"
