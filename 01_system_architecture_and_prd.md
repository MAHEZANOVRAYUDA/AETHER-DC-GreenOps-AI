# 01 — System Architecture & Product Requirements Document (PRD)
## Project Name: **AETHER-DC (GreenOps AI)** — Autonomous Green AI Data Center Telemetry, Streaming Lakehouse & Self-Healing MLOps Platform

---

## 1. Executive Summary & Career Positioning Matrix

**AETHER-DC (`greenops-ai-datacenter-mlops`)** adalah proyek portofolio *flagship* kedua milik **Maheza Novrayuda** yang dirancang khusus untuk melengkapi proyek pertama (**[telco-retention-decision-engine](https://github.com/MAHEZANOVRAYUDA/telco-retention-decision-engine)**). Jika proyek pertama menonjolkan *Causal ML & Mathematical Optimization (MILP)* pada data pelanggan tabular, maka **AETHER-DC** membuktikan penguasaan *end-to-end* atas **Real-Time Data Engineering, Production MLOps, Observability, dan Agentic AI Engineering** pada domain infrastruktur paling strategis saat ini: **AI Data Center & Green Compute Operations (AIOps)**.

| Target Role | Kompetensi Inti yang Dibuktikan di AETHER-DC | Bukti Teknis pada Sistem (Verifiable Artifacts) |
| :--- | :--- | :--- |
| **Data Engineer** | Real-Time Event Streaming, Schema Contracts, Dead-Letter Queue (DLQ), Medallion Lakehouse (Bronze-Silver-Gold), Rolling Feature Store | Broker **Redpanda (Kafka-compatible)** + *In-Memory Dual-Mode Replay*, validasi ketat **Pydantic v2**, penyimpanan analitik **DuckDB + Apache Parquet**, dan agregasi *sliding window* (`5m`, `15m`, `1h`). |
| **ML Engineer (MLOps)** | Low-Latency Inference API, Data/Concept Drift Detection, Shadow Deployment, Champion vs. Challenger Hot-Swap, Prometheus Telemetry | **FastAPI** async inference (`<15ms`), perhitungan **Population Stability Index (PSI)** & **KS-Test** *real-time*, *Shadow Evaluation* (**LightGBM Champion** vs **XGBoost Challenger** + **Isolation Forest Guard**), serta *endpoint* `/metrics` **Prometheus**. |
| **Data Scientist** | Multi-Task Predictive Modeling, Unsupervised Anomaly Detection, SHAP Attribution, Physics-Informed Feature Engineering | Model **Multi-Task** (Prediksi *Power Usage Effectiveness / PUE* & *Thermal Spike Anomaly Classification*), *feature engineering* termodinamika server ($\Delta T/\Delta t$, *Cooling Efficiency Ratio*, *Carbon Intensity*), dan *local SHAP explainability*. |
| **AI Engineer** | Agentic SRE Root-Cause Analysis (RCA), Structured Pydantic Tool Outputs, Hybrid Deterministic + LLM Fallback | **Autonomous SRE Incident Copilot** yang mengonsumsi telemetri anomali, atribusi *SHAP*, dan status *drift* Prometheus untuk menghasilkan *Root-Cause Analysis (RCA)* serta rekomendasi remediasi beban pendingin/GPU secara deterministik maupun via LLM API. |

---

## 2. Open-Source Dataset Specification & Provenance

Sistem ini menggunakan **100% dataset open-source** yang dapat diunduh secara otomatis melalui skrip `scripts/bootstrap_datasets.py` (dengan *deterministic physics-calibrated fallback generator* apabila lingkungan *cloud* membatasi unduhan eksternal):

### 2.1 Primary Dataset: Green AI Data Center Telemetry Dataset (Kaggle)
- **Sumber Resmi**: [Green AI Data Center Telemetry Dataset — Kaggle (`deeplumiere/green-ai-data-center-telemetry-dataset`)](https://www.kaggle.com/datasets/deeplumiere/green-ai-data-center-telemetry-dataset/data)
- **Karakteristik**: Merepresentasikan hubungan kausal dan korelasi fisik antara beban komputasi AI/GPU, utilisasi sumber daya, sistem pendingin (*Air, Liquid, Hybrid*), suhu *inlet*, konsumsi daya (kW), biaya operasional (USD/jam), emisi karbon ($	ext{kg CO}_2$), dan **PUE (*Power Usage Effectiveness*)**, lengkap dengan ~5% injeksi anomali realistis (*power spikes*, *extreme PUE*, *high inlet temperature*, *zombie near-idle servers*).

| Nama Kolom (Schema) | Tipe Data | Rentang / Nilai Valid | Deskripsi Fisik & Operasional |
| :--- | :--- | :--- | :--- |
| `event_id` | `VARCHAR (UUID)` | UUIDv4 unik | Identitas unik paket telemetri sensor per *timestamp*. |
| `timestamp` | `TIMESTAMP` | ISO-8601 UTC | Waktu pencatatan sensor (interval *streaming* 5–10 detik). |
| `rack_id` | `VARCHAR` | `RACK-{REGION}-{01..24}` | Identitas rak server fisik di dalam fasilitas *data center*. |
| `datacenter_region` | `VARCHAR` | `NA`, `EU`, `APAC`, `ME` | Wilayah geografis fasilitas *data center* (memengaruhi suhu ambien & faktor emisi grid). |
| `server_type` | `VARCHAR` | `GPU`, `Compute`, `Storage`, `Edge` | Arsitektur node server (`GPU` memiliki TDP & sensitivitas termal tertinggi). |
| `cooling_type` | `VARCHAR` | `Liquid`, `Hybrid`, `Air` | Teknologi pendinginan rak (`Liquid` paling efisien untuk klaster `GPU`). |
| `time_of_day` | `VARCHAR` | `Peak`, `Off-Peak`, `Night` | Siklus beban operasional harian. |
| `workload_intensity` | `DOUBLE` | `0.00` – `1.00` | Intensitas beban kerja komputasi AI/cloud ternormalisasi. |
| `cpu_utilization` | `DOUBLE` | `0.0` – `100.0` (%) | Persentase utilisasi CPU/GPU node. |
| `memory_utilization` | `DOUBLE` | `0.0` – `100.0` (%) | Persentase penggunaan memori VRAM/RAM sistem. |
| `network_throughput_gbps` | `DOUBLE` | `0.1` – `400.0` (Gbps) | Trafik jaringan *interconnect* node. |
| `inlet_temperature_c` | `DOUBLE` | `15.0` – `55.0` (°C) | Suhu udara/cairan masuk ke rak server (ambang kritis ASHRAE: `>32.0°C`). |
| `cooling_efficiency` | `DOUBLE` | `0.10` – `1.00` | Skor efisiensi perpindahan panas unit pendingin (degradasi pompa menurunkan skor ini). |
| `power_consumption_kw` | `DOUBLE` | `0.5` – `120.0` (kW) | Konsumsi daya listrik aktual rak server. |
| `pue` | `DOUBLE` | `1.02` – `2.80` | *Power Usage Effectiveness* ($	ext{Total Facility Power} / 	ext{IT Equipment Power}$). Ideal `< 1.25`. |
| `carbon_emission_kg` | `DOUBLE` | `0.1` – `85.0` (kg/jam) | Estimasi emisi karbon berdasarkan konsumsi kW dan intensitas karbon *grid* regional. |
| `compute_cost_usd` | `DOUBLE` | `0.5` – `250.0` (USD/jam) | Biaya operasional listrik dan komputasi per jam. |
| `energy_efficiency_class` | `VARCHAR` | `High`, `Medium`, `Low` | Label klasifikasi efisiensi energi operasional. |
| `is_anomaly` | `INTEGER` | `0` (Normal), `1` (Anomaly) | Ground-truth / label deteksi insiden (*Thermal Runaway*, *PUE Spike*, *Cooling Degradation*, *Zombie Node*). |

### 2.2 Secondary Benchmark Datasets (Enrichment & Stress-Testing)
1. **[Server Machine Dataset (SMD — OmniAnomaly KDD'19)](https://github.com/NetManAIOps/OmniAnomaly)** ([Mirror Kaggle](https://www.kaggle.com/datasets/mgusat/smd-onmiad)): Digunakan untuk mengkalibrasi pola *multivariate time-series anomaly* (lonjakan CPU/Memory/Network simultan) pada simulator *streaming*.
2. **[Numenta Anomaly Benchmark (NAB) — AWS CloudWatch Server Metrics](https://www.kaggle.com/datasets/boltzmannbrain/nab)** ([GitHub NAB](https://github.com/numenta/NAB)): Digunakan sebagai referensi evaluasi deteksi anomali dini (*early detection window*) dan *concept drift*.

---

## 3. Dual-Mode Deployment Architecture (Docker Compose + Streamlit Cloud)

Agar proyek ini memenuhi standar **Infrastructure/MLOps Engineer** sekaligus mudah diakses oleh **Recruiter non-teknis** dalam 1 klik:

```
+---------------------------------------------------------------------------------------------------+
|                           AETHER-DC DUAL-MODE EXECUTION ARCHITECTURE                              |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [MODE A: FULL PRODUCTION CONTAINER STACK (docker-compose.yml)]                                   |
|   Telemetry Producer ---> Redpanda (Kafka) ---> FastAPI Consumer/Inference ---> Prometheus (:9090)|
|                                |                        |                             |           |
|                                v                        v                             v           |
|                         Pydantic v2 Gate         DuckDB Medallion              Finnova UI Console |
|                         (Valid vs. DLQ)        (Bronze/Silver/Gold)             (Streamlit :8501) |
|                                                                                                   |
|  [MODE B: ZERO-DEPENDENCY CLOUD DEMO MODE (Streamlit Community Cloud Auto-Fallback)]              |
|   In-Memory RingBuffer ---> Pydantic v2 Gate ---> DuckDB Medallion ---> In-Process Prometheus     |
|   Streaming Engine          (Valid vs. DLQ)      (Bronze/Silver/Gold)   CollectorRegistry         |
|                                                         |                                         |
|                                                         v                                         |
|                                       MLOps Engine (PSI Drift + Shadow Eval                       |
|                                       + Hot-Swap + Agentic SRE RCA Copilot)                       |
+---------------------------------------------------------------------------------------------------+
```

1. **Auto-Detection Runtime (`src/config/runtime.py`)**:
   - Saat aplikasi berjalan, sistem memeriksa ketersediaan *broker* Kafka (`REDPANDA_BROKERS=localhost:9092`) dan *server* FastAPI.
   - Jika terhubung (ketika dijalankan via `docker-compose up --build`), UI akan mengonsumsi *stream* langsung dari **Redpanda/Kafka** dan metrik dari **FastAPI/Prometheus**.
   - Jika dijalankan di **Streamlit Community Cloud** (tanpa kontainer eksternal), sistem otomatis mengaktifkan **Embedded Deterministic Streaming Broker** dan **In-Process Prometheus Collector (`prometheus_client.CollectorRegistry`)** tanpa ada satu pun fitur yang mati atau *error*.

---

## 4. Zero-Bloat Feature Matrix (100% Functional, No Dummy Widgets)

Sesuai prinsip *anti-AI-slop*, **setiap komponen di layar memiliki fungsi teknis nyata yang terhubung ke database DuckDB dan MLOps Engine**:

| No | Modul / Fitur pada UI | Fungsi Teknis Nyata di Backend | Mengapa Penting (Zero Bloat) |
| :--- | :--- | :--- | :--- |
| **1** | **Top Pill Navigation Bar (5 View Modes)** | Mengganti fokus kerja antara `Telemetry & Incident Hub`, `Medallion Lakehouse & DLQ`, `Drift & MLOps Arena`, `SRE AI Root-Cause Copilot`, dan `Prometheus & Architecture`. | Menjaga antarmuka tetap bersih seperti aplikasi SaaS modern (Finnova) tanpa *scrolling* panjang yang membingungkan. |
| **2** | **Live Stream & Drift Injection Trigger (`+ Inject Drift / Anomaly`)** | Menyuntikkan skenario nyata ke dalam antrean *stream* (`Thermal Runaway`, `Liquid Cooling Pump Degradation`, `Workload Surge`, atau `Corrupted Sensor Packet`) dan langsung memperbarui metrik PSI, DLQ, serta *alert* insiden. | Memungkinkan rekruter menguji ketahanan pipeline Data Engineering dan reaksi otomatis MLOps secara *hands-on*. |
| **3** | **4 Finnova-Style Bento KPI Cards** | Menampilkan: (1) *Active Thermal/Power Anomalies*, (2) *Facility PUE & Cooling Load Distribution*, (3) *Real-Time PSI Drift & Latency Trajectory*, (4) *Active Champion vs. Challenger Regime Selector* + tombol `Hot-Swap Now`. | Setiap kartu menggabungkan angka metrik utama, *delta* perubahan, dan *micro-visualization* spesifik (bar, sparkline, atau *model regime selector*). |
| **4** | **Global Pill Filter Bar** | Memfilter seluruh query DuckDB secara *real-time* berdasarkan `Datacenter Region`, `Server Type`, `Cooling Type`, `Severity/Status`, dan kata kunci `Rack ID / Incident ID`. | Semua grafik dan daftar insiden di bawahnya langsung berubah secara reaktif sesuai filter yang dipilih. |
| **5** | **Obsidian Split-View Incident & Node Inspector (Master-Detail)** | Panel kiri menampilkan antrean rak/insiden prioritas tinggi (`Active Incidents`, `Drift Warnings`, `DLQ Packets`); panel kanan (kartu *Periwinkle-Indigo*) menampilkan *deep-dive* 1 rak terpilih: atribusi *SHAP*, perbandingan prediksi *Champion vs. Challenger*, dampak biaya/karbon, dan tombol eksekusi remediasi. | Menghindari tabel kaku yang membosankan dan mengadopsi pola *Master-Detail Inspector* dari referensi UI Finnova. |

---

## 5. Repository Directory Structure

```text
greenops-ai-datacenter-mlops/
├── .github/
│   └── workflows/
│       └── ci_mlops_pipeline.yml        # Automated pytest, Ruff lint, schema & model smoke test
├── config/
│   ├── prometheus.yml                   # Scrape configuration for FastAPI & MLOps exporter
│   └── settings.yaml                    # Thresholds: PSI=0.20, ASHRAE temp=32.0C, PUE target=1.25
├── data/
│   ├── raw/                             # Seed CSV/Parquet from Kaggle Green AI Data Center Telemetry
│   ├── lakehouse/                       # DuckDB database + partitioned Bronze/Silver/Gold Parquet files
│   └── models/                          # Serialized Champion (LightGBM), Challenger (XGBoost), IsoForest
├── docker/
│   ├── Dockerfile.api                   # FastAPI + ML inference + Prometheus exporter container
│   ├── Dockerfile.dashboard             # Streamlit Finnova UI container
│   └── Dockerfile.producer              # Kafka/Redpanda telemetry stream producer container
├── scripts/
│   ├── bootstrap_datasets.py            # Downloads/verifies Kaggle dataset & builds deterministic seed
│   └── train_initial_models.py          # Trains & registers baseline Champion/Challenger artifacts
├── src/
│   ├── __init__.py
│   ├── config/
│   │   └── runtime.py                   # Dual-Mode detector (Docker Kafka vs. Cloud In-Memory Broker)
│   ├── schemas/
│   │   └── telemetry_contract.py        # Pydantic v2 strict validation schemas & DLQ error models
│   ├── ingestion/
│   │   ├── kafka_producer.py            # Redpanda/Kafka producer + Drift/Anomaly scenario injector
│   │   └── stream_broker.py             # Dual-mode consumer & ring-buffer manager
│   ├── lakehouse/
│   │   └── medallion_engine.py          # DuckDB Bronze -> Silver (rolling windows) -> Gold aggregations
│   ├── mlops/
│   │   ├── model_registry.py            # Champion vs. Challenger manager & zero-downtime hot-swap
│   │   ├── drift_detector.py            # Population Stability Index (PSI) & KS-Test calculator
│   │   ├── shap_explainer.py            # Fast TreeSHAP local feature attribution engine
│   │   └── prometheus_metrics.py        # Prometheus Counter, Gauge, Histogram exporter
│   ├── copilot/
│   │   └── sre_rca_agent.py             # Agentic SRE Root-Cause Analysis & Cooling Optimizer
│   ├── api/
│   │   └── main.py                      # FastAPI server (/ingest, /predict, /drift, /swap, /metrics)
│   └── ui/
│       ├── theme_finnova.py             # Custom CSS & HTML component builders matching Finnova UI
│       ├── components_bento.py          # 4 Top Bento KPI Cards & Pill Navigation renderers
│       └── components_inspector.py      # Bottom Obsidian Split-View Master-Detail Inspector
├── tests/
│   ├── test_telemetry_contract.py       # Unit tests for Pydantic v2 schema & DLQ routing
│   ├── test_medallion_lakehouse.py      # Unit tests for Bronze-Silver-Gold DuckDB transformations
│   └── test_mlops_drift_and_swap.py     # Unit tests for PSI calculation & Champion/Challenger swap
├── app.py                               # Main Streamlit entry point (runs in both Docker & Cloud modes)
├── docker-compose.yml                   # Redpanda + FastAPI + Prometheus + Streamlit orchestration
├── requirements.txt                     # Pinned dependencies for Streamlit Cloud & Docker
└── README.md                            # Architecture badges, live demo link, quickstart & benchmarks
```
