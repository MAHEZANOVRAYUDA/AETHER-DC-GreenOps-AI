# Graph Report - AETHER-DC (GreenOps AI)  (2026-11-01)

## Corpus Check
- 30 files · ~98,615 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 375 nodes · 564 edges · 23 communities (20 shown, 3 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9039e737`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- bootstrap_datasets.py
- post
- prepare_training_features
- TelemetryEventContract
- app.py
- ._get_connection
- get
- Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform
- test_mlops_drift_and_swap.py
- 03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification
- test_api_endpoints.py
- theme_finnova.py
- FastTreeSHAPExplainer
- 01 — System Architecture & Product Requirements Document (PRD)
- 02 — Data Engineering, Streaming Kafka & Medallion Lakehouse Specification
- 04 — UI Design System & Dashboard Specification (Finnova Visual Architecture)
- AETHER-DC (`greenops-ai-datacenter-mlops`)
- components_bento.py
- .inject_scenario
- Architecture & Remediation Phases
- .publish_event
- __init__.py
- todo.md

## God Nodes (most connected - your core abstractions)
1. `MedallionEngine` - 27 edges
2. `MLOpsModelRegistry` - 17 edges
3. `PrometheusMetricsManager` - 17 edges
4. `ensure_dataset_and_lakehouse_ready()` - 14 edges
5. `DualModeStreamBroker` - 12 edges
6. `init_system_resources()` - 11 edges
7. `TelemetryEventContract` - 11 edges
8. `get_models_dir()` - 10 edges
9. `MultiFeatureDriftDetector` - 10 edges
10. `prepare_training_features()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `init_system_resources()` --uses--> `AgenticSREIncidentCopilot`  [INFERRED]
  app.py → src/copilot/sre_rca_agent.py
- `init_system_resources()` --uses--> `DualModeStreamBroker`  [INFERRED]
  app.py → src/ingestion/stream_broker.py
- `init_system_resources()` --uses--> `MedallionEngine`  [INFERRED]
  app.py → src/lakehouse/medallion_engine.py
- `init_system_resources()` --uses--> `PrometheusMetricsManager`  [INFERRED]
  app.py → src/mlops/prometheus_metrics.py
- `temp_lakehouse()` --uses--> `MedallionEngine`  [INFERRED]
  tests/test_medallion_lakehouse.py → src/lakehouse/medallion_engine.py

## Import Cycles
- None detected.

## Communities (23 total, 3 thin omitted)

### Community 0 - "bootstrap_datasets.py"
Cohesion: 0.08
Nodes (34): fixture, ensure_dataset_and_lakehouse_ready(), generate_physics_calibrated_telemetry(), initialize_duckdb_schema(), DataFrame, DuckDBPyConnection, Dataset Bootstrap & Physics-Calibrated Lakehouse Seeder for AETHER-DC. Based on…, Creates Bronze, DLQ, Silver View, and Gold Analytical tables in DuckDB. (+26 more)

### Community 1 - "post"
Cohesion: 0.15
Nodes (16): post, execute_hotswap(), ingest_telemetry(), inject_scenario(), predict_shadow(), Any, BaseModel, Ingests a telemetry packet through Pydantic v2 contract gate. (+8 more)

### Community 2 - "prepare_training_features"
Cohesion: 0.13
Nodes (14): prepare_training_features(), DataFrame, Path, Initial Model Training & Serialization Script for AETHER-DC. Trains: 1.…, Prepares feature matrix and targets with physics features & label encodings., Trains Champion (LGBM), Challenger (XGBoost), and Guardrail (IsoForest)., train_and_save_all_models(), Series (+6 more)

### Community 3 - "TelemetryEventContract"
Cohesion: 0.07
Nodes (34): model_validator, parametrize, AgenticSREIncidentCopilot, Any, Agentic SRE Incident Copilot & Counterfactual Cooling Optimizer for AETHER-DC.…, Autonomous SRE Incident Copilot for Green Data Center Operations., Analyzes an active data center incident using SHAP attributions and…, DLQCorruptedEvent (+26 more)

### Community 4 - "app.py"
Cohesion: 0.05
Nodes (42): get_cached_drift(), get_cached_eval(), get_cached_kpis(), get_cached_silver(), AETHER-DC (GreenOps AI) — Main Streamlit Application Entrypoint. Autonomous…, cache_data, Enum, FastAPI (+34 more)

### Community 5 - "._get_connection"
Cohesion: 0.11
Nodes (13): Any, DataFrame, DuckDBPyConnection, Ingests a batch of raw telemetry events, returning (valid_count, dlq_count)., Retrieves enriched silver layer features with rolling windows., Retrieves filtered incident predictions queue for Finnova Master-Detail view., Retrieves Dead-Letter Queue corrupted events., Calculates reactive KPIs for the 4 Finnova Bento Cards. (+5 more)

### Community 6 - "get"
Cohesion: 0.29
Nodes (7): get, get_drift_metrics(), list_incidents(), prometheus_metrics(), Calculates live Population Stability Index (PSI) and KS-test metrics., Returns filtered active incidents queue., Prometheus scraping endpoint.

### Community 7 - "Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform"
Cohesion: 0.14
Nodes (13): 1. Objective & Scope, 2. Tech Stack & Execution Commands, 3. Capability Map & Module Boundaries, 4. Data Contracts & Physics Constraints (`src/schemas/telemetry_contract.py`), 5. Medallion Lakehouse Transformation Spec (`src/lakehouse/medallion_engine.py`), 6. MLOps Drift & Shadow Architecture Spec, 7. Finnova UI Visual Specification, 8. Verification & Acceptance Criteria (+5 more)

### Community 9 - "test_mlops_drift_and_swap.py"
Cohesion: 0.07
Nodes (34): init_system_resources(), cache_resource, CollectorRegistry, ndarray, calculate_ks_drift(), calculate_psi(), MultiFeatureDriftDetector, Any (+26 more)

### Community 13 - "03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification"
Cohesion: 0.17
Nodes (11): 03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification, 1.1 Zero-Downtime Hot-Swap & Shadow Evaluation Logic, 1. Multi-Model Champion vs. Challenger Architecture (`src/mlops/model_registry.py`), 2.1 Population Stability Index (PSI), 2.2 Two-Sample Kolmogorov-Smirnov (KS) Test, 2. Mathematical Specification for Data & Concept Drift (`src/mlops/drift_detector.py`), 3. Prometheus Observability & Metrics Exporter (`src/mlops/prometheus_metrics.py`), 4.1 Cara Kerja Hibrida (Deterministic SHAP-Physics Engine + Optional LLM API) (+3 more)

### Community 14 - "test_api_endpoints.py"
Cohesion: 0.17
Nodes (11): Integration Tests for FastAPI Backend Endpoints., GET /health returns healthy status and metadata., POST /predict runs shadow prediction across all models., GET /drift returns PSI and KS metrics., POST /inject triggers scenario injection., GET /metrics returns text-formatted Prometheus metrics., test_api_drift_metrics(), test_api_healthcheck() (+3 more)

### Community 15 - "theme_finnova.py"
Cohesion: 0.50
Nodes (3): inject_finnova_theme(), Finnova UI Theme & Custom CSS Generator for AETHER-DC. Translates Finnova…, Injects custom Finnova styling into Streamlit application using native st.html.

### Community 17 - "FastTreeSHAPExplainer"
Cohesion: 0.27
Nodes (7): FastTreeSHAPExplainer, Any, DataFrame, Fast TreeSHAP explainer for LightGBM and XGBoost models., Initializes shap.TreeExplainer with tree model., Calculates SHAP attribution values for a single telemetry record. Returns list…, Physics-informed attribution heuristic if model explainer is unavailable.

### Community 18 - "01 — System Architecture & Product Requirements Document (PRD)"
Cohesion: 0.20
Nodes (9): 01 — System Architecture & Product Requirements Document (PRD), 1. Executive Summary & Career Positioning Matrix, 2.1 Primary Dataset: Green AI Data Center Telemetry Dataset (Kaggle), 2.2 Secondary Benchmark Datasets (Enrichment & Stress-Testing), 2. Open-Source Dataset Specification & Provenance, 3. Dual-Mode Deployment Architecture (Docker Compose + Streamlit Cloud), 4. Zero-Bloat Feature Matrix (100% Functional, No Dummy Widgets), 5. Repository Directory Structure (+1 more)

### Community 19 - "02 — Data Engineering, Streaming Kafka & Medallion Lakehouse Specification"
Cohesion: 0.20
Nodes (9): 02 — Data Engineering, Streaming Kafka & Medallion Lakehouse Specification, 1. End-to-End Data Engineering Pipeline Overview, 2. Pydantic v2 Data Contract & Dead-Letter Queue (DLQ) (`src/schemas/telemetry_contract.py`), 3. Dual-Mode Streaming Broker (`src/ingestion/stream_broker.py`), 4.1 Bronze Table DDL (`bronze_telemetry_events` & `dlq_corrupted_events`), 4.2 Silver Layer Transformation SQL (`silver_enriched_telemetry`), 4.3 Gold Layer Analytical Marts (`gold_rack_health_summary` & `gold_incident_queue`), 4. DuckDB Medallion Lakehouse Specification (`src/lakehouse/medallion_engine.py`) (+1 more)

### Community 20 - "04 — UI Design System & Dashboard Specification (Finnova Visual Architecture)"
Cohesion: 0.20
Nodes (9): 04 — UI Design System & Dashboard Specification (Finnova Visual Architecture), 1. Visual Deconstruction of the Finnova Reference UI (Anti-AI-Slop Mandate), 2.1 Color Palette Tokens (CSS Custom Properties), 2.2 Typography Scale, 2. Exact Color Tokens & Typography Extracted from Reference, 3. Zone-by-Zone Layout Mapping (Finnova $, Detail Spesifik 4 Kartu Bento (Zone 3):, Detail Spesifik Obsidian Split-View Master-Detail (Zone 5): (+1 more)

### Community 21 - "AETHER-DC (`greenops-ai-datacenter-mlops`)"
Cohesion: 0.20
Nodes (9): 1. Executive Summary & Career Positioning Matrix, 2. Zero-Bloat Technical Architecture, 3. Quickstart & Deployment Guide, 4. Benchmark & Performance SLAs, 5. Repository Structure, 6. License & Author, AETHER-DC (`greenops-ai-datacenter-mlops`), Option 1: 1-Click Cloud Run / Local Python (Streamlit Cloud Ready) (+1 more)

### Community 22 - "components_bento.py"
Cohesion: 0.18
Nodes (10): Any, Finnova Top Navigation, Action Header & 4 Asymmetric Bento KPI Cards.…, Renders Zone 1 Left: Brand Logo, Name, Badge, and Counter Pill., Renders Zone 1 Right: Icon Cluster, Status Chips, and User Avatar., Renders Zone 2: Action Header Row (Title, Subtitle, and Back Button)., Renders Zone 3: 4 Asymmetric Bento KPI Cards with micro-visualizations., render_action_header(), render_bento_kpi_cards() (+2 more)

### Community 24 - ".inject_scenario"
Cohesion: 0.33
Nodes (4): Any, Publishes event to Kafka (if active) and ingests into DuckDB Lakehouse &…, Returns the most recent events from ring buffer or silver layer., Injects live real-time scenarios into the data pipeline.

### Community 26 - "Architecture & Remediation Phases"
Cohesion: 0.25
Nodes (7): Architecture & Remediation Phases, Comprehensive Remediation Plan: AETHER-DC (GreenOps AI) Overhaul, Phase 1: Zero Code Exposure & HTML Parsing Fix (Vital / Critical), Phase 2: Pixel-Accurate Finnova UI Overhaul vs `desain ui.jpg` (Heavy / Critical), Phase 3: Web Performance Optimization & Memoization (Heavy / `/webperf`), Phase 4: Data Engineering, MLOps & DevSecOps Hardening (Moderate), Phase 5: Verification & Quality Assurance

## Knowledge Gaps
- **48 isolated node(s):** `Project Name: **AETHER-DC (GreenOps AI)** — Autonomous Green AI Data Center Telemetry, Streaming Lakehouse & Self-Healing MLOps Platform`, `1. Executive Summary & Career Positioning Matrix`, `2.1 Primary Dataset: Green AI Data Center Telemetry Dataset (Kaggle)`, `2.2 Secondary Benchmark Datasets (Enrichment & Stress-Testing)`, `3. Dual-Mode Deployment Architecture (Docker Compose + Streamlit Cloud)` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 196 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MedallionEngine` connect `app.py` to `bootstrap_datasets.py`, `test_mlops_drift_and_swap.py`, `TelemetryEventContract`, `._get_connection`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `PrometheusMetricsManager` connect `app.py` to `test_mlops_drift_and_swap.py`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `MLOpsModelRegistry` connect `test_mlops_drift_and_swap.py` to `prepare_training_features`, `app.py`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `MedallionEngine` (e.g. with `init_system_resources()` and `DualModeStreamBroker`) actually correct?**
  _`MedallionEngine` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MLOpsModelRegistry` (e.g. with `init_system_resources()` and `MedallionEngine`) actually correct?**
  _`MLOpsModelRegistry` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `PrometheusMetricsManager` (e.g. with `init_system_resources()` and `MLOpsModelRegistry`) actually correct?**
  _`PrometheusMetricsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `DualModeStreamBroker` (e.g. with `init_system_resources()` and `RuntimeMode`) actually correct?**
  _`DualModeStreamBroker` has 4 INFERRED edges - model-reasoned connections that need verification._