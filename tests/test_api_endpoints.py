"""Integration Tests for FastAPI Backend Endpoints."""

import os
os.environ["LOKY_MAX_CPU_COUNT"] = "4"

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_api_healthcheck():
    """GET /health returns healthy status and metadata."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "runtime_mode" in data
    assert "mean_facility_pue" in data


def test_api_predict_shadow():
    """POST /predict runs shadow prediction across all models."""
    payload = {
        "workload_intensity": 0.88,
        "cpu_utilization": 90.0,
        "memory_utilization": 85.0,
        "network_throughput_gbps": 250.0,
        "inlet_temperature_c": 28.0,
        "cooling_efficiency": 0.82,
        "power_consumption_kw": 85.0,
        "pue": 1.20,
        "carbon_emission_kg": 14.0,
        "compute_cost_usd": 32.0,
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "datacenter_region": "APAC",
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "active_anomaly_prob" in data
    assert "champion_lgbm_prob" in data
    assert "challenger_xgb_prob" in data
    assert "inference_latency_ms" in data


def test_api_drift_metrics():
    """GET /drift returns PSI and KS metrics."""
    res = client.get("/drift")
    assert res.status_code == 200
    data = res.json()
    assert "max_psi" in data
    assert "feature_metrics" in data


def test_api_inject_scenario():
    """POST /inject triggers scenario injection."""
    res = client.post("/inject", json={"scenario_name": "thermal_runaway"})
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "Injected" in data["status"]


def test_api_prometheus_metrics():
    """GET /metrics returns text-formatted Prometheus metrics."""
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "aether_telemetry_events_total" in res.text
    assert "aether_facility_pue_gauge" in res.text

