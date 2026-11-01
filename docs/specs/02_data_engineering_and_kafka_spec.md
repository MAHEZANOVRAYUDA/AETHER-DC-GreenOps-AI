# 02 — Data Engineering, Streaming Kafka & Medallion Lakehouse Specification
## Project Name: **AETHER-DC (GreenOps AI)**

---

## 1. End-to-End Data Engineering Pipeline Overview

Modul **Data Engineering** pada **AETHER-DC** dirancang untuk memperlihatkan kapabilitas *real-time streaming ingestion*, *strict data quality contracts*, *Dead-Letter Queue (DLQ) isolation*, serta *Medallion Lakehouse Architecture* (**Bronze $ightarrow$ Silver $ightarrow$ Gold**) berbasis **DuckDB + Apache Parquet**.

```
[Telemetry Producer / Drift Injector]
          |
          | (JSON Event Stream via Redpanda Topic: `dc.telemetry.raw` OR In-Memory RingBuffer)
          v
+-------------------------------------------------------------------+
| 1. PYDANTIC V2 SCHEMA & PHYSICS CONTRACT GATE                     |
|    - Checks physical bounds (e.g., 10 <= inlet_temp_c <= 65,      |
|      1.0 <= pue <= 3.5, 0 <= cpu_utilization <= 100)              |
|    - Checks mandatory fields & timestamp monotonicity             |
+-------------------------------------------------------------------+
          |                                           |
     [VALID PACKET]                            [INVALID PACKET]
          |                                           |
          v                                           v
+-----------------------------------+       +-----------------------+
| 2. BRONZE LAYER (Append-Only)     |       | DEAD-LETTER QUEUE     |
|    `bronze_telemetry_events`      |       | `dlq_corrupted_events`|
|    Raw validated JSON + metadata  |       | Error reason, payload,|
+-----------------------------------+       | source rack, timestamp|
          |                                 +-----------------------+
          v
+-------------------------------------------------------------------+
| 3. SILVER LAYER (Enriched & Rolling Window Feature Store)         |
|    `silver_enriched_telemetry`                                    |
|    - Deduplication by `event_id`                                  |
|    - Sliding window features per `rack_id` (5m, 15m, 1h):         |
|      * `rolling_temp_mean_5m`, `rolling_temp_std_5m`              |
|      * `thermal_velocity_c_per_min` (dT/dt)                       |
|      * `cooling_stress_index` = power_kw / (cooling_eff + 0.05)   |
|      * `it_power_kw` = power_consumption_kw / pue                 |
|      * `cooling_overhead_kw` = power_consumption_kw - it_power_kw |
+-------------------------------------------------------------------+
          |
          v
+-------------------------------------------------------------------+
| 4. GOLD LAYER (Business & MLOps Marts)                            |
|    - `gold_rack_health_summary`: Current status per rack & region |
|    - `gold_incident_queue`: Prioritized anomalies + SHAP + RCA    |
|    - `gold_mlops_Window_metrics`: Hourly PSI, F1, MAE, PUE savings|
+-------------------------------------------------------------------+
```

---

## 2. Pydantic v2 Data Contract & Dead-Letter Queue (DLQ) (`src/schemas/telemetry_contract.py`)

Setiap pesan yang masuk dari *stream* wajib melewati validasi struktural dan fisika sebelum diizinkan masuk ke tabel **Bronze**. Jika gagal (misalnya akibat *sensor glitch*, nilai negatif pada daya, atau `pue < 1.0` yang melanggar hukum kekekalan energi), pesan tidak akan menjatuhkan pipeline, melainkan langsung dialihkan ke tabel **Dead-Letter Queue (`dlq_corrupted_events`)**.

```python
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid

class TelemetryEventContract(BaseModel):
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
    def verify_thermodynamic_consistency(self) -> "TelemetryEventContract":
        # Verify region consistency with rack_id prefix
        expected_prefix = f"RACK-{self.datacenter_region}-"
        if not self.rack_id.startswith(expected_prefix):
            raise ValueError(
                f"Region mismatch: rack_id '{self.rack_id}' does not match region '{self.datacenter_region}'"
            )
        return self

class DLQCorruptedEvent(BaseModel):
    dlq_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ingested_at: datetime
    raw_payload: str
    error_type: str
    error_detail: str
    source_topic: str = "dc.telemetry.raw"
```

---

## 3. Dual-Mode Streaming Broker (`src/ingestion/stream_broker.py`)

Agar sistem berjalan mulus baik di lingkungan **Docker Compose (Redpanda/Kafka)** maupun di **Streamlit Community Cloud**, buat kelas abstraksi `DualModeStreamBroker`:

1. **Mode Kafka (`USE_KAFKA=true` / Broker Terdeteksi)**:
   - Menggunakan `confluent-kafka` atau `kafka-python-ng` untuk mempublikasikan dan mengonsumsi *event* dari topik `dc.telemetry.raw` dan `dc.telemetry.dlq` pada **Redpanda (`localhost:9092`)**.
2. **Mode Cloud / Standalone (`USE_KAFKA=false` atau Broker Offline)**:
   - Otomatis beralih ke `collections.deque(maxlen=25000)` yang aman terhadap *thread* (*thread-safe*) dan langsung memproses *micro-batch* dari dataset **[Green AI Data Center Telemetry Dataset](https://www.kaggle.com/datasets/deeplumiere/green-ai-data-center-telemetry-dataset/data)**.
3. **Interactive Scenario Injector (`inject_scenario(mode)`)**:
   - Menyediakan 4 mode injeksi yang dapat dipicu langsung dari tombol CTA di UI:
     - `thermal_runaway`: Menaikkan `inlet_temperature_c` sebesar $+9.5^\circ	ext{C}$ hingga $+16.0^\circ	ext{C}$ dan menurunkan `cooling_efficiency` sebesar $-35\%$ pada rak `GPU` di region `APAC`.
     - `cooling_degradation`: Menurunkan `cooling_efficiency` secara bertahap dan menaikkan `pue` hingga $>1.65$ (memicu *Concept & Covariate Drift* pada fitur utama).
     - `workload_surge`: Melonjakkan `workload_intensity` ke `0.96–1.00`, `cpu_utilization` ke `>95%`, dan `network_throughput_gbps` hingga $3	imes$ lipat.
     - `corrupted_sensor_burst`: Mengirimkan 15 paket dengan `pue = 0.45` (mustahil secara fisik), `cpu_utilization = 145%`, atau `rack_id` salah format untuk mendemonstrasikan penangkapan otomatis oleh **Dead-Letter Queue (DLQ)**.

---

## 4. DuckDB Medallion Lakehouse Specification (`src/lakehouse/medallion_engine.py`)

Gunakan **DuckDB** (`data/lakehouse/aether_dc.duckdb`) sebagai mesin OLAP *in-process* yang mengeksekusi transformasi SQL berkecepatan tinggi di atas tabel relasional dan file **Apache Parquet**:

### 4.1 Bronze Table DDL (`bronze_telemetry_events` & `dlq_corrupted_events`)
```sql
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

CREATE TABLE IF NOT EXISTS dlq_corrupted_events (
    dlq_id VARCHAR PRIMARY KEY,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_payload VARCHAR,
    error_type VARCHAR,
    error_detail VARCHAR,
    source_topic VARCHAR
);
```

### 4.2 Silver Layer Transformation SQL (`silver_enriched_telemetry`)
Transformasi dari **Bronze** ke **Silver** melakukan *deduplication*, mengekstrak fitur fisika termal, dan menghitung *rolling window aggregations* per `rack_id`:

```sql
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
    -- Sliding Window Features per Rack (Last 6 and 12 observations)
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
```

### 4.3 Gold Layer Analytical Marts (`gold_rack_health_summary` & `gold_incident_queue`)
Tabel/View **Gold** menyimpan hasil inferensi model *Champion* dan *Challenger*, skor anomali, status *drift*, serta antrean insiden siap pakai untuk *Split-View Inspector* di UI:

```sql
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
    incident_status VARCHAR,         -- 'Critical Drift', 'Thermal Spike', 'Cooling Degradation', 'Resolved'
    severity_level VARCHAR,          -- 'CRITICAL', 'WARNING', 'NOMINAL'
    top_shap_feature VARCHAR,
    top_shap_impact DOUBLE,
    estimated_hourly_waste_usd DOUBLE,
    recommended_action VARCHAR
);
```
