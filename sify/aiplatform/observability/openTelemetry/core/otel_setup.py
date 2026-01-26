# import logging
# from typing import Dict, Any
# from opentelemetry.sdk.resources import Resource
# from opentelemetry import trace, metrics
# from opentelemetry._logs import set_logger_provider

# from opentelemetry.sdk.trace import TracerProvider, SpanLimits
# from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.sdk.metrics.export import (
#     PeriodicExportingMetricReader,
#     ConsoleMetricExporter,
# )

# from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
# from opentelemetry.sdk._logs.export import (
#     BatchLogRecordProcessor,
#     ConsoleLogExporter,
# )

# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
# from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

# from ..config import TelemetryConfig

# logger = logging.getLogger(__name__)


# def setup_otel(
#     config: TelemetryConfig,
#     resource: Resource,
# ) -> Dict[str, Any]:
#     """
#     Fully working OpenTelemetry setup:
#     - Traces → OTLP → Collector
#     - Metrics → OTLP → Collector
#     - Logs   → OTLP → Collector → Loki
#     """

#     providers = {
#         "tracer_provider": None,
#         "meter_provider": None,
#         "logger_provider": None,
#     }

#     use_http = (config.protocol or "").startswith("http")

#     # =========================================================
#     # TRACES
#     # =========================================================
#     if config.enable_traces:
#         try:
#             tracer_provider = TracerProvider(
#                 resource=resource,
#                 span_limits=SpanLimits(
#                     max_attributes=config.max_span_attributes,
#                     max_events=256,
#                     max_links=128,
#                 ),
#             )

#             span_exporter = OTLPSpanExporter(
#                 endpoint=f"{config.collector_endpoint}/v1/traces",
#                 headers=config.headers or {},
#             ) if config.collector_endpoint else ConsoleSpanExporter()

#             tracer_provider.add_span_processor(
#                 BatchSpanProcessor(
#                     span_exporter,
#                     schedule_delay_millis=config.export_interval_ms,
#                     max_export_batch_size=config.max_export_batch_size,
#                     max_queue_size=config.max_queue_size,
#                 )
#             )

#             trace.set_tracer_provider(tracer_provider)
#             providers["tracer_provider"] = tracer_provider

#         except Exception:
#             logger.exception("Trace setup failed")

#     # =========================================================
#     # METRICS
#     # =========================================================
#     if config.enable_metrics:
#         try:
#             metric_exporter = OTLPMetricExporter(
#                 endpoint=f"{config.collector_endpoint}/v1/metrics",
#                 headers=config.headers or {},
#             ) if config.collector_endpoint else ConsoleMetricExporter()

#             meter_provider = MeterProvider(
#                 resource=resource,
#                 metric_readers=[
#                     PeriodicExportingMetricReader(
#                         exporter=metric_exporter,
#                         export_interval_millis=config.export_interval_ms,
#                     )
#                 ],
#             )

#             metrics.set_meter_provider(meter_provider)
#             providers["meter_provider"] = meter_provider

#         except Exception:
#             logger.exception("Metric setup failed")

#     # =========================================================
#     # LOGS
#     # =========================================================
#     if config.enable_logs:
#         try:
#             logger_provider = LoggerProvider(resource=resource)

#             log_exporter = OTLPLogExporter(
#                 endpoint=f"{config.collector_endpoint}/v1/logs",
#                 headers=config.headers or {},
#             ) if config.collector_endpoint else ConsoleLogExporter()

#             logger_provider.add_log_record_processor(
#                 BatchLogRecordProcessor(log_exporter)
#             )

#             set_logger_provider(logger_provider)

#             handler = LoggingHandler(
#                 level=logging.NOTSET,
#                 logger_provider=logger_provider,
#             )

#             root_logger = logging.getLogger()
#             root_logger.addHandler(handler)
#             root_logger.setLevel(logging.INFO)

#             providers["logger_provider"] = logger_provider

#         except Exception:
#             logger.exception("Log setup failed")

#     return providers



import logging
from typing import Dict, Any
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace, metrics
from opentelemetry._logs import set_logger_provider

from opentelemetry.sdk.trace import TracerProvider, SpanLimits
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    ConsoleLogExporter,
)

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from ..config import TelemetryConfig

logger = logging.getLogger(__name__)


def setup_otel(config: TelemetryConfig) -> Dict[str, Any]:
    """
    Fully working OpenTelemetry setup:
    - Traces → OTLP → Collector
    - Metrics → OTLP → Collector
    - Logs   → OTLP → Collector → Loki
    """

    providers = {
        "tracer_provider": None,
        "meter_provider": None,
        "logger_provider": None,
    }

    # ---------------------------------------------------------
    # Resource (VERY IMPORTANT FOR LOKI LABELS)
    # ---------------------------------------------------------
    resource = Resource.create({
        "service.clientname": config.service_name,
        # "otel.service.name": config.otel_service_name,
        "service.namespace": "sify",    
        **(config.resource_attributes or {}),
    })

    use_http = (config.protocol or "").startswith("http")

    # =========================================================
    # TRACES
    # =========================================================
    if config.enable_traces:
        try:
            tracer_provider = TracerProvider(
                resource=resource,
                span_limits=SpanLimits(
                    max_attributes=config.max_span_attributes,
                    max_events=256,
                    max_links=128,
                ),
            )

            span_exporter = OTLPSpanExporter(
                endpoint=f"{config.collector_endpoint}/v1/traces",
                headers=config.headers or {},
            ) if config.collector_endpoint else ConsoleSpanExporter()

            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    span_exporter,
                    schedule_delay_millis=config.export_interval_ms,
                    max_export_batch_size=config.max_export_batch_size,
                    max_queue_size=config.max_queue_size,
                )
            )

            trace.set_tracer_provider(tracer_provider)
            providers["tracer_provider"] = tracer_provider

        except Exception as e:
            logger.exception("Trace setup failed")

    # =========================================================
    # METRICS
    # =========================================================
    if config.enable_metrics:
        try:
            metric_exporter = OTLPMetricExporter(
                endpoint=f"{config.collector_endpoint}/v1/metrics",
                headers=config.headers or {},
            ) if config.collector_endpoint else ConsoleMetricExporter()

            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[
                    PeriodicExportingMetricReader(
                        exporter=metric_exporter,
                        export_interval_millis=config.export_interval_ms,
                    )
                ],
            )

            metrics.set_meter_provider(meter_provider)
            providers["meter_provider"] = meter_provider

        except Exception as e:
            logger.exception("Metric setup failed")

    # =========================================================
    # LOGS THIS IS THE CRITICAL PART
    # =========================================================
    if config.enable_logs:
        try:
            logger_provider = LoggerProvider(resource=resource)

            log_exporter = OTLPLogExporter(
                endpoint=f"{config.collector_endpoint}/v1/logs",
                headers=config.headers or {},
            ) if config.collector_endpoint else ConsoleLogExporter()

            logger_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )

            #  REQUIRED: register provider globally
            set_logger_provider(logger_provider)

            # REQUIRED: attach handler to Python logging
            handler = LoggingHandler(
                level=logging.NOTSET,
                logger_provider=logger_provider,
            )

            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.INFO)

            providers["logger_provider"] = logger_provider

        except Exception as e:
            logger.exception("Log setup failed")

    return providers

f"""setup_otel() initializes OpenTelemetry Tracing + Metrics for your SDK:

Creates resource attributes like service.name

Creates and configures the TracerProvider

Creates and configures the MeterProvider

Selects OTLP HTTP or OTLP gRPC exporters based on config

Provides console fallback if OTEL exporter fails

Leaves logging to LogsManager (not handled here)

Returns a dict of initialized providers


providers contain the exporters and processors that actually send telemetry to endpoints.

Think of them as:

Provider = Manager
Processor = Worker
Exporter = Delivery System (HTTP → Collector → Jaeger/Prometheus/Loki)


| Provider           | What it manages                   | What gets exported            |
| ------------------ | --------------------------------- | ----------------------------- |
| **TracerProvider** | Span processors + span exporters  | → Jaeger, OTEL Collector      |
| **MeterProvider**  | Metric readers + metric exporters | → Prometheus / OTEL Collector |
| **LoggerProvider** | Log processors + log exporters    | → Loki / OTEL Collector       |


1️⃣ Provider created
tracer_provider = TracerProvider(resource=my_resource)

2️⃣ Exporter attached
span_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4318")
processor = BatchSpanProcessor(span_exporter)
tracer_provider.add_span_processor(processor)

3️⃣ Provider is set globally
trace.set_tracer_provider(tracer_provider)


Now any tracer from this point:

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("test"):
    ...


TracerProvider → BatchSpanProcessor → OTLP Exporter → Collector → Jaeger



"""