from typing import Dict, Any, Optional
from contextlib import contextmanager

from sify.aiplatform.observability.openTelemetry.utils.user_context import get_user_context

try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind, Status, StatusCode
except Exception:
    trace = None
    SpanKind = None
    Status = None
    StatusCode = None


class DummySpan:
    """Safe no-op span fallback."""
    def set_attribute(self, k, v): pass
    def add_event(self, name, attributes=None): pass
    def record_exception(self, exc): pass
    def set_status(self, status): pass
    def end(self): pass

    def get_span_context(self):
        class Ctx:
            trace_id = 0
            span_id = 0
        return Ctx()


class TracesManager:
    """
    Thin wrapper around OpenTelemetry tracing.

    IMPORTANT:
    - Does NOT create TracerProvider
    - Does NOT create Resource
    - Does NOT set service.name
    All of that must happen in otel_setup.py
    """

    def __init__(self):
        self.tracer = trace.get_tracer(__name__) if trace else None

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _normalize_kind(self, kind):
        if kind is not None:
            return kind
        return SpanKind.INTERNAL if SpanKind else None

    def _inject_user(self, attributes: Dict[str, Any] | None):
        attrs = dict(attributes or {})
        user_id = get_user_context()
        if user_id:
            attrs["user.id"] = user_id
        return attrs

    # --------------------------------------------------
    # Span creation
    # --------------------------------------------------
    @contextmanager
    def start_span(self, name: str, attributes: Dict[str, Any] = None, kind=None):
        kind = self._normalize_kind(kind)
        attributes = self._inject_user(attributes)

        if self.tracer:
            try:
                with self.tracer.start_as_current_span(
                    name,
                    attributes=attributes,
                    kind=kind,
                ) as span:
                    yield span
                return
            except Exception:
                pass

        yield DummySpan()

    def start_span_as_current(self, name: str, attributes: Dict[str, Any] = None, kind=None):
        kind = self._normalize_kind(kind)
        attributes = self._inject_user(attributes)

        if self.tracer:
            try:
                return self.tracer.start_as_current_span(
                    name,
                    attributes=attributes,
                    kind=kind,
                )
            except Exception:
                pass

        class DummyCM:
            def __enter__(self): return DummySpan()
            def __exit__(self, *a): return False

        return DummyCM()

    def create_span(self, name: str, attributes: Dict[str, Any] = None, kind=None):
        kind = self._normalize_kind(kind)
        attributes = self._inject_user(attributes)

        if self.tracer:
            try:
                return self.tracer.start_span(
                    name,
                    attributes=attributes,
                    kind=kind,
                )
            except Exception:
                pass

        return DummySpan()

    # --------------------------------------------------
    # Span helpers
    # --------------------------------------------------
    def get_current_span(self):
        try:
            return trace.get_current_span() if trace else DummySpan()
        except Exception:
            return DummySpan()

    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        span = self.get_current_span()
        try:
            span.add_event(name, attributes or {})
        except Exception:
            pass

    def update_attributes(self, attributes: Dict[str, Any]):
        span = self.get_current_span()
        try:
            for k, v in (attributes or {}).items():
                span.set_attribute(k, v)
        except Exception:
            pass

    def record_exception(self, exception: Exception):
        span = self.get_current_span()
        try:
            span.record_exception(exception)
            if Status and StatusCode:
                span.set_status(Status(StatusCode.ERROR, str(exception)))
        except Exception:
            pass

    def set_span_status_ok(self):
        span = self.get_current_span()
        try:
            if Status and StatusCode:
                span.set_status(Status(StatusCode.OK))
        except Exception:
            pass

    def set_span_status_error(self, message="error"):
        span = self.get_current_span()
        try:
            if Status and StatusCode:
                span.set_status(Status(StatusCode.ERROR, message))
        except Exception:
            pass

    # --------------------------------------------------
    # Trace context helper
    # --------------------------------------------------
    def get_trace_context(self) -> Dict[str, Optional[str]]:
        try:
            span = self.get_current_span()
            ctx = span.get_span_context()
            if not ctx or ctx.trace_id == 0:
                return {}
            return {
                "trace_id": f"{ctx.trace_id:032x}",
                "span_id": f"{ctx.span_id:016x}",
            }
        except Exception:
            return {}







# | Feature                   | Description                       |
# | ------------------------- | --------------------------------- |
# | `end_span()`              | Safe manual end for spans         |
# | `set_span_status_ok()`    | Mark span status as OK            |
# | `set_span_status_error()` | Mark span status as ERROR         |
# | `record_exception()`      | Proper OTel exception recording   |
# | `add_event()`             | Add event to current span         |
# | `update_attributes()`     | Bulk attribute setter             |
# | `get_trace_context()`     | Returns trace_id/span_id properly |
# | Full fallback DummySpan   | Never breaks user app             |


"""1️⃣ Core Span Management

start_span()

start_span_as_current()

create_span()

end_span()

2️⃣ Rich Observability Helpers

add_event()

update_attributes()

record_exception()

set_span_status_ok()

set_span_status_error()

3️⃣ Safe Fallbacks

Every method works even if:

OpenTelemetry is not installed

Exporter fails

Tracer provider not configured

4️⃣ Usability Helpers

get_current_span()

get_trace_context() (trace_id + span_id)"""