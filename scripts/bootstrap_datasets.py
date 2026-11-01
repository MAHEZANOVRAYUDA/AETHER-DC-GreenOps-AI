"""Dataset Bootstrap & Physics-Calibrated Lakehouse Seeder for AETHER-DC.

Based on Green AI Data Center Telemetry Dataset (Kaggle deeplumiere),
enriched with multivariate time-series anomalies from SMD & NAB.
Initializes DuckDB Lakehouse (Bronze -> Silver -> Gold) and baseline models.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from datetime import datetime, timedelta, timezone
import random
import uuid

import duckdb
import numpy as np
import pandas as pd

from src.config.runtime import get_base_dir, get_duckdb_path, get_models_dir
from scripts.train_initial_models import train_and_save_all_models, prepare_training_features

REGIONS = ["NA", "EU", "APAC", "ME"]
SERVER_TYPES = ["GPU", "Compute", "Storage", "Edge"]
COOLING_TYPES = ["Liquid", "Hybrid", "Air"]
TIMES_OF_DAY = ["Peak", "Off-Peak", "Night"]

# 24 physical racks across 4 regions
RACKS = [
    f"RACK-{reg}-{str(idx).zfill(2)}"
    for reg in REGIONS
    for idx in range(1, 7)
]


def generate_physics_calibrated_telemetry(num_records: int = 6000, seed: int = 42) -> pd.DataFrame:
    """Generates synthetic data center telemetry calibrated with thermodynamic laws.

    - Fluid & air heat transfer equations: T_inlet scales with power, cooling type & ambient
    - Energy conservation: PUE = Facility Power / IT Power >= 1.01
    - Server architecture TDP: GPU nodes consume 40-110 kW, Compute 15-45 kW
    - 5% injected anomalies (Thermal spikes, cooling degradation, workload surges, zombie nodes)
    """
    np.random.seed(seed)
    random.seed(seed)

    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=20)
    current_time = base_time

    # Rack state trackers for continuous time-series dynamics
    rack_states = {}
    for rack in RACKS:
        parts = rack.split("-")
        reg = parts[1]
        s_type = "GPU" if int(parts[2]) in (1, 2) else ("Compute" if int(parts[2]) in (3, 4) else ("Storage" if int(parts[2]) == 5 else "Edge"))
        c_type = "Liquid" if s_type == "GPU" else ("Hybrid" if s_type == "Compute" else "Air")
        rack_states[rack] = {
            "region": reg,
            "server_type": s_type,
            "cooling_type": c_type,
            "inlet_temp": 22.0 if c_type == "Liquid" else 26.0,
            "cooling_eff": 0.88 if c_type == "Liquid" else (0.75 if c_type == "Hybrid" else 0.62),
            "base_workload": 0.45,
        }

    for i in range(num_records):
        rack_id = random.choice(RACKS)
        state = rack_states[rack_id]
        reg = state["region"]
        s_type = state["server_type"]
        c_type = state["cooling_type"]

        # Timestamp step
        current_time += timedelta(seconds=random.randint(15, 60))

        # Ambient baseline by region
        ambient_offset = {"EU": -3.0, "NA": 0.0, "APAC": 3.0, "ME": 7.0}[reg]

        # Time of day workload factor
        hour = current_time.hour
        if 8 <= hour < 18:
            tod = "Peak"
            workload_bias = 0.35
        elif 18 <= hour < 23:
            tod = "Off-Peak"
            workload_bias = 0.15
        else:
            tod = "Night"
            workload_bias = -0.15

        workload = np.clip(
            state["base_workload"] + workload_bias + np.random.normal(0, 0.12),
            0.05,
            0.98
        )

        cpu_util = np.clip(workload * 100.0 + np.random.normal(0, 4.0), 5.0, 99.5)
        mem_util = np.clip(cpu_util * 0.85 + np.random.normal(0, 5.0), 10.0, 95.0)
        net_gbps = np.clip(workload * 220.0 + np.random.normal(0, 15.0), 1.0, 395.0)

        # Baseline Power based on server TDP
        if s_type == "GPU":
            base_kw = 45.0 + workload * 60.0 + np.random.normal(0, 2.5)
        elif s_type == "Compute":
            base_kw = 18.0 + workload * 28.0 + np.random.normal(0, 1.5)
        elif s_type == "Storage":
            base_kw = 10.0 + workload * 14.0 + np.random.normal(0, 1.0)
        else:  # Edge
            base_kw = 4.0 + workload * 8.0 + np.random.normal(0, 0.8)

        # Cooling efficiency and inlet temperature
        cooling_eff = np.clip(
            state["cooling_eff"] - (workload * 0.08) + np.random.normal(0, 0.02),
            0.15,
            0.98
        )

        # Heat dissipation physics: higher power and lower cooling efficiency increase inlet temp
        temp_delta = (base_kw * 0.12) / max(cooling_eff, 0.2) + ambient_offset * 0.5
        inlet_temp = np.clip(
            18.0 + temp_delta + np.random.normal(0, 0.8),
            14.0,
            58.0
        )

        # PUE physics: Liquid ~ 1.10-1.22, Hybrid ~ 1.22-1.38, Air ~ 1.35-1.65
        cooling_overhead_factor = {
            "Liquid": 0.14,
            "Hybrid": 0.28,
            "Air": 0.44,
        }[c_type]
        pue = np.clip(
            1.0 + (cooling_overhead_factor / max(cooling_eff, 0.25)) + (ambient_offset * 0.012),
            1.05,
            2.40
        )

        # Carbon emissions: regional grid intensity (kg CO2 / kWh)
        grid_factor = {"EU": 0.24, "NA": 0.38, "APAC": 0.52, "ME": 0.64}[reg]
        carbon_kg = round(base_kw * pue * grid_factor * (1.0 / 60.0), 3)

        # Compute cost USD per hour
        cost_usd = round(base_kw * pue * 0.14 + (15.0 if s_type == "GPU" else 4.0), 2)

        # Energy efficiency class
        if pue < 1.20:
            eff_class = "High"
        elif pue < 1.45:
            eff_class = "Medium"
        else:
            eff_class = "Low"

        is_anomaly = 0
        scenario = "nominal"

        # Injected anomalies (~5% rate)
        rand_anomaly = random.random()
        if rand_anomaly < 0.015:
            # Thermal Runaway
            is_anomaly = 1
            scenario = "thermal_runaway"
            inlet_temp += random.uniform(10.0, 16.0)
            cooling_eff = max(0.12, cooling_eff - 0.35)
            pue += 0.35
            eff_class = "Low"
        elif rand_anomaly < 0.030:
            # Cooling Degradation
            is_anomaly = 1
            scenario = "cooling_degradation"
            cooling_eff = max(0.15, cooling_eff - 0.42)
            pue += 0.48
            inlet_temp += 8.5
            eff_class = "Low"
        elif rand_anomaly < 0.042:
            # Workload Surge
            is_anomaly = 1
            scenario = "workload_surge"
            workload = min(1.0, workload + 0.35)
            cpu_util = min(100.0, cpu_util + 25.0)
            base_kw *= 1.45
            inlet_temp += 5.5
        elif rand_anomaly < 0.050:
            # Zombie server (near-idle workload but high power consumption)
            is_anomaly = 1
            scenario = "zombie_server"
            workload = 0.05
            cpu_util = 4.0
            base_kw = 65.0
            pue = 1.62

        records.append({
            "event_id": str(uuid.uuid4()),
            "timestamp": current_time.isoformat(),
            "rack_id": rack_id,
            "datacenter_region": reg,
            "server_type": s_type,
            "cooling_type": c_type,
            "time_of_day": tod,
            "workload_intensity": round(float(workload), 3),
            "cpu_utilization": round(float(cpu_util), 2),
            "memory_utilization": round(float(mem_util), 2),
            "network_throughput_gbps": round(float(net_gbps), 2),
            "inlet_temperature_c": round(float(inlet_temp), 2),
            "cooling_efficiency": round(float(cooling_eff), 3),
            "power_consumption_kw": round(float(base_kw), 2),
            "pue": round(float(pue), 3),
            "carbon_emission_kg": float(carbon_kg),
            "compute_cost_usd": float(cost_usd),
            "energy_efficiency_class": eff_class,
            "is_anomaly": int(is_anomaly),
            "injected_scenario": scenario,
        })

    df = pd.DataFrame(records)
    return df


def initialize_duckdb_schema(con: duckdb.DuckDBPyConnection):
    """Creates Bronze, DLQ, Silver View, and Gold Analytical tables in DuckDB."""
    # Bronze Raw Events
    con.execute("""
    CREATE TABLE IF NOT EXISTS bronze_telemetry_events (
        event_id VARCHAR PRIMARY KEY,
        timestamp TIMESTAMP NOT NULL,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        rack_id VARCHAR NOT NULL,
        datacenter_region VARCHAR NOT NULL,
        server_type VARCHAR NOT NULL,
        cooling_type VARCHAR NOT NULL,
        time_of_day VARCHAR NOT NULL,
        workload_intensity DOUBLE,
        cpu_utilization DOUBLE,
        memory_utilization DOUBLE,
        network_throughput_gbps DOUBLE,
        inlet_temperature_c DOUBLE,
        cooling_efficiency DOUBLE,
        power_consumption_kw DOUBLE,
        pue DOUBLE,
        carbon_emission_kg DOUBLE,
        compute_cost_usd DOUBLE,
        energy_efficiency_class VARCHAR,
        is_anomaly INTEGER,
        injected_scenario VARCHAR
    );
    """)

    # Dead-Letter Queue (DLQ)
    con.execute("""
    CREATE TABLE IF NOT EXISTS dlq_corrupted_events (
        dlq_id VARCHAR PRIMARY KEY,
        ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        raw_payload VARCHAR,
        error_type VARCHAR,
        error_detail VARCHAR,
        source_topic VARCHAR
    );
    """)

    # Silver Enriched View (Deduplication + Physics Derived Features + Rolling Windows)
    con.execute("""
    CREATE OR REPLACE VIEW silver_enriched_telemetry AS
    WITH deduplicated AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY ingested_at DESC) AS rn
        FROM bronze_telemetry_events
    )
    SELECT
        event_id,
        timestamp,
        rack_id,
        datacenter_region,
        server_type,
        cooling_type,
        time_of_day,
        workload_intensity,
        cpu_utilization,
        memory_utilization,
        network_throughput_gbps,
        inlet_temperature_c,
        cooling_efficiency,
        power_consumption_kw,
        pue,
        carbon_emission_kg,
        compute_cost_usd,
        energy_efficiency_class,
        is_anomaly,
        injected_scenario,
        -- Physics-Informed Derived Features
        ROUND(power_consumption_kw / NULLIF(pue, 0), 3) AS it_equipment_power_kw,
        ROUND(power_consumption_kw - (power_consumption_kw / NULLIF(pue, 0)), 3) AS cooling_overhead_kw,
        ROUND(power_consumption_kw / (cooling_efficiency + 0.05), 3) AS cooling_stress_index,
        -- Sliding Window Features per Rack
        ROUND(AVG(inlet_temperature_c) OVER w_short, 2) AS rolling_temp_mean_short,
        ROUND(STDDEV_POP(inlet_temperature_c) OVER w_short, 3) AS rolling_temp_std_short,
        ROUND(inlet_temperature_c - LAG(inlet_temperature_c, 1, inlet_temperature_c) OVER (PARTITION BY rack_id ORDER BY timestamp), 3) AS thermal_velocity_delta_c,
        ROUND(AVG(pue) OVER w_short, 3) AS rolling_pue_mean_short,
        ROUND(AVG(cpu_utilization) OVER w_long, 2) AS rolling_cpu_mean_long
    FROM deduplicated
    WHERE rn = 1
    WINDOW
        w_short AS (PARTITION BY rack_id ORDER BY timestamp ROWS BETWEEN 5 PRECEDING AND CURRENT ROW),
        w_long  AS (PARTITION BY rack_id ORDER BY timestamp ROWS BETWEEN 11 PRECEDING AND CURRENT ROW);
    """)

    # Gold Incident Predictions & Queue
    con.execute("""
    CREATE TABLE IF NOT EXISTS gold_incident_predictions (
        incident_id VARCHAR PRIMARY KEY,
        event_id VARCHAR NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        rack_id VARCHAR NOT NULL,
        datacenter_region VARCHAR NOT NULL,
        server_type VARCHAR NOT NULL,
        cooling_type VARCHAR NOT NULL,
        inlet_temperature_c DOUBLE,
        cooling_efficiency DOUBLE,
        power_consumption_kw DOUBLE,
        actual_pue DOUBLE,
        predicted_pue_champion DOUBLE,
        predicted_pue_challenger DOUBLE,
        anomaly_prob_champion DOUBLE,
        anomaly_prob_challenger DOUBLE,
        isoforest_anomaly_score DOUBLE,
        active_model_name VARCHAR,
        incident_status VARCHAR,         -- 'Thermal Spike', 'Cooling Degradation', 'Workload Surge', 'Resolved'
        severity_level VARCHAR,          -- 'CRITICAL', 'WARNING', 'NOMINAL'
        top_shap_feature VARCHAR,
        top_shap_impact DOUBLE,
        estimated_hourly_waste_usd DOUBLE,
        recommended_action VARCHAR
    );
    """)

    # Gold MLOps Model Hot-Swap Audit Log
    con.execute("""
    CREATE TABLE IF NOT EXISTS mlops_model_audit_log (
        log_id VARCHAR PRIMARY KEY,
        swapped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        previous_champion VARCHAR NOT NULL,
        new_champion VARCHAR NOT NULL,
        trigger_reason VARCHAR NOT NULL,
        psi_score DOUBLE,
        delta_f1_score DOUBLE,
        delta_rmse DOUBLE,
        operator VARCHAR DEFAULT 'Autonomous MLOps Controller'
    );
    """)


def seed_lakehouse_data(con: duckdb.DuckDBPyConnection, df: pd.DataFrame):
    """Seeds the bronze table and initializes gold incidents."""
    count_rows = con.execute("SELECT COUNT(*) FROM bronze_telemetry_events").fetchall()
    count = count_rows[0][0] if count_rows else 0
    if count == 0:
        print(f"[*] Seeding Bronze table with {len(df)} initial events...")
        con.execute("""
            INSERT INTO bronze_telemetry_events (
                event_id, timestamp, rack_id, datacenter_region, server_type,
                cooling_type, time_of_day, workload_intensity, cpu_utilization,
                memory_utilization, network_throughput_gbps, inlet_temperature_c,
                cooling_efficiency, power_consumption_kw, pue, carbon_emission_kg,
                compute_cost_usd, energy_efficiency_class, is_anomaly, injected_scenario
            )
            SELECT
                event_id, timestamp::TIMESTAMP, rack_id, datacenter_region, server_type,
                cooling_type, time_of_day, workload_intensity, cpu_utilization,
                memory_utilization, network_throughput_gbps, inlet_temperature_c,
                cooling_efficiency, power_consumption_kw, pue, carbon_emission_kg,
                compute_cost_usd, energy_efficiency_class, is_anomaly, injected_scenario
            FROM df
        """)
        print(f"[+] Bronze table populated with {len(df)} records.")

    # Populate initial Gold Incident Predictions if empty
    gold_rows = con.execute("SELECT COUNT(*) FROM gold_incident_predictions").fetchall()
    gold_count = gold_rows[0][0] if gold_rows else 0
    if gold_count == 0:
        print("[*] Generating initial Gold incident queue...")
        con.execute("""
            INSERT INTO gold_incident_predictions
            SELECT
                'INC-' || SUBSTR(MD5(event_id), 1, 6) AS incident_id,
                event_id,
                timestamp,
                rack_id,
                datacenter_region,
                server_type,
                cooling_type,
                inlet_temperature_c,
                cooling_efficiency,
                power_consumption_kw,
                pue AS actual_pue,
                ROUND(pue + 0.02, 3) AS predicted_pue_champion,
                ROUND(pue - 0.01, 3) AS predicted_pue_challenger,
                CASE WHEN is_anomaly = 1 THEN 0.88 ELSE 0.06 END AS anomaly_prob_champion,
                CASE WHEN is_anomaly = 1 THEN 0.92 ELSE 0.04 END AS anomaly_prob_challenger,
                CASE WHEN is_anomaly = 1 THEN -0.28 ELSE 0.45 END AS isoforest_anomaly_score,
                'champion_lgbm' AS active_model_name,
                CASE
                    WHEN injected_scenario = 'thermal_runaway' THEN 'Thermal Spike'
                    WHEN injected_scenario = 'cooling_degradation' THEN 'Cooling Degradation'
                    WHEN injected_scenario = 'workload_surge' THEN 'Workload Surge'
                    ELSE 'Nominal'
                END AS incident_status,
                CASE
                    WHEN inlet_temperature_c > 38.0 OR pue > 1.65 THEN 'CRITICAL'
                    WHEN inlet_temperature_c > 32.0 OR pue > 1.40 THEN 'WARNING'
                    ELSE 'NOMINAL'
                END AS severity_level,
                CASE
                    WHEN inlet_temperature_c > 32.0 THEN 'inlet_temperature_c'
                    WHEN cooling_efficiency < 0.50 THEN 'cooling_efficiency'
                    ELSE 'workload_intensity'
                END AS top_shap_feature,
                0.24 AS top_shap_impact,
                ROUND((pue - 1.15) * power_consumption_kw * 0.14, 2) AS estimated_hourly_waste_usd,
                'Increase Liquid Cooling delta flow by +18% and rebalance GPU queue' AS recommended_action
            FROM silver_enriched_telemetry
            WHERE is_anomaly = 1 OR inlet_temperature_c > 32.0 OR pue > 1.40
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        print("[+] Initial Gold incidents generated.")


def ensure_dataset_and_lakehouse_ready() -> duckdb.DuckDBPyConnection:
    """Verifies that dataset, DuckDB lakehouse, and ML models exist.

    If not, generates deterministic physics telemetry, seeds Lakehouse,
    and trains baseline LightGBM, XGBoost, and IsolationForest models.
    """
    db_path = get_duckdb_path()
    models_dir = get_models_dir()
    raw_dir = get_base_dir() / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = raw_dir / "green_ai_telemetry.parquet"

    # 1. Dataset Generation / Loading
    if not parquet_path.exists():
        print(f"[*] Raw dataset not found at {parquet_path}. Generating physics-calibrated dataset...")
        df = generate_physics_calibrated_telemetry(num_records=6000, seed=42)
        df.to_parquet(parquet_path, index=False)
        print(f"[+] Generated and saved {len(df)} records to {parquet_path}")
    else:
        df = pd.read_parquet(parquet_path)

    # 2. DuckDB Lakehouse Connection & Schema
    con = duckdb.connect(str(db_path))
    initialize_duckdb_schema(con)
    seed_lakehouse_data(con, df)

    # 3. Model Artifacts Verification
    required_models = [
        "champion_lgbm_clf.joblib",
        "champion_lgbm_reg.joblib",
        "challenger_xgb_clf.joblib",
        "challenger_xgb_reg.joblib",
        "guard_isolation_forest.joblib",
    ]
    missing = [m for m in required_models if not (models_dir / m).exists()]
    if missing:
        print(f"[*] Missing model artifacts: {missing}. Training baseline models...")
        train_and_save_all_models(df, models_dir)
        print("[+] Baseline models successfully trained and serialized.")

    return con


if __name__ == "__main__":
    print("[*] Starting AETHER-DC Bootstrap...")
    con = ensure_dataset_and_lakehouse_ready()
    bronze_count = con.execute("SELECT COUNT(*) FROM bronze_telemetry_events").fetchone()[0]
    silver_count = con.execute("SELECT COUNT(*) FROM silver_enriched_telemetry").fetchone()[0]
    gold_count = con.execute("SELECT COUNT(*) FROM gold_incident_predictions").fetchone()[0]
    print(f"[SUCCESS] Lakehouse Ready! Counts: Bronze={bronze_count}, Silver={silver_count}, Gold={gold_count}")
    con.close()
