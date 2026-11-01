"""Dual-Mode Streaming Broker & Interactive Scenario Injector for AETHER-DC.

Operates seamlessly across:
1. Docker Mode: Redpanda/Kafka Topic `dc.telemetry.raw`
2. Streamlit Cloud Fallback Mode: In-Memory Thread-Safe RingBuffer
Provides 4 live scenario injection triggers:
- Thermal Runaway
- Cooling Degradation
- Workload Surge
- Corrupted Sensor Burst (DLQ test)
"""

from collections import deque
from datetime import datetime, timezone
import random
from typing import Any, Dict, List, Optional
import uuid

from src.config.runtime import RuntimeMode, detect_runtime_mode
from src.ingestion.kafka_producer import KafkaTelemetryProducer
from src.lakehouse.medallion_engine import MedallionEngine


class DualModeStreamBroker:
    """Manages telemetry event streaming, ring-buffering, and live anomaly injection."""

    def __init__(self, medallion_engine: Optional[MedallionEngine] = None):
        self.runtime_mode = detect_runtime_mode()
        self.medallion = medallion_engine or MedallionEngine()
        self.ring_buffer = deque(maxlen=25000)
        self.kafka_producer = (
            KafkaTelemetryProducer() if self.runtime_mode == RuntimeMode.DOCKER_KAFKA else None
        )

    def publish_telemetry(self, raw_event: Dict[str, Any]) -> tuple[bool, str]:
        """Publishes event to Kafka (if active) and ingests into DuckDB Lakehouse & RingBuffer."""
        # 1. Attempt Kafka produce if in Docker mode
        if self.kafka_producer and self.runtime_mode == RuntimeMode.DOCKER_KAFKA:
            self.kafka_producer.publish_event("dc.telemetry.raw", raw_event)

        # 2. Append to in-memory ring-buffer
        self.ring_buffer.append(raw_event)

        # 3. Ingest into DuckDB Medallion Lakehouse (Bronze or DLQ)
        is_valid, msg = self.medallion.ingest_event(raw_event)
        return is_valid, msg

    def get_latest_stream(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent events from ring buffer or silver layer."""
        if self.ring_buffer:
            return list(self.ring_buffer)[-limit:]
        silver_df = self.medallion.get_silver_features(limit=limit)
        return silver_df.to_dict(orient="records")

    def inject_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Injects live real-time scenarios into the data pipeline."""
        now = datetime.now(timezone.utc)
        scenario_key = scenario_name.lower().replace(" ", "_")

        if scenario_key == "thermal_runaway":
            # Target APAC Liquid GPU rack
            rack_id = "RACK-APAC-01"
            event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": now.isoformat(),
                "rack_id": rack_id,
                "datacenter_region": "APAC",
                "server_type": "GPU",
                "cooling_type": "Liquid",
                "time_of_day": "Peak",
                "workload_intensity": 0.94,
                "cpu_utilization": 96.5,
                "memory_utilization": 92.0,
                "network_throughput_gbps": 380.0,
                "inlet_temperature_c": 46.8,  # Critical Thermal Runaway (>42C)
                "cooling_efficiency": 0.22,  # Severe cooling pump failure
                "power_consumption_kw": 105.4,
                "pue": 1.76,  # Severe PUE degradation
                "carbon_emission_kg": 18.2,
                "compute_cost_usd": 48.5,
                "energy_efficiency_class": "Low",
                "is_anomaly": 1,
                "injected_scenario": "thermal_runaway",
            }
            self.publish_telemetry(event)
            return {
                "status": "Injected Thermal Runaway",
                "rack_id": rack_id,
                "inlet_temp_c": 46.8,
                "pue": 1.76,
                "cooling_efficiency": 0.22,
                "action": "Triggered Critical Thermal Spike alert in Gold Incident Queue.",
            }

        elif scenario_key == "cooling_degradation":
            # Target ME Compute rack
            rack_id = "RACK-ME-02"
            event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": now.isoformat(),
                "rack_id": rack_id,
                "datacenter_region": "ME",
                "server_type": "Compute",
                "cooling_type": "Hybrid",
                "time_of_day": "Peak",
                "workload_intensity": 0.65,
                "cpu_utilization": 68.0,
                "memory_utilization": 62.0,
                "network_throughput_gbps": 140.0,
                "inlet_temperature_c": 39.5,
                "cooling_efficiency": 0.26,  # Gradual heat exchanger scale accumulation
                "power_consumption_kw": 44.0,
                "pue": 1.68,
                "carbon_emission_kg": 9.4,
                "compute_cost_usd": 24.0,
                "energy_efficiency_class": "Low",
                "is_anomaly": 1,
                "injected_scenario": "cooling_degradation",
            }
            self.publish_telemetry(event)
            return {
                "status": "Injected Cooling Degradation",
                "rack_id": rack_id,
                "inlet_temp_c": 39.5,
                "pue": 1.68,
                "cooling_efficiency": 0.26,
                "action": "Covariate drift injected on cooling_efficiency & PUE.",
            }

        elif scenario_key == "workload_surge":
            # Target NA GPU rack
            rack_id = "RACK-NA-03"
            event = {
                "event_id": str(uuid.uuid4()),
                "timestamp": now.isoformat(),
                "rack_id": rack_id,
                "datacenter_region": "NA",
                "server_type": "GPU",
                "cooling_type": "Liquid",
                "time_of_day": "Peak",
                "workload_intensity": 0.99,
                "cpu_utilization": 99.8,
                "memory_utilization": 98.0,
                "network_throughput_gbps": 540.0,
                "inlet_temperature_c": 33.5,
                "cooling_efficiency": 0.82,
                "power_consumption_kw": 118.0,
                "pue": 1.28,
                "carbon_emission_kg": 15.6,
                "compute_cost_usd": 52.0,
                "energy_efficiency_class": "Medium",
                "is_anomaly": 1,
                "injected_scenario": "workload_surge",
            }
            self.publish_telemetry(event)
            return {
                "status": "Injected Workload Surge",
                "rack_id": rack_id,
                "workload_intensity": 0.99,
                "cpu_utilization": 99.8,
                "power_kw": 118.0,
                "action": "Massive LLM fine-tuning cluster spike generated.",
            }

        elif scenario_key in ("corrupted_sensor_burst", "corrupted_dlq_burst"):
            # Burst of 15 corrupted packets violating physical laws
            corrupted_samples = [
                {"pue": 0.42, "reason": "PUE < 1.0 violates thermodynamics"},
                {"cpu_utilization": 155.0, "reason": "CPU utilization > 100%"},
                {"inlet_temperature_c": 95.0, "reason": "Inlet temp > 65C physical bound"},
                {"datacenter_region": "APAC", "rack_id": "RACK-NA-01", "reason": "Region prefix mismatch"},
                {"power_consumption_kw": -25.0, "reason": "Negative power consumption"},
            ]
            dlq_trapped = 0
            for i in range(15):
                sample = corrupted_samples[i % len(corrupted_samples)]
                bad_event = {
                    "event_id": str(uuid.uuid4()),
                    "timestamp": now.isoformat(),
                    "rack_id": sample.get("rack_id", "RACK-EU-01"),
                    "datacenter_region": sample.get("datacenter_region", "EU"),
                    "server_type": "Compute",
                    "cooling_type": "Air",
                    "time_of_day": "Peak",
                    "workload_intensity": 0.5,
                    "cpu_utilization": sample.get("cpu_utilization", 50.0),
                    "memory_utilization": 50.0,
                    "network_throughput_gbps": 50.0,
                    "inlet_temperature_c": sample.get("inlet_temperature_c", 24.0),
                    "cooling_efficiency": 0.7,
                    "power_consumption_kw": sample.get("power_consumption_kw", 25.0),
                    "pue": sample.get("pue", 1.25),
                    "carbon_emission_kg": 5.0,
                    "compute_cost_usd": 10.0,
                    "energy_efficiency_class": "Medium",
                    "is_anomaly": 0,
                    "injected_scenario": "corrupted_sensor_burst",
                }
                is_valid, _ = self.publish_telemetry(bad_event)
                if not is_valid:
                    dlq_trapped += 1

            return {
                "status": "Injected Corrupted Sensor Burst",
                "packets_sent": 15,
                "dlq_isolated_count": dlq_trapped,
                "action": f"{dlq_trapped} packets trapped and routed to dlq_corrupted_events table.",
            }

        return {"status": "Unknown Scenario", "action": "None"}

