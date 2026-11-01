"""Unit Tests for MLOps Engine: 10-bin PSI Drift, Shadow Evaluation & Hot-Swap."""

import numpy as np
import pandas as pd
import pytest

from src.mlops.drift_detector import (
    calculate_ks_drift,
    calculate_psi,
    MultiFeatureDriftDetector,
)
from src.mlops.model_registry import MLOpsModelRegistry
from src.mlops.shap_explainer import FastTreeSHAPExplainer
from src.lakehouse.medallion_engine import MedallionEngine


def test_psi_identical_distribution():
    """Identical distributions should have PSI close to zero (< 0.05)."""
    np.random.seed(42)
    reference = np.random.normal(25.0, 3.0, 1000)
    current = np.random.normal(25.0, 3.0, 1000)

    psi = calculate_psi(reference, current, num_bins=10)
    assert psi < 0.05


def test_psi_critical_drift():
    """Significantly shifted distribution should trigger critical drift (PSI >= 0.20)."""
    np.random.seed(42)
    reference = np.random.normal(22.0, 2.0, 1000)
    current = np.random.normal(38.0, 4.0, 1000)  # Severe thermal shift

    psi = calculate_psi(reference, current, num_bins=10)
    assert psi >= 0.20


def test_ks_drift_detection():
    """Kolmogorov-Smirnov test detects significant distributional drift."""
    np.random.seed(42)
    reference = np.random.exponential(1.5, 1000)
    current = np.random.exponential(4.5, 1000)

    ks_stat, p_val, is_drift = calculate_ks_drift(reference, current)
    assert is_drift is True
    assert p_val < 0.01
    assert ks_stat > 0.15


def test_multi_feature_drift_detector():
    """Detector computes per-feature PSI and overall alert status."""
    np.random.seed(42)
    base_data = {
        "inlet_temperature_c": np.random.normal(22.0, 2.0, 200),
        "cooling_efficiency": np.random.normal(0.85, 0.05, 200),
        "workload_intensity": np.random.uniform(0.3, 0.8, 200),
        "power_consumption_kw": np.random.normal(50.0, 10.0, 200),
        "pue": np.random.normal(1.18, 0.04, 200),
        "cpu_utilization": np.random.normal(60.0, 10.0, 200),
    }
    base_df = pd.DataFrame(base_data)

    # Shifted live data
    live_data = dict(base_data)
    live_data["inlet_temperature_c"] = np.random.normal(42.0, 3.0, 200)  # Thermal spike
    live_df = pd.DataFrame(live_data)

    detector = MultiFeatureDriftDetector(baseline_df=base_df)
    drift_report = detector.compute_drifts(live_df)

    assert "inlet_temperature_c" in drift_report["feature_metrics"]
    assert drift_report["feature_metrics"]["inlet_temperature_c"]["psi_score"] >= 0.20
    assert drift_report["overall_status"] == "CRITICAL ALERT"


def test_model_registry_shadow_prediction(tmp_path):
    """Model registry runs shadow evaluation on Champion, Challenger, and Guard."""
    registry = MLOpsModelRegistry.get_instance()

    sample_df = pd.DataFrame([{
        "workload_intensity": 0.85,
        "cpu_utilization": 88.0,
        "memory_utilization": 80.0,
        "network_throughput_gbps": 220.0,
        "inlet_temperature_c": 35.0,
        "cooling_efficiency": 0.65,
        "power_consumption_kw": 80.0,
        "pue": 1.25,
        "carbon_emission_kg": 12.0,
        "compute_cost_usd": 30.0,
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "datacenter_region": "APAC",
        "is_anomaly": 1,
    }])

    pred = registry.predict_shadow(sample_df)
    assert "active_model_name" in pred
    assert "champion_lgbm_prob" in pred
    assert "challenger_xgb_prob" in pred
    assert "guard_isoforest_score" in pred
    assert pred["inference_latency_ms"] >= 0.0


def test_zero_downtime_hot_swap():
    """Hot-swap atomically swaps Champion and Challenger roles."""
    registry = MLOpsModelRegistry.get_instance()
    initial_champ = registry.active_champion_name
    initial_chall = registry.challenger_name

    receipt = registry.hot_swap_now(reason="Test Hot-Swap", psi=0.24)
    assert receipt["status"] == "HOT_SWAP_SUCCESS"
    assert registry.active_champion_name == initial_chall
    assert registry.challenger_name == initial_champ

    # Swap back
    receipt2 = registry.hot_swap_now(reason="Reverting Test Hot-Swap", psi=0.08)
    assert receipt2["status"] == "HOT_SWAP_SUCCESS"
    assert registry.active_champion_name == initial_champ


def test_treeshap_feature_attribution():
    """TreeSHAP explainer attributes incident to key thermodynamic drivers."""
    registry = MLOpsModelRegistry.get_instance()
    clf_model = registry.models.get("champion_lgbm_clf")

    explainer = FastTreeSHAPExplainer(model=clf_model)
    row = pd.DataFrame([{
        "workload_intensity": 0.95,
        "cpu_utilization": 98.0,
        "memory_utilization": 92.0,
        "network_throughput_gbps": 350.0,
        "inlet_temperature_c": 46.5,
        "cooling_efficiency": 0.22,
        "power_consumption_kw": 105.0,
        "pue": 1.74,
        "carbon_emission_kg": 18.0,
        "compute_cost_usd": 45.0,
        "server_type": "GPU",
        "cooling_type": "Liquid",
        "datacenter_region": "APAC",
    }])

    attributions = explainer.explain_instance(row)
    assert len(attributions) > 0
    top_feat = attributions[0]
    assert "feature" in top_feat
    assert "abs_impact" in top_feat
    assert top_feat["abs_impact"] >= 0.0
