import time
from opentelemetry import metrics, trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import start_http_server
import psutil

# Initialize tracing
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
tracer = trace.get_tracer(__name__)

# Initialize metrics
reader = PrometheusMetricReader()
meter_provider = MeterProvider(resource=Resource.create(), metric_readers=[reader])
set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Start Prometheus metrics server
start_http_server(port=8001, addr="0.0.0.0")

def observe_resource_usage(_):
    """Callback function for resource monitoring"""
    try:
        return [
            Observation(psutil.cpu_percent(), {"resource": "cpu"}),
            Observation(psutil.virtual_memory().percent, {"resource": "memory"})
        ]
    except Exception as e:
        print(f"Resource monitoring error: {e}")
        return []

# Create and register metrics
meter.create_observable_gauge(
    name="system_resource_usage_percent",
    callbacks=[observe_resource_usage],
    description="System resource usage percentage",
    unit="%"
)

api_request_counter = meter.create_counter(
    "api_requests_total",
    description="Total number of API requests",
    unit="1"
)

api_latency_histogram = meter.create_histogram(
    "api_latency_seconds",
    description="API latency in seconds",
    unit="s"
)

embedding_latency_histogram = meter.create_histogram(
    "embedding_latency_seconds",
    description="Embedding generation latency in seconds",
    unit="s"
)