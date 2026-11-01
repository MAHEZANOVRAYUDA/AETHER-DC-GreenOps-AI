"""Initial Model Training & Serialization Script for AETHER-DC.

Trains:
1. Champion Model: LightGBM (LGBMClassifier for anomalies + LGBMRegressor for PUE)
2. Challenger Model: XGBoost (XGBClassifier for anomalies + XGBRegressor for PUE)
3. Guardrail Model: IsolationForest (Unsupervised Out-Of-Distribution detector)
Saves artifacts to data/models/.
"""

import os
import sys
from pathlib import Path

# Fix joblib wmic deprecation on Windows
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from lightgbm import LGBMClassifier, LGBMRegressor
from xgboost import XGBClassifier, XGBRegressor

FEATURE_COLS = [
    "workload_intensity",
    "cpu_utilization",
    "memory_utilization",
    "network_throughput_gbps",
    "inlet_temperature_c",
    "cooling_efficiency",
    "power_consumption_kw",
    "it_equipment_power_kw",
    "cooling_overhead_kw",
    "cooling_stress_index",
    "rolling_temp_mean_short",
    "thermal_velocity_delta_c",
    "rolling_pue_mean_short",
    "server_type_encoded",
    "cooling_type_encoded",
    "region_encoded",
]


def prepare_training_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Prepares feature matrix and targets with physics features & label encodings."""
    df_feat = df.copy()

    # Derived physics features if not present
    if "it_equipment_power_kw" not in df_feat.columns:
        df_feat["it_equipment_power_kw"] = (
            df_feat["power_consumption_kw"] / df_feat["pue"].replace(0, 1.0)
        ).round(3)
    if "cooling_overhead_kw" not in df_feat.columns:
        df_feat["cooling_overhead_kw"] = (
            df_feat["power_consumption_kw"] - df_feat["it_equipment_power_kw"]
        ).round(3)
    if "cooling_stress_index" not in df_feat.columns:
        df_feat["cooling_stress_index"] = (
            df_feat["power_consumption_kw"] / (df_feat["cooling_efficiency"] + 0.05)
        ).round(3)
    if "rolling_temp_mean_short" not in df_feat.columns:
        df_feat["rolling_temp_mean_short"] = df_feat["inlet_temperature_c"]
    if "thermal_velocity_delta_c" not in df_feat.columns:
        df_feat["thermal_velocity_delta_c"] = 0.0
    if "rolling_pue_mean_short" not in df_feat.columns:
        df_feat["rolling_pue_mean_short"] = df_feat["pue"]

    # Encodings
    server_map = {"GPU": 0, "Compute": 1, "Storage": 2, "Edge": 3}
    cooling_map = {"Liquid": 0, "Hybrid": 1, "Air": 2}
    region_map = {"NA": 0, "EU": 1, "APAC": 2, "ME": 3}

    df_feat["server_type_encoded"] = df_feat["server_type"].map(server_map).fillna(0).astype(int)
    df_feat["cooling_type_encoded"] = df_feat["cooling_type"].map(cooling_map).fillna(0).astype(int)
    df_feat["region_encoded"] = df_feat["datacenter_region"].map(region_map).fillna(0).astype(int)

    X = df_feat[FEATURE_COLS].fillna(0)
    y_clf = (
        df_feat["is_anomaly"].astype(int)
        if "is_anomaly" in df_feat.columns
        else pd.Series(np.zeros(len(df_feat), dtype=int))
    )
    y_reg = (
        df_feat["pue"].astype(float)
        if "pue" in df_feat.columns
        else pd.Series(np.ones(len(df_feat), dtype=float) * 1.20)
    )

    return X, y_clf, y_reg


def train_and_save_all_models(df: pd.DataFrame, models_dir: Path) -> dict:
    """Trains Champion (LGBM), Challenger (XGBoost), and Guardrail (IsoForest)."""
    models_dir.mkdir(parents=True, exist_ok=True)
    X, y_clf, y_reg = prepare_training_features(df)

    print(f"[*] Training baseline models on {len(X)} records...")

    # 1. Champion Model: LightGBM
    lgbm_clf = LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.05,
        random_state=42,
        verbosity=-1,
    )
    lgbm_clf.fit(X, y_clf)

    lgbm_reg = LGBMRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.05,
        random_state=42,
        verbosity=-1,
    )
    lgbm_reg.fit(X, y_reg)

    # 2. Challenger Model: XGBoost
    xgb_clf = XGBClassifier(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.04,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
    )
    xgb_clf.fit(X, y_clf)

    xgb_reg = XGBRegressor(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.04,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
    )
    xgb_reg.fit(X, y_reg)

    # 3. Guardrail Model: IsolationForest (Unsupervised OOD)
    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )
    iso_forest.fit(X)

    # Save artifacts
    artifacts = {
        "champion_lgbm_clf.joblib": lgbm_clf,
        "champion_lgbm_reg.joblib": lgbm_reg,
        "challenger_xgb_clf.joblib": xgb_clf,
        "challenger_xgb_reg.joblib": xgb_reg,
        "guard_isolation_forest.joblib": iso_forest,
    }

    for filename, model in artifacts.items():
        filepath = models_dir / filename
        joblib.dump(model, filepath)
        print(f"    [+] Saved model artifact: {filepath.name}")

    # Save baseline feature summary for PSI drift reference (including raw target pue)
    feature_ref_path = models_dir / "baseline_feature_reference.parquet"
    X_ref = X.copy()
    X_ref["pue"] = y_reg.values
    X_ref.to_parquet(feature_ref_path, index=False)
    print(f"    [+] Saved baseline feature reference with PUE: {feature_ref_path.name}")

    return artifacts
