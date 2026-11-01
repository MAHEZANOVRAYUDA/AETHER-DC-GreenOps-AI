"""Prometheus Observability & Metrics Exporter for AETHER-DC.

Exposes industry-standard metrics on GET /metrics for:
- Telemetry event volume (valid vs DLQ)
- Facility PUE & rack inlet temperatures
- Real-time PSI drift scores
- Model inference latencies & rolling F1-scores
- Zero-downtime model hot-swap occurrences
"""

from typing import Optional
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)


class PrometheusMetricsManager:
    """Manages Prometheus telemetry collectors with in-process and external support."""

    _instance: Optional["PrometheusMetricsManager"] = None

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        # Use provided registry or default global registry
        self.registry = registry or REGISTRY

        # Counters
        self.telemetry_events_total = Counter(
            "aether_telemetry_events_total",
            "Total telemetry packets processed by Pydantic v2 gate",
            ["region", "server_type", "status"],
            registry=self.registry,
        )

        self.model_hotswap_total = Counter(
            "aether_model_hotswap_total",
            "Total zero-downtime model hot-swaps between Champion and Challenger",
            ["from_model", "to_model", "trigger_reason"],
            registry=self.registry,
        )

        # Gauges
        self.facility_pue_gauge = Gauge(
            "aether_facility_pue_gauge",
            "Current average Power Usage Effectiveness (PUE) per facility",
            ["region", "cooling_type"],
            registry=self.registry,
        )

        self.rack_inlet_temp_celsius = Gauge(
            "aether_rack_inlet_temp_celsius",
            "Actual rack inlet temperature in degrees Celsius",
            ["rack_id", "region"],
            registry=self.registry,
        )

        self.feature_drift_psi = Gauge(
            "aether_feature_drift_psi",
            "Current Population Stability Index (PSI) score per sensor feature",
            ["feature_name"],
            registry=self.registry,
        )

        self.model_rolling_f1_score = Gauge(
            "aether_model_rolling_f1_score",
            "Rolling window F1-score for anomaly classification",
            ["model_role", "model_name"],
            registry=self.registry,
        )

        # Histograms
        self.model_inference_latency_ms = Histogram(
            "aether_model_inference_latency_ms",
            "Model prediction inference latency in milliseconds",
            ["model_role"],
            buckets=[1.0, 2.5, 5.0, 10.0, 15.0, 25.0, 50.0],
            registry=self.registry,
        )

    @classmethod
    def get_instance(cls, registry: Optional[CollectorRegistry] = None) -> "PrometheusMetricsManager":
        """Singleton getter for PrometheusMetricsManager."""
        if cls._instance is None:
            cls._instance = PrometheusMetricsManager(registry)
        return cls._instance

    def record_ingest(self, region: str, server_type: str, is_valid: bool):
        """Records telemetry ingestion event."""
        status = "valid" if is_valid else "dlq"
        self.telemetry_events_total.labels(
            region=region,
            server_type=server_type,
            status=status,
        ).inc()

    def record_pue(self, region: str, cooling_type: str, pue_value: float):
        """Updates facility PUE gauge."""
        self.facility_pue_gauge.labels(region=region, cooling_type=cooling_type).set(pue_value)

    def record_inlet_temp(self, rack_id: str, region: str, temp_c: float):
        """Updates rack inlet temperature gauge."""
        self.rack_inlet_temp_celsius.labels(rack_id=rack_id, region=region).set(temp_c)

    def record_psi(self, feature_name: str, psi_score: float):
        """Updates PSI gauge for a specific feature."""
        self.feature_drift_psi.labels(feature_name=feature_name).set(psi_score)

    def record_f1(self, model_role: str, model_name: str, f1_score: float):
        """Updates rolling F1-score gauge."""
        self.model_rolling_f1_score.labels(model_role=model_role, model_name=model_name).set(f1_score)

    def record_hotswap(self, from_model: str, to_model: str, trigger_reason: str):
        """Increments model hot-swap counter."""
        self.model_hotswap_total.labels(
            from_model=from_model,
            to_model=to_model,
            trigger_reason=trigger_reason,
        ).inc()

    def export_metrics(self) -> bytes:
        """Serializes current metrics in Prometheus text format."""
        return generate_latest(self.registry)

