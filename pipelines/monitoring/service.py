import time
import logging
from typing import Dict, Any
from prometheus_client import start_http_server, Gauge, Counter

logger = logging.getLogger(__name__)

# Metrics
METRICS = {
    "search_latency": Gauge("search_latency_seconds", "Search request latency"),
    "search_errors": Counter("search_errors_total", "Total search errors"),
    "index_size": Gauge("index_size_items", "Number of items in the index"),
    "embedding_time": Gauge("embedding_time_seconds", "Time to generate embeddings")
}

class MonitoringService:
    def __init__(self):
        self.metrics_port = int(os.getenv("METRICS_PORT", 8000))
        start_http_server(self.metrics_port)
        logger.info(f"Started metrics server on port {self.metrics_port}")

    def record_search_metrics(self, latency: float, success: bool):
        METRICS["search_latency"].set(latency)
        if not success:
            METRICS["search_errors"].inc()

    def update_index_metrics(self, size: int):
        METRICS["index_size"].set(size)

    def record_embedding_time(self, duration: float):
        METRICS["embedding_time"].set(duration)

def get_monitoring_service():
    return MonitoringService()