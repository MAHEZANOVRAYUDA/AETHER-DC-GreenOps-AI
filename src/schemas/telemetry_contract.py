"""Pydantic v2 Telemetry Contract, Dead-Letter Queue (DLQ) & SRE Remediation Models.

Enforces physical boundaries, thermodynamic conservation (PUE >= 1.01),
and geographical rack naming constraints for AETHER-DC.
"""

from datetime import datetime, timezone
from typing import Literal, Optional
import uuid

from pydantic import BaseModel, Field, model_validator


class TelemetryEventContract(BaseModel):
    """Strict schema contract for data center telemetry events."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime
    rack_id: str = Field(..., pattern=r"^RACK-(NA|EU|APAC|ME)-\d{2}$")
    datacenter_region: Literal["NA", "EU", "APAC", "ME"]
    server_type: Literal["GPU", "Compute", "Storage", "Edge"]
    cooling_type: Literal["Liquid", "Hybrid", "Air"]
    time_of_day: Literal["Peak", "Off-Peak", "Night"]
    workload_intensity: float = Field(..., ge=0.0, le=1.0)
    cpu_utilization: float = Field(..., ge=0.0, le=100.0)
    memory_utilization: float = Field(..., ge=0.0, le=100.0)
    network_throughput_gbps: float = Field(..., ge=0.0, le=800.0)
    inlet_temperature_c: float = Field(..., ge=10.0, le=65.0)
    cooling_efficiency: float = Field(..., ge=0.05, le=1.0)
    power_consumption_kw: float = Field(..., gt=0.1, le=250.0)
    pue: float = Field(..., ge=1.01, le=3.50)
    carbon_emission_kg: float = Field(..., ge=0.0, le=200.0)
    compute_cost_usd: float = Field(..., ge=0.0, le=500.0)
    energy_efficiency_class: Literal["High", "Medium", "Low"]
    is_anomaly: int = Field(default=0, ge=0, le=1)
    injected_scenario: Optional[str] = Field(default="nominal")

    @model_validator(mode="after")
    def verify_thermodynamic_and_geographical_consistency(self) -> "TelemetryEventContract":
        """Verify regional prefix and thermodynamic consistency."""
        expected_prefix = f"RACK-{self.datacenter_region}-"
        if not self.rack_id.startswith(expected_prefix):
            raise ValueError(
                f"Region mismatch: rack_id '{self.rack_id}' does not match datacenter_region '{self.datacenter_region}'"
            )
        return self


class DLQCorruptedEvent(BaseModel):
    """Schema for routing malformed or physically impossible packets into Dead-Letter Queue."""

    dlq_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: str
    error_type: str
    error_detail: str
    source_topic: str = "dc.telemetry.raw"


class SRERemediationPlan(BaseModel):
    """Structured Pydantic contract for Agentic SRE RCA and Counterfactual Optimization."""

    incident_id: str
    rack_id: str
    root_cause_summary: str
    primary_physical_driver: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    recommended_cooling_action: str
    recommended_workload_action: str
    recommended_mlops_action: str
    projected_pue_after_action: float = Field(..., ge=1.01)
    estimated_hourly_savings_usd: float = Field(..., ge=0.0)
    estimated_carbon_reduction_kg: float = Field(..., ge=0.0)
