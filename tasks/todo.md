# Tasks Checklist: AETHER-DC (GreenOps AI)

- [x] **Task 1: Foundations & Dependencies Scaffold**
  - [x] Buat `requirements.txt` lengkap dan tersemat
  - [x] Buat struktur folder proyek (`config/`, `data/`, `docker/`, `scripts/`, `src/`, `tests/`)
  - [x] Buat `config/settings.yaml` dan `config/prometheus.yml`

- [x] **Task 2: Pydantic v2 Contracts & Deterministic Dataset Bootstrap**
  - [x] Implementasikan `src/schemas/telemetry_contract.py` (`TelemetryEventContract`, `DLQCorruptedEvent`, `SRERemediationPlan`)
  - [x] Implementasikan `src/config/runtime.py` (deteksi Docker Kafka vs Streamlit Cloud In-Memory)
  - [x] Buat `scripts/bootstrap_datasets.py` (Kaggle Green AI Telemetry + NAB/SMD calibrated physics generator)
  - [x] Buat `scripts/train_initial_models.py` (pelatihan awal Champion LGBM, Challenger XGB, Guard IsoForest)
  - [x] Jalankan skrip bootstrap untuk menghasilkan data awal dan model artifact

- [x] **Task 3: Dual-Mode Broker & DuckDB Medallion Lakehouse**
  - [x] Implementasikan `src/ingestion/stream_broker.py` (`DualModeStreamBroker` + scenario injector: Thermal Runaway, Cooling Degradation, Workload Surge, Corrupted DLQ Burst)
  - [x] Implementasikan `src/ingestion/kafka_producer.py`
  - [x] Implementasikan `src/lakehouse/medallion_engine.py` (Bronze, Silver rolling window SQL view, Gold analytical tables)
  - [x] Buat unit tests: `tests/test_telemetry_contract.py` & `tests/test_medallion_lakehouse.py`
  - [x] Verifikasi tests lulus dengan `pytest`

- [x] **Task 4: Production MLOps Engine, Drift Detection, SHAP & Prometheus**
  - [x] Implementasikan `src/mlops/drift_detector.py` (10-bin PSI + KS-test)
  - [x] Implementasikan `src/mlops/model_registry.py` (Shadow evaluation & zero-downtime hot-swap)
  - [x] Implementasikan `src/mlops/shap_explainer.py` (TreeSHAP feature attribution)
  - [x] Implementasikan `src/mlops/prometheus_metrics.py` (Prometheus metric exporter & in-process registry)
  - [x] Buat unit tests: `tests/test_mlops_drift_and_swap.py`
  - [x] Verifikasi tests lulus dengan `pytest`

- [x] **Task 5: Agentic SRE Incident Copilot & FastAPI Backend**
  - [x] Implementasikan `src/copilot/sre_rca_agent.py` (Structured Pydantic RCA & counterfactual optimizer)
  - [x] Implementasikan `src/api/main.py` (FastAPI endpoints: `/health`, `/ingest`, `/predict`, `/drift`, `/swap`, `/remediate`, `/metrics`)
  - [x] Buat integration tests: `tests/test_api_endpoints.py`
  - [x] Verifikasi endpoint FastAPI dengan pytest (5/5 tests passed)

- [x] **Task 6: Finnova UI Design System & Streamlit Dashboard**
  - [x] Implementasikan `src/ui/theme_finnova.py` (CSS injection, Alabaster canvas `#FBFAFF`, hidden sidebar, tokens)
  - [x] Implementasikan `src/ui/components_bento.py` (4 Top Bento KPI Cards dengan micro-visualizations)
  - [x] Implementasikan `src/ui/components_inspector.py` (Obsidian Split-View Master-Detail Workspace `#1E2132` + Periwinkle-Indigo detail card `#5E5CE6`)
  - [x] Implementasikan `app.py` (Entry point Streamlit, state management, filter reactivity, scenario injection triggers, hot-swap handler, remediation handler)
  - [x] Uji jalankan Streamlit dan pastikan semua interaktivitas berjalan mulus tanpa error

- [x] **Task 7: Dockerization, Full Testing & Documentation**
  - [x] Buat `docker/Dockerfile.api` & `docker/Dockerfile.dashboard`
  - [x] Buat `docker-compose.yml` (Redpanda, FastAPI, Prometheus, Streamlit Dashboard)
  - [x] Buat `README.md` komprehensif (Architecture, live demo link, badges, quickstart)
  - [x] Jalankan seluruh test suite `pytest tests/` dan validasi 100% pass (26/26 tests passed)
