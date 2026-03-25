from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from config import get_settings

settings = get_settings()

_meter_provider: MeterProvider | None = None


def setup_metrics() -> None:
    global _meter_provider
    exporter = OTLPMetricExporter(
        endpoint=settings.otel_exporter_otlp_endpoint, insecure=True
    )
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15_000)
    _meter_provider = MeterProvider(metric_readers=[reader])
    metrics.set_meter_provider(_meter_provider)


def get_meter(name: str = "multimodal-rag") -> metrics.Meter:
    return metrics.get_meter(name)
