# Specification: AETHER-DC (GreenOps AI)
## Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform

---

### 1. Objective & Scope

**AETHER-DC (`greenops-ai-datacenter-mlops`)** adalah sistem produksi *high-impact* yang mendemonstrasikan integrasi end-to-end antara **Real-Time Data Engineering, Production MLOps, Enterprise Observability, dan Agentic AI Engineering** pada infrastruktur operasi komputasi kecerdasan buatan (*AI Data Center Operations & Green Compute / AIOps*).

#### Success Criteria:
1. **Zero-Dummy / Zero-Bloat Execution**: Setiap interaksi UI (filter, dropdown, tombol skenario, tombol Hot-Swap, tombol remediate) memutasi dan membaca state analitik nyata dari DuckDB (`aether_dc.duckdb`) dan MLOps Engine.
2. **Dual-Mode Execution**:
   - **Mode A (Full Docker Compose Stack)**: Redpanda (Kafka-compatible) + FastAPI (`:8000`) + Prometheus (`:9090`) + Streamlit Finnova UI (`:8501`).
   - **Mode B (Zero-Dependency Streamlit Cloud Fallback)**: Menggunakan `DualModeStreamBroker` berbasis in-memory ring-buffer dan in-process Prometheus `CollectorRegistry`, 100% fungsional tanpa runtime error di lingkungan cloud publik.
3. **Pydantic v2 Physics Contract & Dead-Letter Queue (DLQ)**: Memvalidasi integritas data sensor dan termodinamika secara ketat; paket korup dialihkan ke tabel DuckDB `dlq_corrupted_events`.
4. **DuckDB Medallion Architecture**: Pipeline Bronze -> Silver (window functions: thermal velocity dT/dt, cooling stress, rolling PUE/temp) -> Gold analytical marts.
5. **Production MLOps Shadow Arena**:
   - Multi-Task Champion (`LightGBM`) vs Challenger (`XGBoost`) vs Guardrail (`IsolationForest`).
   - 10-bin Population Stability Index (PSI) & Kolmogorov-Smirnov (KS-test) drift detection.
   - Fast TreeSHAP local explainability untuk atribusi anomali.
   - Zero-downtime hot-swap dengan DuckDB audit log dan Prometheus metrics.
6. **Agentic SRE Incident Copilot**: Structured Pydantic RCA output, counterfactual cooling/workload simulation, dan eksekusi remediated state.
7. **Finnova Visual Design System**: Mengadopsi arsitektur visual Finnova secara presisi (kanvas Alabaster `#FBFAFF`, 4 Bento KPI cards dengan micro-visualizations unik, dan Obsidian Split-View Master-Detail Workspace `#1E2132` dengan kartu inspektur Periwinkle-Indigo `#5E5CE6`).

---

### 2. Tech Stack & Execution Commands

| Komponen | Teknologi Terpilih | Versi Teruji |
| :--- | :--- | :--- |
| **Language & Core Runtime** | Python | `>= 3.11, 3.13.2` |
| **Data Validation & Contract** | Pydantic v2 | `>= 2.8` |
| **Analytical Lakehouse** | DuckDB + Apache Parquet | `duckdb >= 1.0.0` |
| **Machine Learning & MLOps** | LightGBM, XGBoost, Scikit-Learn | `lightgbm >= 4.0`, `xgboost >= 2.0`, `scikit-learn >= 1.4` |
| **Explainability** | SHAP (TreeSHAP) | `shap >= 0.44` |
| **Streaming & Messaging** | Redpanda (Kafka API) / In-Memory Deque | `confluent-kafka` / fallback ring-buffer |
| **Backend Inference API** | FastAPI + Uvicorn | `fastapi >= 0.110`, `uvicorn >= 0.28` |
| **Metrics & Observability** | Prometheus Client | `prometheus-client >= 0.20` |
| **Frontend UI / Dashboard** | Streamlit + Custom Finnova CSS | `streamlit >= 1.35` |
| **Testing & Linting** | Pytest, Scipy | `pytest >= 8.0`, `scipy >= 1.12` |

#### Commands:
- **Environment Bootstrap**: `python scripts/bootstrap_datasets.py`
- **Model Training**: `python scripts/train_initial_models.py`
- **Unit & Integration Tests**: `pytest -v tests/`
- **Run FastAPI**: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
- **Run Streamlit Dashboard**: `streamlit run app.py --server.port 8501`
- **Docker Compose Full Stack**: `docker-compose up --build`

---

### 3. Capability Map & Module Boundaries

```
+---------------------------------------------------------------------------------------+
|                                    CAPABILITY MAP                                     |
+---------------------------------------------------------------------------------------+
| 1. schemas: TelemetryEventContract, DLQCorruptedEvent, SRERemediationPlan             |
| 2. config: runtime.py (Dual-Mode Environment & Broker Detection), settings.yaml       |
| 3. bootstrap: Dataset loader (Kaggle Green AI Data Center) + physics synthetic seed   |
| 4. lakehouse: MedallionEngine (DuckDB Bronze, Silver rolling SQL view, Gold marts)     |
| 5. ingestion: DualModeStreamBroker + Interactive Anomaly & Drift Scenario Injector    |
| 6. mlops: DriftDetector (PSI + KS), ModelRegistry (Champion/Challenger/Guard), SHAP   |
| 7. copilot: SRE Incident Copilot (RCA agent + counterfactual cooling optimizer)       |
| 8. api: FastAPI backend (/ingest, /predict, /drift, /swap, /remediate, /metrics)       |
| 9. ui: Finnova UI Design System (Theme, Top Pill, Bento Cards, Obsidian Master-Detail)|
| 10. deployment: Dockerfile.api, Dockerfile.dashboard, docker-compose.yml              |
+---------------------------------------------------------------------------------------+
```

---

### 4. Data Contracts & Physics Constraints (`src/schemas/telemetry_contract.py`)

#### Pydantic v2 Strict Validations:
- `timestamp`: Datetime ISO-8601.
- `rack_id`: Regex `^RACK-(NA|EU|APAC|ME)-\d{2}$`.
- `datacenter_region`: Enum `NA`, `EU`, `APAC`, `ME`.
- `server_type`: Enum `GPU`, `Compute`, `Storage`, `Edge`.
- `cooling_type`: Enum `Liquid`, `Hybrid`, `Air`.
- `workload_intensity`: Float $[0.0, 1.0]$.
- `cpu_utilization`, `memory_utilization`: Float $[0.0, 100.0]$.
- `inlet_temperature_c`: Float $[10.0, 65.0]$ (ASHRAE warning threshold: $>32.0^\circ\text{C}$).
- `cooling_efficiency`: Float $[0.05, 1.0]$.
- `power_consumption_kw`: Float $(0.1, 250.0]$.
- `pue`: Float $[1.01, 3.50]$ ($PUE < 1.0$ melanggar termodinamika).
- `carbon_emission_kg`: Float $\ge 0.0$.
- `compute_cost_usd`: Float $\ge 0.0$.
- `model_validator`: Verifikasi prefix `rack_id` wajib cocok dengan `datacenter_region`.

---

### 5. Medallion Lakehouse Transformation Spec (`src/lakehouse/medallion_engine.py`)

- **Bronze**: Append-only raw validated events (`bronze_telemetry_events`) + DLQ table (`dlq_corrupted_events`).
- **Silver**: Deduplication via `ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY ingested_at DESC)`.
  - Feature Engineering SQL:
    - `it_equipment_power_kw` = `power_consumption_kw / NULLIF(pue, 0)`
    - `cooling_overhead_kw` = `power_consumption_kw - it_equipment_power_kw`
    - `cooling_stress_index` = `power_consumption_kw / (cooling_efficiency + 0.05)`
    - `rolling_temp_mean_short` = `AVG(inlet_temperature_c) OVER w_short` (6 baris)
    - `rolling_temp_std_short` = `STDDEV_POP(inlet_temperature_c) OVER w_short`
    - `thermal_velocity_delta_c` = `inlet_temperature_c - LAG(inlet_temperature_c, 1) OVER (PARTITION BY rack_id ORDER BY timestamp)`
    - `rolling_pue_mean_short` = `AVG(pue) OVER w_short`
- **Gold**:
  - `gold_rack_health_summary`: Status agregat rak terkini, thermal alerts, average PUE.
  - `gold_incident_predictions`: Antrean anomali aktif, perbandingan skor Champion vs Challenger, ISOForest score, top SHAP driver, estimated waste USD, dan remediation status.
  - `mlops_model_audit_log`: Catatan audit pergantian model (hot-swap events).

---

### 6. MLOps Drift & Shadow Architecture Spec

1. **Population Stability Index (PSI)**:
   - 10 decile bins pada baseline training set $P$. Live streaming window $Q$.
   - $\text{PSI} < 0.10$ (Stable), $0.10 \le \text{PSI} < 0.20$ (Moderate), $\text{PSI} \ge 0.20$ (Critical Alert).
2. **Kolmogorov-Smirnov (KS) Test**:
   - Evaluasi distribusi live vs reference (`ks_2samp`), p-value $< 0.01$ and KS stat $> 0.15$.
3. **Multi-Task Models**:
   - **Task 1**: Anomaly Probability Classifier (`anomaly_prob`).
   - **Task 2**: PUE Regression (`predicted_pue`).
   - **Champion**: LightGBM (`models/champion_lgbm_clf.joblib`, `models/champion_lgbm_reg.joblib`).
   - **Challenger**: XGBoost (`models/challenger_xgb_clf.joblib`, `models/challenger_xgb_reg.joblib`).
   - **Guard**: Isolation Forest (`models/guard_isolation_forest.joblib`).
4. **Zero-Downtime Hot-Swap**:
   - Mempromosikan Challenger menjadi Champion secara in-memory, memperbarui konfigurasi aktif, mencatat audit log di DuckDB, dan menaikkan Prometheus counter `aether_model_hotswap_total`.

---

### 7. Finnova UI Visual Specification

1. **Top Floating Pill Navbar**:
   - Kapsul gelap `#161825` di tengah dengan 5 tab: `+ Telemetry Hub`, `Lakehouse & DLQ`, `Drift & MLOps`, `SRE Copilot`, `Prometheus & Infra`.
   - Status indikator runtime: `Docker Kafka` (hijau) atau `Cloud Stream` (ungu/biru).
2. **Zone 2 Action Header**:
   - Judul tebal `30px` + Deskripsi ringkas.
   - Scenario selector: `Thermal Runaway`, `Cooling Degradation`, `Workload Surge`, `Corrupted DLQ Burst`.
   - Tombol ungu `+ Inject Drift / Anomaly`.
3. **Zone 3 Bento KPI Cards (4 Cards)**:
   - **Card 1 (Thermal & DLQ Alerts)**: Total active alerts, rack health bar visualization.
   - **Card 2 (Facility Power & PUE)**: Mean PUE, 7 gradient purple bars (`#5B4FE9` -> `#DFDCFF`).
   - **Card 3 (Feature Drift PSI & Latency)**: Max PSI value, node-line sparkline (`o-o-o`).
   - **Card 4 (Model & Cooling Regime)**: Active model F1/savings, 3 vertical mini-cards (`LGBM`, `XGBoost` highlighted, `IsoForest`), tombol hitam `Hot-Swap Now`.
4. **Zone 4 Filter Bar**:
   - Pill filters: `Active filters [N]`, dropdowns `Region`, `Server Type`, `Cooling Type`, `Severity`, search `Rack / Incident #`.
5. **Zone 5 Obsidian Split-View Master-Detail Workspace**:
   - Kontainer gelap `#1E2132` (radius `28px`).
   - Top-center inverted notch tabs: `All Racks`, `DLQ Alerts`, `Active Incidents`.
   - Panel kiri (38%): Antrean interaktif dengan selected row bersinar dalam kapsul ungu `#5B4FE9`.
   - Panel kanan (62%): Kartu inspektur Periwinkle-Indigo (`linear-gradient(135deg, #5E5CE6 0%, #7B78D8 100%)`) dengan 4 sub-kartu kaca transparan, ringkasan PUE, dan tombol putih `Execute Remediation`.

---

### 8. Verification & Acceptance Criteria

- [x] Unit test `test_telemetry_contract.py`: Memverifikasi validasi Pydantic v2 dan isolasi DLQ untuk data korup.
- [x] Unit test `test_medallion_lakehouse.py`: Memverifikasi pipeline Bronze -> Silver -> Gold di DuckDB.
- [x] Unit test `test_mlops_drift_and_swap.py`: Memverifikasi kalkulasi PSI 10-bin, evaluasi shadow, dan zero-downtime hot-swap.
- [x] End-to-end execution `app.py`: Streamlit dashboard menyala tanpa error baik di mode lokal maupun cloud fallback.
- [x] Docker orchestration: `docker-compose.yml` mengorkestrasikan Redpanda, FastAPI, Prometheus, dan Streamlit secara harmonis.

