
import logging
from typing import Dict, Any, Callable, Optional
# from telemetry.utils.user_context import get_user_context
# from sify.aiplatform.observability.openTelemetry.utils.user_context import get_user_context
from sify.aiplatform.observability.openTelemetry.config import TelemetryConfig
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.WARNING)

try:
    from opentelemetry import metrics as ot_metrics
except Exception:
    ot_metrics = None


# ---------------- NO-OP FALLBACK TYPES -------------------

class _NoopCounter:
    def add(self, value: float = 1.0, attributes: Dict[str, Any] = None):
        return None

class _NoopUpDownCounter:
    def add(self, value: float = 1.0, attributes: Dict[str, Any] = None):
        return None

class _NoopHistogram:
    def record(self, value: float, attributes: Dict[str, Any] = None):
        return None

class _NoopObservable:
    def __init__(self):
        self.callback = None


# ---------------------------------------------------------
#                METRIC MANAGER (FINAL VERSION)
# ---------------------------------------------------------

class MetricsManager:
    """
    Production-grade metrics manager supporting:
      ✔ Counter
      ✔ UpDownCounter
      ✔ Histogram
      ✔ Observable Gauge
      ✔ Observable Counter
      ✔ Observable UpDownCounter
    With auto-noop fallback & safe instrumentation recreation.
    """

    def __init__(self, meter_provider=None):
        try:
            self._config = TelemetryConfig()
            self.otel_service_name = self._config.otel_service_name
            self.service_name = self._config.service_name
        except Exception:
            self.otel_service_name = None
            self.service_name = None
        self.meter_provider = meter_provider
        self._instruments: Dict[str, Any] = {}
        self._observable_callbacks: Dict[str, Any] = {}

    # ------------------- METER HELPERS ---------------------

    def get_meter(self, name: str):
        """Return a meter from provider or fallback to ot_metrics."""
        try:
            if self.meter_provider:
                return self.meter_provider.get_meter(name)
            if ot_metrics:
                return ot_metrics.get_meter(name)
        except Exception as e:
            logger.debug("get_meter failed for %s: %s", name, e, exc_info=True)
        return None

    def _is_noop(self, inst: Any) -> bool:
        return isinstance(inst, (_NoopCounter, _NoopUpDownCounter, _NoopHistogram, _NoopObservable))

    # ------------------- GENERIC CREATION HELPER ---------------------

    def _get_or_create(self, name: str, inst_type: str,
                       description: Optional[str],
                       unit: Optional[str]):

        existing = self._instruments.get(name)
        # user_id = get_user_context()
        if existing and not self._is_noop(existing):
            return existing

        if existing and self._is_noop(existing):
            logger.debug(f"Attempting to replace noop instrument '{name}'.")

        meter = self.get_meter(name)

        try:
            if meter:
                kwargs = {}
                if description: kwargs["description"] = description
                if unit: kwargs["unit"] = unit

                # mapping to real otel API
                creator_map = {
                    "counter": meter.create_counter,
                    "updown": meter.create_up_down_counter,
                    "histogram": meter.create_histogram,
                }

                if inst_type in creator_map:
                    inst = creator_map[inst_type](name, **kwargs)
                    self._instruments[name] = inst
                    # logger.info("Created real %s '%s'", inst_type, name)
                    return inst

        except Exception as e:
            logger.debug(f"Failed to create {inst_type} '{name}': {e}", exc_info=True)

        # fallback to noop
        noop_map = {
            "counter": _NoopCounter(),
            "updown": _NoopUpDownCounter(),
            "histogram": _NoopHistogram(),
        }
        noop = noop_map[inst_type]
        self._instruments[name] = noop

        logger.warning(
            f"Using NOOP {inst_type} for '{name}'. "
            f"Install OpenTelemetry or configure a meter provider."
        )
        return noop

    # ------------------- COUNTERS ---------------------

    def increment_counter(self, name: str, value: float = 1.0, attributes: Dict[str, Any] = None):
        inst = self._get_or_create(name, "counter", description="", unit="")
            
        try:
            attrs = dict(attributes or {})

            # always attach service identity
            

            

            # attach user only if present
            # user_id = get_user_context()
            # if user_id:
            #     attrs.setdefault("user.id", user_id)

            inst.add(value, attrs)
        except Exception:
            logger.debug("Error incrementing counter '%s'", name, exc_info=True)

    def create_counter(self, name: str, description=None, unit=None):
        return self._get_or_create(name, "counter", description, unit)

    # ------------------- UP-DOWN COUNTERS ---------------------

    def add_updown(self, name: str, value: float = 1.0, attributes: Dict[str, Any] = None):
        inst = self._get_or_create(name, "updown", description="", unit="")
        try:
            attrs = dict(attributes or {})
            # user_id = get_user_context()
            # if user_id:
            #     attrs.setdefault("user.id", user_id)

            inst.add(value, attrs)
        except Exception:
            logger.debug("Error updating updown counter '%s'", name, exc_info=True)

    def create_updown(self, name: str, description=None, unit=None):
        return self._get_or_create(name, "updown", description, unit)

    # ------------------- HISTOGRAM ----------------------

    def record_histogram(self, name: str, value: float, attributes: Dict[str, Any] = None, unit=None):
        inst = self._get_or_create(name, "histogram", description="", unit=unit)
        try:
            attrs = dict(attributes or {})

            

            

            # user_id = get_user_context()
            # if user_id:
            #     attrs.setdefault("user.id", user_id)

            inst.record(value, attrs)
        except Exception:
            logger.debug("Error recording histogram '%s'", name, exc_info=True)

    def create_histogram(self, name: str, description=None, unit=None):
        return self._get_or_create(name, "histogram", description, unit)

    # ------------------- OBSERVABLE METRICS ---------------------

    def create_observable_gauge(self, name: str, callback: Callable):
        return self._create_observable(name, callback, inst_type="gauge")

    def create_observable_counter(self, name: str, callback: Callable):
        return self._create_observable(name, callback, inst_type="counter")

    def create_observable_updown(self, name: str, callback: Callable):
        return self._create_observable(name, callback, inst_type="updown")

    def _create_observable(self, name: str, callback: Callable, inst_type: str):
        meter = self.get_meter(name)

        try:
            if meter:
                if inst_type == "gauge":
                    observable = meter.create_observable_gauge(name, callbacks=[callback])
                elif inst_type == "counter":
                    observable = meter.create_observable_counter(name, callbacks=[callback])
                else:
                    observable = meter.create_observable_up_down_counter(name, callbacks=[callback])

                self._instruments[name] = observable
                self._observable_callbacks[name] = callback
                # logger.info("Created observable %s '%s'", inst_type, name)
                return observable

        except Exception as e:
            logger.debug(f"Failed to create observable {inst_type} '{name}': {e}", exc_info=True)

        # fallback noop
        noop = _NoopObservable()
        noop.callback = callback
        self._instruments[name] = noop
        return noop

    # --------------------- FLUSH ------------------------

    def flush(self):
        try:
            if self.meter_provider and hasattr(self.meter_provider, "shutdown"):
                self.meter_provider.shutdown()
        except Exception:
            logger.debug("Error flushing meter provider", exc_info=True)











# import logging
# from typing import Optional, List, Dict, Any
# from .config import TelemetryConfig
# from .core.otel_setup import setup_otel
# from .core.traces import TracesManager
# from .core.metrics import MetricsManager
# from .core.logs import LogsManager
# from .auto.library_instrumentor import LibraryInstrumentor
# from .auto.framework_instrumentor import FrameworkInstrumentor
# from .auto.database_instrumentor import DatabaseInstrumentor
# from .auto.sify_sdk_instrumentor import SifySDKInstrumentor
# from .auto.function_instrumentor import FunctionInstrumentor
# from .auto.class_instrumentor import ClassInstrumentor
# from .auto.decorators import create_decorators
# from opentelemetry.sdk.resources import Resource
# from sify.aiplatform.observability.openTelemetry.utils.service_name import (
#     detect_service_name,
# )
# logger = logging.getLogger(__name__)


# class TelemetryCollector:
#     def __init__(self, config: Optional[TelemetryConfig] = None):
#         self.config = config or TelemetryConfig()

#         service_name = self.config.service_name or detect_service_name(
#             framework_app=self.config.framework_app
#         )
#         self.service_name = service_name

#         resource = Resource.create({
#             "service.name": service_name,
#             "telemetry.sdk.name": "sify-otel-sdk",
#         })

#         providers = setup_otel(self.config, resource)
#         self.trace_rules = self.config.trace_rules
#         self.enable_traces = self.config.enable_traces

#         self.tracer_provider = providers.get("tracer_provider")
#         self.meter_provider = providers.get("meter_provider")
#         self.logger_provider = providers.get("logger_provider")

#         # Managers
#         self._traces = TracesManager(self.tracer_provider)
#         self._metrics = MetricsManager(self.meter_provider)
#         self._logs = LogsManager(self.config, logger_provider=self.logger_provider)

#         # Instrumentors
#         self._lib_instrumentor = LibraryInstrumentor()
#         self._fw_instrumentor = FrameworkInstrumentor(self)
#         self._db_instrumentor = DatabaseInstrumentor()
#         self._sify_instrumentor = SifySDKInstrumentor()
#         self._func_instrumentor = FunctionInstrumentor()
#         self._class_instrumentor = ClassInstrumentor()

#         self._decorators = create_decorators(self)
#         self._instrumented_libraries = set()

#         # --------------------------------------------------------
#         # 1️⃣ Auto-instrument Framework (Flask / Django / FastAPI)
#         # --------------------------------------------------------
#         if self.config.auto_instrument and self.config.instrument_frameworks:
#             logger.debug("Auto-instrumenting framework...")
#             try:
#                 if self.config.framework_app:
#                     self._fw_instrumentor.instrument_app(self.config.framework_app)
#             except Exception:
#                 logger.debug("Framework auto-instrumentation failed", exc_info=True)

#         # --------------------------------------------------------
#         # 2️⃣ Auto-instrument Libraries (requests, httpx, urllib3)
#         # --------------------------------------------------------

#         if (
#             self.config.auto_instrument
#             and self.config.instrument_libraries_enabled
#             and self.config.instrument_libraries
#         ):
#             logger.debug(f"Auto-instrumenting libraries: {self.config.instrument_libraries}")
#             try:
#                 results = self._lib_instrumentor.instrument(self.config.instrument_libraries)
#                 self._instrumented_libraries.update(self.config.instrument_libraries)
#             except Exception:
#                 logger.debug("Library auto-instrumentation failed", exc_info=True)


#         # --------------------------------------------------------
#         # 3️⃣ Auto-instrument Databases
#         # --------------------------------------------------------
#         if (
#             self.config.auto_instrument
#             and self.config.instrument_databases_enabled
#             and self.config.instrument_databases
#         ):
#             logger.debug(f"Auto-instrumenting DB clients: {self.config.instrument_databases}")
#             try:
#                 self._db_instrumentor.instrument(self.config.instrument_databases)
#             except Exception:
#                 logger.debug("Database instrumentation failed", exc_info=True)

#         if self.config.enable_logs and self.config.auto_instrument:
#             try:
#                 from opentelemetry.instrumentation.logging import LoggingInstrumentor
#                 LoggingInstrumentor().instrument(
#                     set_logging_format=True,
#                     excluded_loggers=[
#                         "werkzeug",
#                         "werkzeug._internal",
#                         "werkzeug.serving",
#                         "werkzeug.developmentserver",
#                         "werkzeug.wsgi",
#                         "gunicorn.access",
#                         "uvicorn.access",
#                     ],
#                 )
#             except Exception:
#                 logger.debug("Python logging auto-instrumentation failed", exc_info=True)

#         #  THEN disable framework logs (user intent)
#         if self.config.disable_framework_logs:
#             for name in self.config.framework_loggers_to_disable:
#                 logging.getLogger(name).disabled = True

#     # --------------------------------------------------------
#     #  NEW METHOD: EXPORT NORMAL PYTHON LOGS → OTEL → LOKI
#     # --------------------------------------------------------
#     def _enable_python_auto_log_capture(self):
#         import logging
#         from opentelemetry.trace import get_current_span

#         provider = self._logs.otel_logger_provider
#         otel_logger = provider.get_logger(self.service_name)

#         class OTelLoggingHandler(logging.Handler):
#             def emit(self, record):
#                 try:
#                     span_ctx = get_current_span().get_span_context()
#                     trace_attrs = {}

#                     if span_ctx and span_ctx.trace_id != 0:
#                         trace_attrs = {
#                             "trace_id": f"{span_ctx.trace_id:032x}",
#                             "span_id": f"{span_ctx.span_id:016x}",
#                         }

#                     otel_logger.emit(
#                         body=record.getMessage(),
#                         severity_text=record.levelname,
#                         severity_number=record.levelno,
#                         attributes={
#                             "logger.name": record.name,
#                             "file": record.filename,
#                             "line": record.lineno,
#                             **trace_attrs,
#                         },
#                     )
#                 except Exception:
#                     pass

#         root = logging.getLogger()
#         root.addHandler(OTelLoggingHandler())
#         root.setLevel(logging.INFO)

#     # ---------------- PROPERTIES ----------------
#     @property
#     def traces(self):
#         return self._traces

#     @property
#     def metrics(self):
#         return self._metrics

#     @property
#     def logs(self):
#         return self._logs

#     @property
#     def decorators(self):
#         return self._decorators

#     # ---------------- PUBLIC API ----------------
#     def enable_auto_instrumentation(self, libraries: Optional[List[str]] = None):
#         libs = libraries or self.config.instrument_libraries or []
#         self._lib_instrumentor.instrument(libs)
#         self._instrumented_libraries.update(libs)
#         return True

#     def disable_auto_instrumentation(self):
#         for lib in list(self._instrumented_libraries):
#             try:
#                 self._lib_instrumentor.uninstrument(lib)
#             except Exception:
#                 pass
#         self._instrumented_libraries.clear()
#         return True

#     def instrument_database(self, db_libs: List[str]):
#         return self._db_instrumentor.instrument(db_libs)

#     def instrument_library(self, library_name: str):
#         self._lib_instrumentor.instrument([library_name])
#         self._instrumented_libraries.add(library_name)
#         return True

#     def instrument_app(self, app: Any, framework: str = None):
#         return self._fw_instrumentor.instrument_app(app, framework)

#     def instrument_class(self, cls, prefix=None):
#         return self._class_instrumentor.instrument(cls, self, prefix)
    

#     def instrument_function(self, func, name: str = None):

#         print(" [Collector.instrument_function] Called", flush=True)
#         print(f"    ➤ func original: {func} (id={id(func)})", flush=True)
#         print(f"    ➤ func name: {func.__name__}", flush=True)

#         # Avoid double wrapping
#         if getattr(func, "__wrapped_by_sdk__", False):
#             print("     Function already wrapped, returning existing wrapper", flush=True)
#             return func

#         # Ask FunctionInstrumentor to wrap the function
#         wrapped = self._func_instrumentor.instrument(func, name,  telemetry=self)
#         print(f"    ✔ Wrapper created: {wrapped} (id={id(wrapped)})", flush=True)
#         print(f"    ✔ Wrapper __name__ = {wrapped.__name__}", flush=True)
#         wrapped.__wrapped_by_sdk__ = True

#         print(f"     Attached TelemetryCollector to wrapper _telemetry={wrapped._telemetry}", flush=True)

#         # EXTRA DEBUG - Check mapping
#         try:
#             instrumentor_map = self._func_instrumentor._wrapped
#             if func in instrumentor_map:
#                 print(f"    Mapping found: {func} → {instrumentor_map[func]}", flush=True)
#             else:
#                 print("     Mapping NOT found inside FunctionInstrumentor!", flush=True)
#         except Exception as e:
#             print(f"     Failed to inspect FunctionInstrumentor mapping: {e}", flush=True)

#         print(" [Collector.instrument_function] DONE\n", flush=True)

#         return wrapped



#     # ---------------- CONTEXT ----------------
#     def inject_context(self, carrier: Dict[str, str], context=None):
#         try:
#             from .utils.context import inject
#             inject(carrier, context)
#         except Exception:
#             pass
#         return carrier

#     def extract_context(self, carrier: Dict[str, str]):
#         try:
#             from .utils.context import extract
#             return extract(carrier)
#         except Exception:
#             return None

#     # ---------------- LIFECYCLE ----------------
#     def flush(self, timeout_ms: int = 30000) -> bool:
#         try:
#             if hasattr(self.tracer_provider, "force_flush"):
#                 self.tracer_provider.force_flush(timeout_ms / 1000.0)
#                 return True
#         except Exception:
#             pass
#         return False

#     def shutdown(self, timeout_ms: int = 30000) -> bool:
#         try:
#             if hasattr(self.tracer_provider, "shutdown"):
#                 self.tracer_provider.shutdown(timeout_ms / 1000.0)
#         except Exception:
#             pass
#         return True
    # def is_enabled(self) -> bool:
    #     return bool(
    #         self.config.enable_traces
    #         or self.config.enable_metrics
    #         or self.config.enable_logs
    #     )
