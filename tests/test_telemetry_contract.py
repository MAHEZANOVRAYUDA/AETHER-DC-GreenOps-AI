"""Unit Tests for Pydantic v2 Telemetry Contract & DLQ Routing."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from src.schemas.telemetry_contract import (
    DLQCorruptedEvent,
    SRERemediationPlan,
    TelemetryEventContract,
)


def test_valid_telemetry_contract():
    """Valid contract should instantiate cleanly without error."""
    payload = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-APAC-02",
        "datacenter_region": "APAC",
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "time_of_day": "Peak",
        "workload_intensity": 0.85,
        "cpu_utilization": 88.0,
        "memory_utilization": 82.0,
        "network_throughput_gbps": 220.0,
        "inlet_temperature_c": 24.5,
        "cooling_efficiency": 0.88,
        "power_consumption_kw": 85.0,
        "pue": 1.18,
        "carbon_emission_kg": 12.0,
        "compute_cost_usd": 32.0,
        "energy_efficiency_class": "High",
        "is_anomaly": 0,
    }
    contract = TelemetryEventContract(**payload)
    assert contract.rack_id == "RACK-APAC-02"
    assert contract.datacenter_region == "APAC"
    assert contract.pue == 1.18


@pytest.mark.parametrize(
    "bad_key,bad_value",
    [
        ("pue", 0.85),  # Thermodynamic violation (PUE < 1.01)
        ("pue", 3.80),  # Exceeds max allowable PUE (3.50)
        ("cpu_utilization", 105.0),  # CPU > 100%
        ("inlet_temperature_c", 75.0),  # Exceeds physical bounds (65.0)
        ("cooling_efficiency", 0.02),  # Lower than physical floor (0.05)
        ("power_consumption_kw", -10.0),  # Negative power consumption
    ],
)
def test_physics_boundary_violations(bad_key, bad_value):
    """Physical boundaries must raise ValidationError."""
    base_payload = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-EU-01",
        "datacenter_region": "EU",
        "server_type": "Compute",
        "cooling_type": "Air",
        "time_of_day": "Peak",
        "workload_intensity": 0.5,
        "cpu_utilization": 50.0,
        "memory_utilization": 50.0,
        "network_throughput_gbps": 50.0,
        "inlet_temperature_c": 22.0,
        "cooling_efficiency": 0.7,
        "power_consumption_kw": 30.0,
        "pue": 1.25,
        "carbon_emission_kg": 5.0,
        "compute_cost_usd": 10.0,
        "energy_efficiency_class": "Medium",
    }
    base_payload[bad_key] = bad_value
    with pytest.raises(ValidationError):
        TelemetryEventContract(**base_payload)


def test_rack_region_mismatch_violation():
    """Rack ID prefix must match datacenter_region."""
    payload = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-NA-01",
        "datacenter_region": "APAC",  # Mismatch!
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "time_of_day": "Peak",
        "workload_intensity": 0.5,
        "cpu_utilization": 50.0,
        "memory_utilization": 50.0,
        "network_throughput_gbps": 50.0,
        "inlet_temperature_c": 22.0,
        "cooling_efficiency": 0.7,
        "power_consumption_kw": 30.0,
        "pue": 1.25,
        "carbon_emission_kg": 5.0,
        "compute_cost_usd": 10.0,
        "energy_efficiency_class": "Medium",
    }
    with pytest.raises(ValidationError) as exc:
        TelemetryEventContract(**payload)
    assert "Region mismatch" in str(exc.value)


def test_dlq_model_instantiation():
    """DLQ model stores error details without crashing."""
    dlq = DLQCorruptedEvent(
        raw_payload='{"pue": 0.5}',
        error_type="ValidationError",
        error_detail="PUE violates thermodynamics",
    )
    assert dlq.source_topic == "dc.telemetry.raw"
    assert dlq.dlq_id is not None


def test_sre_remediation_plan_contract():
    """SRERemediationPlan strict validation check."""
    plan = SRERemediationPlan(
        incident_id="INC-1001",
        rack_id="RACK-APAC-01",
        root_cause_summary="Cooling pump failure caused thermal runaway",
        primary_physical_driver="inlet_temperature_c",
        confidence_score=0.96,
        recommended_cooling_action="Increase liquid pump flow rate by +18%",
        recommended_workload_action="Rebalance 15% GPU batch jobs to EU cluster",
        recommended_mlops_action="Hot-swap to Challenger XGBoost due to covariate drift",
        projected_pue_after_action=1.17,
        estimated_hourly_savings_usd=42.50,
        estimated_carbon_reduction_kg=8.4,
    )
    assert plan.confidence_score == 0.96
    assert plan.projected_pue_after_action >= 1.01
