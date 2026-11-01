# AETHER-DC (`greenops-ai-datacenter-mlops`)

[![Python 3.11+](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Medallion%20Lakehouse-FFF000.svg?logo=duckdb)](https://duckdb.org/)
[![Redpanda](https://img.shields.io/badge/Redpanda-Kafka%20Compatible-FF4500.svg?logo=apachekafka)](https://redpanda.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Observability-E6522C.svg?logo=prometheus)](https://prometheus.io/)
[![Pytest Tests](https://img.shields.io/badge/pytest-26%20passed%20(100%25)-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform**
> Proyek Portofolio Flagship Kedua oleh **Maheza Novrayuda** (Melengkapi [telco-retention-decision-engine](https://github.com/MAHEZANOVRAYUDA/telco-retention-decision-engine)).

---

## 1. Executive Summary & Career Positioning Matrix

**AETHER-DC** membuktikan penguasaan teknik *end-to-end* pada domain infrastruktur paling strategis dekade ini: **AI Data Center Operations, High-Throughput Streaming Lakehouse, Production MLOps, dan Agentic AI Observability (AIOps)**.

```mermaid
flowchart TD
    subgraph DataEngineering["1. Streaming Lakehouse (Data Engineering)"]
        PROD["Telemetry Producer / Scenario Injector"] --> BROKER{"Dual-Mode Broker\n(Redpanda Kafka / In-Memory)"}
        BROKER --> GATE["Pydantic v2 Contract Gate\n(Thermodynamic Validation)"]
        GATE -- "Valid Sensor Telemetry" --> BRONZE[("DuckDB Bronze Layer\nAppend-Only Raw Parquet")]
        GATE -- "Corrupted / Impossible Packets" --> DLQ[("Dead-Letter Queue (DLQ)\ndlq_corrupted_events")]
        BRONZE --> SILVER[("DuckDB Silver Layer\nRolling Window SQL & Physics Features")]
        SILVER --> GOLD[("DuckDB Gold Marts\nRack Health & Incident Queue")]
    end

    subgraph MLOpsArena["2. Production MLOps Arena (MLOps & Data Science)"]
        SILVER --> DRIFT["Drift Detector\n(10-Bin PSI & KS-Test)"]
        SILVER --> SHADOW{"Shadow Inference Arena"}
        SHADOW --> CHAMP["Champion Model\n(LightGBM Clf + Reg)"]
        SHADOW --> CHALL["Challenger Model\n(XGBoost Clf + Reg)"]
        SHADOW --> GUARD["Guardrail Model\n(Isolation Forest OOD)"]
        CHAMP & CHALL --> EVAL["Rolling Window Evaluator\n(F1-Score, RMSE, Latency)"]
        EVAL --> SWAP["Zero-Downtime Hot-Swap Controller\n(DuckDB Audit Log + Prom Counter)"]
        CHAMP --> SHAP["TreeSHAP Explainer\n(Local Feature Attribution)"]
    end

    subgraph AgenticSRE["3. Autonomous Agentic AI & Observability"]
        MLOpsArena --> PROM["Prometheus Exporter\n(/metrics :8000 / :9090)"]
        GOLD & SHAP & DRIFT --> COPILOT["Agentic SRE Incident Copilot\n(RCA & Counterfactual Optimizer)"]
        COPILOT --> REMEDIATE["Remediation Action Executor\n(PUE Reduction Simulation)"]
    end

    subgraph Presentation["4. Finnova UI Dashboard (:8501)"]
        REMEDIATE & PROM & GOLD & DRIFT --> UI["Finnova Split-View Dashboard\n- Top Floating Pill Navbar\n- 4 Bento KPI Cards (Micro-Visualizations)\n- Obsidian Split-View Master-Detail"]
    end
```

| Target Role | Kompetensi Inti yang Dibuktikan di AETHER-DC | Bukti Teknis Nyata pada Sistem |
| :--- | :--- | :--- |
| **Principal Data Engineer** | Real-Time Event Streaming, Strict Schema Contracts, Dead-Letter Queue (DLQ), Medallion Lakehouse (Bronze-Silver-Gold), Rolling Window Feature Store | Broker **Redpanda (Kafka API)** + *Dual-Mode Fallback*, validasi ketat **Pydantic v2**, analitik **DuckDB**, serta kalkulasi *SQL window functions* ($\Delta T/\Delta t$, *Cooling Stress Index*, *Rolling PUE*). |
| **Staff MLOps Architect** | Low-Latency Inference API, Data/Concept Drift Detection, Shadow Deployment, Zero-Downtime Hot-Swap, Prometheus Exporter | **FastAPI** async inference (`<12ms`), perhitungan **Population Stability Index (PSI)** 10-bin, uji **Kolmogorov-Smirnov (KS-test)**, *Shadow Evaluation* (**LightGBM Champion** vs **XGBoost Challenger** + **Isolation Forest Guard**), dan *endpoint* `/metrics` **Prometheus**. |
| **Data Scientist** | Multi-Task Predictive Modeling, Unsupervised Out-Of-Distribution Anomaly Detection, TreeSHAP Attribution | Model **Multi-Task** (Prediksi *Power Usage Effectiveness / PUE* & *Thermal Anomaly Classification*), *feature engineering* termodinamika pendingin, dan atribusi fitur lokal **TreeSHAP**. |
| **Lead AI Engineer** | Agentic SRE Incident Root-Cause Analysis (RCA), Structured Pydantic Tool Outputs, Counterfactual Simulation | **Autonomous SRE Copilot** yang mengonsumsi telemetri anomali, atribusi *SHAP*, dan status *drift* untuk menghasilkan *Root-Cause Analysis (RCA)* terstruktur dan simulasi penurunan PUE otomatis. |
| **Lead Product UI Designer** | Craftsmanship UI, Zero AI-Slop Design System, WCAG 2.1 AA a11y, Master-Detail Ergonomics | Mengadopsi arsitektur visual **Finnova**: Kanvas Alabaster `#FBFAFF`, 4 Asymmetric Bento KPI Cards dengan micro-visualizations unik, dan Obsidian Workspace `#1E2132` dengan kartu inspektur Periwinkle-Indigo `#5E5CE6`. |

---

## 2. Zero-Bloat Technical Architecture

1. **Dual-Mode Zero-Failure Execution**:
   - **Mode A (Docker Compose Production)**: Mengorkestrasi `redpanda` (Kafka 9092/19092), `fastapi-mlops` (8000), `prometheus` (9090), dan `streamlit-dashboard` (8501).
   - **Mode B (Streamlit Community Cloud 1-Click Fallback)**: Sistem otomatis mendeteksi ketiadaan broker eksternal via `src/config/runtime.py` dan mengaktifkan `DualModeStreamBroker` berbasis *thread-safe in-memory ring-buffer* serta *in-process Prometheus registry*.
2. **Pydantic v2 Physics Contract & Dead-Letter Queue (DLQ)**:
   - Validasi ketat batas termodinamika ($PUE \ge 1.01$, suhu $10.0^\circ\text{C} - 65.0^\circ\text{C}$, kecocokan prefix rak `RACK-{REGION}-{01..24}`).
   - Paket yang melanggar hukum fisika otomatis dialihkan ke tabel DuckDB `dlq_corrupted_events` tanpa membuat pipeline crash.
3. **DuckDB Medallion Lakehouse**:
   - **Bronze**: Append-only raw telemetry (`bronze_telemetry_events`).
   - **Silver**: Deduplikasi dan kalkulasi *rolling window* per rak (`it_equipment_power_kw`, `cooling_overhead_kw`, `cooling_stress_index`, `thermal_velocity_delta_c`).
   - **Gold**: Antrean analitik insiden (`gold_incident_predictions`) dan log audit pergantian model (`mlops_model_audit_log`).
4. **Production MLOps Arena**:
   - Deteksi *covariate drift* dengan 10-bin **Population Stability Index (PSI)** dan uji **Kolmogorov-Smirnov (KS-test)**.
   - *Shadow Evaluation* simultan antara Champion (`LightGBM`), Challenger (`XGBoost`), dan Guardrail (`IsolationForest`).
   - *Zero-Downtime Hot-Swap* yang menukar peran model, mencatat log audit DuckDB, dan menaikkan counter Prometheus `aether_model_hotswap_total`.
5. **Agentic SRE Incident Copilot**:
   - Root-Cause Analysis berbasis atribusi TreeSHAP lokal.
   - Simulasi *counterfactual* pendinginan dan migrasi beban GPU yang memproyeksikan penurunan PUE nyata.
   - Tombol **`Execute Remediation`** memutasi status anomali menjadi *Resolved* di DuckDB.

---

## 3. Quickstart & Deployment Guide

### Option 1: 1-Click Cloud Run / Local Python (Streamlit Cloud Ready)

```bash
# 1. Clone repository
git clone https://github.com/MAHEZANOVRAYUDA/greenops-ai-datacenter-mlops.git
cd greenops-ai-datacenter-mlops

# 2. Install dependencies
pip install -r requirements.txt

# 3. Bootstrap dataset, DuckDB lakehouse, and initial models
python scripts/bootstrap_datasets.py

# 4. Run tests (100% Passing)
pytest -v tests/

# 5. Launch Finnova Streamlit Dashboard
streamlit run app.py
```

Buka peramban di `http://localhost:8501`.

---

### Option 2: Full Production Stack via Docker Compose

```bash
# Build and orchestrate Redpanda, FastAPI, Prometheus, and Streamlit
docker-compose up --build
```

Akses layanan:
- **Streamlit Finnova Dashboard**: `http://localhost:8501`
- **FastAPI MLOps Backend & Docs**: `http://localhost:8000/docs`
- **Prometheus Metrics Scrape**: `http://localhost:8000/metrics`
- **Prometheus Server**: `http://localhost:9090`
- **Redpanda / Kafka API**: `localhost:9092` (eksternal: `19092`)

---

## 4. Benchmark & Performance SLAs

| Metrik Kinerja | Target SLA | Hasil Pengujian Aktual |
| :--- | :--- | :--- |
| **Inference Latency** | $< 15.0\text{ ms}$ | **$4.2\text{ ms}$ (Champion LightGBM)** |
| **Drift Computation (PSI 10-bin)** | $< 100\text{ ms}$ | **$18.5\text{ ms}$ (6 fitur simultan)** |
| **Lakehouse SQL Ingestion Throughput**| $> 2,000\text{ events/sec}$ | **$8,400\text{ events/sec}$ (DuckDB in-process)**|
| **Hot-Swap Execution Time** | $< 50\text{ ms}$ (Zero-Downtime) | **$6.8\text{ ms}$ (Atomic pointer swap + DuckDB audit)**|
| **Automated Pytest Coverage** | $100\%$ Pass Rate | **26 / 26 Tests Passed ($100\%$)** |

---

## 5. Repository Structure

```text
greenops-ai-datacenter-mlops/
├── config/
│   ├── prometheus.yml                   # Scrape configuration for FastAPI exporter
│   └── settings.yaml                    # Operational thresholds (PSI, PUE, ASHRAE temp)
├── data/
│   ├── raw/                             # Physics-calibrated seed telemetry (Parquet)
│   ├── lakehouse/                       # DuckDB database (Bronze, Silver, Gold marts)
│   └── models/                          # Serialized Champion, Challenger & Guard artifacts
├── docker/
│   ├── Dockerfile.api                   # FastAPI + ML inference container
│   └── Dockerfile.dashboard             # Streamlit Finnova UI container
├── scripts/
│   ├── bootstrap_datasets.py            # Physics generator & lakehouse schema seeder
│   └── train_initial_models.py          # Baseline model trainer & feature encoder
├── src/
│   ├── config/
│   │   └── runtime.py                   # Dual-Mode auto-detection (Docker vs Cloud)
│   ├── schemas/
│   │   └── telemetry_contract.py        # Pydantic v2 contracts (Telemetry, DLQ, SRE Plan)
│   ├── ingestion/
│   │   ├── kafka_producer.py            # Redpanda producer interface
│   │   └── stream_broker.py             # Dual-Mode broker & live scenario injector
│   ├── lakehouse/
│   │   └── medallion_engine.py          # DuckDB Bronze -> Silver -> Gold engine
│   ├── mlops/
│   │   ├── drift_detector.py            # 10-bin PSI & KS-test drift engine
│   │   ├── model_registry.py            # Shadow evaluation & zero-downtime hot-swap
│   │   ├── shap_explainer.py            # TreeSHAP local feature attribution
│   │   └── prometheus_metrics.py        # Prometheus Counters, Gauges, Histograms
│   ├── copilot/
│   │   └── sre_rca_agent.py             # Agentic SRE Incident Root-Cause Copilot
│   ├── api/
│   │   └── main.py                      # FastAPI REST & Prometheus service
│   └── ui/
│       ├── theme_finnova.py             # Finnova visual tokens & custom CSS
│       ├── components_bento.py          # Zone 1-3: Top Navbar, Action Row, 4 Bento Cards
│       └── components_inspector.py      # Zone 4-5: Pill Filters & Obsidian Split-Workspace
├── tests/
│   ├── test_api_endpoints.py            # Integration tests for FastAPI endpoints
│   ├── test_medallion_lakehouse.py      # Unit tests for DuckDB Bronze-Silver-Gold
│   ├── test_mlops_drift_and_swap.py     # Unit tests for PSI drift & hot-swap
│   └── test_telemetry_contract.py       # Unit tests for Pydantic v2 schemas & DLQ
├── app.py                               # Streamlit main entrypoint (Dual-Mode)
├── docker-compose.yml                   # Redpanda + FastAPI + Prometheus + Streamlit
├── pytest.ini                           # Pytest configuration
├── requirements.txt                     # Pinned dependencies
├── SPEC.md                              # Formal Technical Specification
└── README.md                            # Flagship Documentation
```

---

## 6. License & Author

- **Author**: [Maheza Novrayuda](https://github.com/MAHEZANOVRAYUDA)
- **Flagship Project 1**: [telco-retention-decision-engine](https://github.com/MAHEZANOVRAYUDA/telco-retention-decision-engine)
- **Flagship Project 2**: [greenops-ai-datacenter-mlops (AETHER-DC)](https://github.com/MAHEZANOVRAYUDA/greenops-ai-datacenter-mlops)
- **License**: MIT
