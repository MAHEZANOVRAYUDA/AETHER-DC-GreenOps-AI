# 03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification
## Project Name: **AETHER-DC (GreenOps AI)**

---

## 1. Multi-Model Champion vs. Challenger Architecture (`src/mlops/model_registry.py`)

Untuk membuktikan kompetensi **ML Engineer & Data Scientist** tingkat lanjut, sistem tidak hanya menjalankan satu model statis, melainkan mengoperasikan **Tiga Model Paralel (*Shadow Deployment Architecture*)**:

| Peran Model | Algoritma Utama | Tugas Prediksi (Multi-Task) | Keunggulan Operasional |
| :--- | :--- | :--- | :--- |
| **Champion Model (Default Active)** | `LightGBM` (`LGBMClassifier` + `LGBMRegressor`) | 1. Klasifikasi Probabilitas Insiden/Anomali (`anomaly_prob`)<br>2. Regresi Estimasi Nilai `PUE` & Konsumsi Daya | Inferensi sangat cepat (`<5ms`), *memory footprint* rendah, dan akurasi tinggi pada distribusi stasioner (*baseline*). |
| **Challenger Model (Shadow Mode)** | `XGBoost` (`XGBClassifier` + `XGBRegressor` dengan *monotonic constraints* & regularisasi L1/L2 kuat) | Berjalan secara paralel (*shadow*) pada setiap paket *stream* dan dievaluasi pada *sliding window* terbaru | Lebih tangguh saat terjadi *covariate/concept drift* ekstrem akibat degradasi pendingin atau lonjakan beban GPU. |
| **Unsupervised Guardrail** | `IsolationForest` (Scikit-Learn) | Mendeteksi *zero-day out-of-distribution (OOD)* *telemetry spikes* yang belum pernah muncul di data latih | Menangkap anomali struktural baru meskipun label historis belum tersedia. |

### 1.1 Zero-Downtime Hot-Swap & Shadow Evaluation Logic
1. Setiap kali *micro-batch* baru masuk ke lapisan **Silver**, baik **Champion (`LightGBM`)** maupun **Challenger (`XGBoost`)** menghasilkan prediksi secara simultan.
2. Sistem menghitung metrik bergulir (*Rolling Window Evaluation* pada 200 sampel terakhir):
   - **Classification F1-Score & ROC-AUC** (deteksi anomali termal/daya).
   - **Regression RMSE & MAE** (prediksi `PUE`).
3. **Auto-Promotion / Hot-Swap Policy**:
   - Apabila skor **PSI (*Population Stability Index*)** melewati ambang kritis (`PSI >= 0.20`) **DAN** `Challenger F1-Score > Champion F1-Score + 0.015` (atau `Challenger RMSE < Champion RMSE`), sistem menyalakan indikator **Promotion Ready** (dan dapat melakukan *Auto Hot-Swap* otomatis atau lewat 1 klik tombol `Hot-Swap Now` di Bento Card ke-4).
   - Seluruh riwayat pergantian model dicatat di tabel DuckDB `mlops_model_audit_log` (lengkap dengan *timestamp*, alasan *swap*, nilai PSI, delta F1/RMSE, dan *latency*).

---

## 2. Mathematical Specification for Data & Concept Drift (`src/mlops/drift_detector.py`)

### 2.1 Population Stability Index (PSI)
Untuk setiap fitur kunci ($X \in \{	ext{inlet\_temperature\_c}, 	ext{cooling\_efficiency}, 	ext{workload\_intensity}, 	ext{power\_consumption\_kw}, 	ext{pue}\}$), distribusi referensi (*baseline training window* $P$) dibagi menjadi $B = 10$ *decile bins* dan dibandingkan terhadap distribusi *live streaming window* saat ini ($Q$):

$$	ext{PSI}(P, Q) = \sum_{b=1}^{B} \left( Q_b - P_b ight) 	imes \ln\left( rac{Q_b + \epsilon}{P_b + \epsilon} ight)$$

dengan $\epsilon = 10^{-4}$ untuk mencegah pembagian nol.
- **Interpretasi Operasional**:
  - $	ext{PSI} < 0.10$: **Nominal (Stable)** — Distribusi sensor sesuai dengan baseline pelatihan.
  - $0.10 \le 	ext{PSI} < 0.20$: **Moderate Drift (Warning)** — Mulai terjadi pergeseran beban/suhu; pantau metrik *Shadow Challenger*.
  - $	ext{PSI} \ge 0.20$: **Critical Drift (Alert)** — Pergeseran distribusi signifikan; memicu *alert* Prometheus dan merekomendasikan *Hot-Swap* atau *Incremental Retraining*.

### 2.2 Two-Sample Kolmogorov-Smirnov (KS) Test
Selain PSI, sistem menghitung statistik `scipy.stats.ks_2samp(reference_arr, current_arr)` untuk mendapatkan pasangan `(ks_statistic, p_value)`. Fitur dinyatakan mengalami *statistically significant drift* apabila `p_value < 0.01` dan `ks_statistic > 0.15`.

---

## 3. Prometheus Observability & Metrics Exporter (`src/mlops/prometheus_metrics.py`)

Menggunakan pustaka resmi `prometheus_client`, sistem mengekspos metrik berstandar industri pada *endpoint* `GET /metrics` di FastAPI (serta menyediakan pembacaan *in-process* untuk antarmuka Streamlit):

| Nama Metrik Prometheus | Tipe Metrik | Label | Deskripsi |
| :--- | :--- | :--- | :--- |
| `aether_telemetry_events_total` | `Counter` | `region`, `server_type`, `status` (`valid` / `dlq`) | Total paket telemetri yang diproses oleh gerbang Pydantic v2. |
| `aether_facility_pue_gauge` | `Gauge` | `region`, `cooling_type` | Nilai *Power Usage Effectiveness (PUE)* rata-rata terkini per fasilitas. |
| `aether_rack_inlet_temp_celsius` | `Gauge` | `rack_id`, `region` | Suhu *inlet* aktual per rak server (°C). |
| `aether_feature_drift_psi` | `Gauge` | `feature_name` | Nilai *Population Stability Index (PSI)* terkini untuk setiap fitur sensor. |
| `aether_model_inference_latency_ms` | `Histogram` | `model_role` (`champion` / `challenger`) | Distribusi latensi inferensi model dalam milidetik. |
| `aether_model_rolling_f1_score` | `Gauge` | `model_role`, `model_name` | Skor F1 bergulir (*rolling window*) untuk membandingkan Champion vs. Challenger. |
| `aether_model_hotswap_total` | `Counter` | `from_model`, `to_model`, `trigger_reason` | Jumlah kumulatif kejadian *zero-downtime model hot-swap*. |

---

## 4. Agentic SRE Root-Cause Analysis (RCA) & Cooling Optimizer (`src/copilot/sre_rca_agent.py`)

Untuk merepresentasikan keahlian **AI Engineer**, **AETHER-DC** dilengkapi modul **Autonomous SRE Incident Copilot** yang terintegrasi langsung di dalam *Right Detail Inspector Card* (kartu *Periwinkle-Indigo* pada UI Finnova).

### 4.1 Cara Kerja Hibrida (Deterministic SHAP-Physics Engine + Optional LLM API)
1. **Input Konteks Terstruktur**:
   - Mengambil data 1 insiden/rak yang sedang diklik pengguna di daftar kiri (`# INC-1003 · RACK-APAC-04`), meliputi: nilai sensor aktual vs. *rolling mean*, top 3 kontributor **TreeSHAP** lokal, skor `PSI` fitur terkait, perbandingan prediksi `Champion` vs `Challenger`, serta pemborosan biaya (`$/hr`) dan karbon (`kg CO2/hr`).
2. **Structured Output Contract (`Pydantic v2`)**:
   ```python
   class SRERemediationPlan(BaseModel):
       incident_id: str
       rack_id: str
       root_cause_summary: str
       primary_physical_driver: str
       confidence_score: float
       recommended_cooling_action: str
       recommended_workload_action: str
       Recommended_mlops_action: str
       projected_pue_after_action: float
       estimated_hourly_savings_usd: float
       estimated_carbon_reduction_kg: float
   ```
3. **Counterfactual Cooling & Workload Simulation**:
   - Saat pengguna menekan tombol **`Execute Remediation / Promote Challenger`** di kanan bawah kartu detail Finnova, sistem menjalankan simulasi *counterfactual* menggunakan model aktif (misalnya: meningkatkan aliran *Liquid Cooling* sebesar $+18\%$ dan memigrasikan $15\%$ beban GPU *non-urgent* ke klaster `EU`), lalu menampilkan penurunan `PUE` (misalnya dari `1.46` turun ke `1.18`) dan mencatat status insiden menjadi `Remediated` di DuckDB!

---

## 5. Docker Compose & FastAPI Orchestration (`docker-compose.yml`)

```yaml
version: "3.9"

services:
  redpanda:
    image: docker.redpanda.com/redpandadata/redpanda:v24.1.4
    container_name: aether-redpanda
    command:
      - redpanda
      - start
      - --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092
      - --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092
      - --smp 1
      - --memory 512M
      - --overprovisioned
    ports:
      - "19092:19092"
    healthcheck:
      test: ["CMD-SHELL", "rpk cluster health | grep -E 'Healthy:.+true' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  fastapi-mlops:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: aether-fastapi
    environment:
      - REDPANDA_BROKERS=redpanda:9092
      - DUCKDB_PATH=/app/data/lakehouse/aether_dc.duckdb
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
    depends_on:
      - redpanda

  prometheus:
    image: prom/prometheus:v2.53.0
    container_name: aether-prometheus
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    ports:
      - "9090:9090"
    depends_on:
      - fastapi-mlops

  streamlit-dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    container_name: aether-dashboard
    environment:
      - API_BASE_URL=http://fastapi-mlops:8000
      - DUCKDB_PATH=/app/data/lakehouse/aether_dc.duckdb
    volumes:
      - ./data:/app/data
    ports:
      - "8501:8501"
    depends_on:
      - fastapi-mlops
```
