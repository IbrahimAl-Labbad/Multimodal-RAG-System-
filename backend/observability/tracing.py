from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def setup_tracing(otlp_endpoint: str) -> None:
    """Configure OpenTelemetry tracing with OTLP export."""
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()


def get_tracer(name: str = "multimodal-rag") -> trace.Tracer:
    return trace.get_tracer(name)
