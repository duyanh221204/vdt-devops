import logging
import time

from opentelemetry import trace
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger()

REQUEST_COUNTER = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


def current_trace_exemplar():
    span = trace.get_current_span()
    context = span.get_span_context()

    if context.is_valid and context.trace_flags.sampled:
        return {'trace_id': f'{context.trace_id:032x}'}
    return None


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in {'/metrics', '/favicon.ico'}:
            return await call_next(request)

        route = request.scope.get('route')
        endpoint = route.path if route else request.url.path

        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            duration = time.perf_counter() - start
            exemplar = current_trace_exemplar()

            REQUEST_COUNTER.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc(1, exemplar)

            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration, exemplar)

            logger.info(
                "client=%s method=%s endpoint=%s status=%d duration_ms=%.2f",
                request.client.host if request.client else "-",
                request.method,
                endpoint,
                status_code,
                duration * 1000
            )

        return response
