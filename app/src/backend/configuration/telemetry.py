import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from configuration.database import async_engine

load_dotenv()

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')


class TraceContextFilter(logging.Filter):
    def filter(self, record):
        span = trace.get_current_span()
        context = span.get_span_context()

        if context.is_valid:
            record.trace_id = f'{context.trace_id:032x}'
            record.span_id = f'{context.span_id:016x}'
        else:
            record.trace_id = '-'
            record.span_id = '-'
        
        return True


def configure_tracing():
    resource = Resource.create({'service.name': 'vdt-backend'})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(
        endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
        insecure=True
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    SQLAlchemyInstrumentor().instrument(engine=async_engine.sync_engine)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s '
        '[trace_id=%(trace_id)s span_id=%(span_id)s] '
        '%(name)s - %(message)s'
    )

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.addFilter(TraceContextFilter())
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            if not any(isinstance(f, TraceContextFilter) for f in handler.filters):
                handler.addFilter(TraceContextFilter())
            handler.setFormatter(formatter)

    root_logger.setLevel(logging.INFO)


def instrument_app(app: FastAPI):
    FastAPIInstrumentor().instrument_app(app)
