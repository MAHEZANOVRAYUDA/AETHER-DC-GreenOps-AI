"""Redpanda / Kafka Producer Interface for AETHER-DC.

Publishes telemetry events and scenario injection batches to topic `dc.telemetry.raw`.
Gracefully falls back when Kafka broker is unreachable.
"""

import json
from typing import Any, Dict, Optional
import os


class KafkaTelemetryProducer:
    """Kafka/Redpanda Producer wrapper with fallback handling."""

    def __init__(self, bootstrap_servers: Optional[str] = None):
        self.bootstrap_servers = bootstrap_servers or os.getenv("REDPANDA_BROKERS", "localhost:9092")
        self.producer = None
        self._init_producer()

    def _init_producer(self):
        """Attempts to initialize confluent_kafka Producer."""
        try:
            from confluent_kafka import Producer  # type: ignore
            conf = {
                "bootstrap.servers": self.bootstrap_servers,
                "client.id": "aether-telemetry-producer",
                "queue.buffering.max.messages": 100000,
                "socket.timeout.ms": 1000,
            }
            self.producer = Producer(conf)
        except Exception:
            self.producer = None

    def publish_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """Publishes a single event JSON payload to Kafka topic."""
        if not self.producer:
            return False
        try:
            payload_bytes = json.dumps(event, default=str).encode("utf-8")
            self.producer.produce(topic, value=payload_bytes)
            self.producer.poll(0)
            return True
        except Exception:
            return False

    def flush(self, timeout_sec: float = 0.5):
        """Flushes remaining messages in buffer."""
        if self.producer:
            try:
                self.producer.flush(timeout_sec)
            except Exception:
                pass
