"""Unit Tests for DuckDB Medallion Lakehouse Engine (Bronze -> Silver -> Gold)."""

from datetime import datetime, timezone
import pytest
import duckdb

from src.lakehouse.medallion_engine import MedallionEngine
from scripts.bootstrap_datasets import initialize_duckdb_schema


@pytest.fixture
def temp_lakehouse(tmp_path):
    """Provides a fresh temporary DuckDB lakehouse instance."""
    db_file = tmp_path / "test_aether.duckdb"
    con = duckdb.connect(str(db_file))
    initialize_duckdb_schema(con)
    con.close()
    return MedallionEngine(db_path=db_file)


def test_bronze_ingestion_valid_event(temp_lakehouse):
    """Valid event routes cleanly to bronze_telemetry_events."""
    event = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-NA-01",
        "datacenter_region": "NA",
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "time_of_day": "Peak",
        "workload_intensity": 0.8,
        "cpu_utilization": 85.0,
        "memory_utilization": 80.0,
        "network_throughput_gbps": 200.0,
        "inlet_temperature_c": 22.0,
        "cooling_efficiency": 0.85,
        "power_consumption_kw": 75.0,
        "pue": 1.16,
        "carbon_emission_kg": 10.0,
        "compute_cost_usd": 28.0,
        "energy_efficiency_class": "High",
        "is_anomaly": 0,
    }
    is_valid, msg = temp_lakehouse.ingest_event(event)
    assert is_valid is True
    assert msg is not None

    silver_df = temp_lakehouse.get_silver_features(rack_id="RACK-NA-01")
    assert len(silver_df) == 1
    # Check physics features calculated
    row = silver_df.iloc[0]
    assert "it_equipment_power_kw" in row
    assert "cooling_overhead_kw" in row
    assert "cooling_stress_index" in row
    assert row["it_equipment_power_kw"] > 0


def test_dlq_routing_invalid_event(temp_lakehouse):
    """Corrupted event (violating physics) routes to dlq_corrupted_events."""
    bad_event = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-EU-01",
        "datacenter_region": "EU",
        "server_type": "Compute",
        "cooling_type": "Air",
        "time_of_day": "Peak",
        "workload_intensity": 0.5,
        "cpu_utilization": 150.0,  # Invalid: > 100%
        "memory_utilization": 50.0,
        "network_throughput_gbps": 50.0,
        "inlet_temperature_c": 22.0,
        "cooling_efficiency": 0.7,
        "power_consumption_kw": 30.0,
        "pue": 0.5,  # Invalid: < 1.01
        "carbon_emission_kg": 5.0,
        "compute_cost_usd": 10.0,
        "energy_efficiency_class": "Medium",
    }
    is_valid, msg = temp_lakehouse.ingest_event(bad_event)
    assert is_valid is False
    assert "DLQ Isolated" in msg

    dlq_df = temp_lakehouse.get_dlq_events()
    assert len(dlq_df) == 1
    assert "ValidationError" in dlq_df.iloc[0]["error_type"]


def test_incident_remediation(temp_lakehouse):
    """Incident remediation updates status to Resolved and sets new target PUE."""
    # Ingest an anomaly event to create an active incident
    anomaly_event = {
        "timestamp": datetime.now(timezone.utc),
        "rack_id": "RACK-APAC-01",
        "datacenter_region": "APAC",
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "time_of_day": "Peak",
        "workload_intensity": 0.95,
        "cpu_utilization": 98.0,
        "memory_utilization": 92.0,
        "network_throughput_gbps": 350.0,
        "inlet_temperature_c": 44.5,
        "cooling_efficiency": 0.25,
        "power_consumption_kw": 95.0,
        "pue": 1.72,
        "carbon_emission_kg": 15.0,
        "compute_cost_usd": 40.0,
        "energy_efficiency_class": "Low",
        "is_anomaly": 1,
    }
    temp_lakehouse.ingest_event(anomaly_event)

    incidents = temp_lakehouse.get_active_incidents()
    assert len(incidents) >= 1
    target_inc_id = incidents.iloc[0]["incident_id"]

    # Remediate
    success = temp_lakehouse.remediate_incident(target_inc_id, new_target_pue=1.15)
    assert success is True

    # Check that it's no longer in active incidents
    remaining = temp_lakehouse.get_active_incidents()
    assert target_inc_id not in remaining["incident_id"].values


def test_model_hotswap_audit_logging(temp_lakehouse):
    """Recording hot-swap inserts a record in mlops_model_audit_log."""
    log_id = temp_lakehouse.record_model_hotswap(
        previous_champion="champion_lgbm",
        new_champion="challenger_xgb",
        reason="PSI Drift > 0.20 and Challenger F1 higher by +0.024",
        psi=0.235,
        delta_f1=0.024,
        delta_rmse=-0.035,
    )
    assert log_id.startswith("SWAP-")

    logs = temp_lakehouse.get_hotswap_audit_logs()
    assert len(logs) == 1
    assert logs.iloc[0]["previous_champion"] == "champion_lgbm"
    assert logs.iloc[0]["new_champion"] == "challenger_xgb"

