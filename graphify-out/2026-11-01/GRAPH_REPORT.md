# Graph Report - AETHER-DC (GreenOps AI)  (2026-11-01)

## Corpus Check
- 30 files · ~26,524 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 365 nodes · 550 edges · 30 communities (27 shown, 3 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9039e737`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- runtime.py
- main.py
- prepare_training_features
- TelemetryEventContract
- MedallionEngine
- ._get_connection
- PrometheusMetricsManager
- Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform
- AgenticSREIncidentCopilot
- test_mlops_drift_and_swap.py
- test_medallion_lakehouse.py
- drift_detector.py
- medallion_engine.py
- 03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification
- test_api_endpoints.py
- app.py
- MultiFeatureDriftDetector
- FastTreeSHAPExplainer
- 01 — System Architecture & Product Requirements Document (PRD)
- 02 — Data Engineering, Streaming Kafka & Medallion Lakehouse Specification
- 04 — UI Design System & Dashboard Specification (Finnova Visual Architecture)
- AETHER-DC (`greenops-ai-datacenter-mlops`)
- components_bento.py
- .__init__
- .inject_scenario
- .ingest_event
- Implementation Plan: AETHER-DC (GreenOps AI) — COMPLETED
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
- `init_system_resources()` --uses--> `MultiFeatureDriftDetector`  [INFERRED]
  app.py → src/mlops/drift_detector.py
- `init_system_resources()` --uses--> `PrometheusMetricsManager`  [INFERRED]
  app.py → src/mlops/prometheus_metrics.py

## Import Cycles
- None detected.

## Communities (30 total, 3 thin omitted)

### Community 0 - "runtime.py"
Cohesion: 0.10
Nodes (30): Enum, ensure_dataset_and_lakehouse_ready(), generate_physics_calibrated_telemetry(), initialize_duckdb_schema(), DataFrame, DuckDBPyConnection, Dataset Bootstrap & Physics-Calibrated Lakehouse Seeder for AETHER-DC. Based on…, Creates Bronze, DLQ, Silver View, and Gold Analytical tables in DuckDB. (+22 more)

### Community 1 - "main.py"
Cohesion: 0.10
Nodes (28): FastAPI, get, post, execute_hotswap(), get_drift_metrics(), healthcheck(), ingest_telemetry(), inject_scenario() (+20 more)

### Community 2 - "prepare_training_features"
Cohesion: 0.13
Nodes (14): prepare_training_features(), DataFrame, Path, Initial Model Training & Serialization Script for AETHER-DC. Trains: 1.…, Prepares feature matrix and targets with physics features & label encodings., Trains Champion (LGBM), Challenger (XGBoost), and Guardrail (IsoForest)., train_and_save_all_models(), Series (+6 more)

### Community 3 - "TelemetryEventContract"
Cohesion: 0.15
Nodes (14): model_validator, parametrize, Strict schema contract for data center telemetry events., Verify regional prefix and thermodynamic consistency., TelemetryEventContract, Unit Tests for Pydantic v2 Telemetry Contract & DLQ Routing., DLQ model stores error details without crashing., Valid contract should instantiate cleanly without error. (+6 more)

### Community 4 - "MedallionEngine"
Cohesion: 0.17
Nodes (10): KafkaTelemetryProducer, Redpanda / Kafka Producer Interface for AETHER-DC. Publishes telemetry events…, Kafka/Redpanda Producer wrapper with fallback handling., Attempts to initialize confluent_kafka Producer., Flushes remaining messages in buffer., DualModeStreamBroker, Dual-Mode Streaming Broker & Interactive Scenario Injector for AETHER-DC.…, Manages telemetry event streaming, ring-buffering, and live anomaly injection. (+2 more)

### Community 5 - "._get_connection"
Cohesion: 0.15
Nodes (9): DataFrame, DuckDBPyConnection, Retrieves enriched silver layer features with rolling windows., Retrieves filtered incident predictions queue for Finnova Master-Detail view., Retrieves Dead-Letter Queue corrupted events., Executes counterfactual SRE remediation on an active incident., Returns a DuckDB connection., Records a Zero-Downtime Model Hot-Swap in the audit log. (+1 more)

### Community 6 - "PrometheusMetricsManager"
Cohesion: 0.12
Nodes (9): PrometheusMetricsManager, Updates facility PUE gauge., Updates rack inlet temperature gauge., Updates PSI gauge for a specific feature., Updates rolling F1-score gauge., Increments model hot-swap counter., Serializes current metrics in Prometheus text format., Manages Prometheus telemetry collectors with in-process and external support. (+1 more)

### Community 7 - "Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform"
Cohesion: 0.14
Nodes (13): 1. Objective & Scope, 2. Tech Stack & Execution Commands, 3. Capability Map & Module Boundaries, 4. Data Contracts & Physics Constraints (`src/schemas/telemetry_contract.py`), 5. Medallion Lakehouse Transformation Spec (`src/lakehouse/medallion_engine.py`), 6. MLOps Drift & Shadow Architecture Spec, 7. Finnova UI Visual Specification, 8. Verification & Acceptance Criteria (+5 more)

### Community 8 - "AgenticSREIncidentCopilot"
Cohesion: 0.14
Nodes (11): AgenticSREIncidentCopilot, Any, Autonomous SRE Incident Copilot for Green Data Center Operations., Analyzes an active data center incident using SHAP attributions and…, Any, DataFrame, Finnova Filter Bar & Obsidian Split-View Master-Detail Workspace. Implements: -…, Renders Zone 4: Horizontal Pill Filter Bar. (+3 more)

### Community 9 - "test_mlops_drift_and_swap.py"
Cohesion: 0.24
Nodes (11): init_system_resources(), cache_resource, MLOpsModelRegistry, Production Model Registry managing Champion, Challenger, and Guardrail models., Unit Tests for MLOps Engine: 10-bin PSI Drift, Shadow Evaluation & Hot-Swap., Hot-swap atomically swaps Champion and Challenger roles., TreeSHAP explainer attributes incident to key thermodynamic drivers., Model registry runs shadow evaluation on Champion, Challenger, and Guard. (+3 more)

### Community 10 - "test_medallion_lakehouse.py"
Cohesion: 0.15
Nodes (12): fixture, Unit Tests for DuckDB Medallion Lakehouse Engine (Bronze -> Silver -> Gold)., Recording hot-swap inserts a record in mlops_model_audit_log., Provides a fresh temporary DuckDB lakehouse instance., Valid event routes cleanly to bronze_telemetry_events., Corrupted event (violating physics) routes to dlq_corrupted_events., Incident remediation updates status to Resolved and sets new target PUE., temp_lakehouse() (+4 more)

### Community 11 - "drift_detector.py"
Cohesion: 0.17
Nodes (12): ndarray, calculate_ks_drift(), calculate_psi(), Population Stability Index (PSI) & Kolmogorov-Smirnov (KS) Drift Detector.…, Calculates Population Stability Index (PSI) across decile bins. PSI = SUM (…, Calculates 2-sample Kolmogorov-Smirnov statistic & drift hypothesis. Returns:…, Identical distributions should have PSI close to zero (< 0.05)., Significantly shifted distribution should trigger critical drift (PSI >= 0.20). (+4 more)

### Community 12 - "medallion_engine.py"
Cohesion: 0.19
Nodes (10): Agentic SRE Incident Copilot & Counterfactual Cooling Optimizer for AETHER-DC.…, DuckDB Medallion Lakehouse Engine for AETHER-DC. Orchestrates: 1. Bronze Layer:…, DLQCorruptedEvent, BaseModel, Pydantic v2 Telemetry Contract, Dead-Letter Queue (DLQ) & SRE Remediation…, Schema for routing malformed or physically impossible packets into Dead-Letter…, Structured Pydantic contract for Agentic SRE RCA and Counterfactual…, SRERemediationPlan (+2 more)

### Community 13 - "03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification"
Cohesion: 0.17
Nodes (11): 03 — Production MLOps, Drift Detection, Prometheus & Agentic SRE Specification, 1.1 Zero-Downtime Hot-Swap & Shadow Evaluation Logic, 1. Multi-Model Champion vs. Challenger Architecture (`src/mlops/model_registry.py`), 2.1 Population Stability Index (PSI), 2.2 Two-Sample Kolmogorov-Smirnov (KS) Test, 2. Mathematical Specification for Data & Concept Drift (`src/mlops/drift_detector.py`), 3. Prometheus Observability & Metrics Exporter (`src/mlops/prometheus_metrics.py`), 4.1 Cara Kerja Hibrida (Deterministic SHAP-Physics Engine + Optional LLM API) (+3 more)

### Community 14 - "test_api_endpoints.py"
Cohesion: 0.17
Nodes (11): Integration Tests for FastAPI Backend Endpoints., GET /health returns healthy status and metadata., POST /predict runs shadow prediction across all models., GET /drift returns PSI and KS metrics., POST /inject triggers scenario injection., GET /metrics returns text-formatted Prometheus metrics., test_api_drift_metrics(), test_api_healthcheck() (+3 more)

### Community 15 - "app.py"
Cohesion: 0.22
Nodes (6): AETHER-DC (GreenOps AI) — Main Streamlit Application Entrypoint. Autonomous…, Multi-Model Champion vs Challenger Registry & Zero-Downtime Hot-Swap…, Prometheus Observability & Metrics Exporter for AETHER-DC. Exposes industry-…, inject_finnova_theme(), Finnova UI Theme & Custom CSS Generator for AETHER-DC. Translates Finnova…, Injects custom Finnova styling into Streamlit application.

### Community 16 - "MultiFeatureDriftDetector"
Cohesion: 0.22
Nodes (8): MultiFeatureDriftDetector, Any, DataFrame, Calculates PSI and KS-test statistics for all key monitored features., Monitors telemetry feature drifts against baseline reference distribution., Loads serialized baseline feature reference if present., Detector computes per-feature PSI and overall alert status., test_multi_feature_drift_detector()

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
Cohesion: 0.22
Nodes (8): Any, Finnova Top Navigation, Action Header & 4 Asymmetric Bento KPI Cards.…, Renders Zone 1: Brand & Status Header., Renders Zone 2: Action Header Row., Renders Zone 3: 4 Asymmetric Bento KPI Cards with micro-visualizations., render_action_header(), render_bento_kpi_cards(), render_top_navbar()

### Community 23 - ".__init__"
Cohesion: 0.25
Nodes (4): CollectorRegistry, Path, Loads serialized models from disk., Singleton getter for PrometheusMetricsManager.

### Community 24 - ".inject_scenario"
Cohesion: 0.33
Nodes (4): Any, Publishes event to Kafka (if active) and ingests into DuckDB Lakehouse &…, Returns the most recent events from ring buffer or silver layer., Injects live real-time scenarios into the data pipeline.

### Community 25 - ".ingest_event"
Cohesion: 0.33
Nodes (4): Any, Ingests a batch of raw telemetry events, returning (valid_count, dlq_count)., Calculates reactive KPIs for the 4 Finnova Bento Cards., Ingests a single raw telemetry event via Pydantic v2 contract gate. - If…

### Community 26 - "Implementation Plan: AETHER-DC (GreenOps AI) — COMPLETED"
Cohesion: 0.40
Nodes (4): Architectural Dependency Graph, Implementation Plan: AETHER-DC (GreenOps AI) — COMPLETED, System Overview, Verification Status Summary

## Knowledge Gaps
- **46 isolated node(s):** `Project Name: **AETHER-DC (GreenOps AI)** — Autonomous Green AI Data Center Telemetry, Streaming Lakehouse & Self-Healing MLOps Platform`, `1. Executive Summary & Career Positioning Matrix`, `2.1 Primary Dataset: Green AI Data Center Telemetry Dataset (Kaggle)`, `2.2 Secondary Benchmark Datasets (Enrichment & Stress-Testing)`, `3. Dual-Mode Deployment Architecture (Docker Compose + Streamlit Cloud)` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 193 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MedallionEngine` connect `MedallionEngine` to `runtime.py`, `main.py`, `TelemetryEventContract`, `._get_connection`, `test_mlops_drift_and_swap.py`, `test_medallion_lakehouse.py`, `medallion_engine.py`, `app.py`, `.__init__`, `.ingest_event`?**
  _High betweenness centrality (0.183) - this node is a cross-community bridge._
- **Why does `PrometheusMetricsManager` connect `PrometheusMetricsManager` to `test_mlops_drift_and_swap.py`, `.__init__`, `main.py`, `app.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `MLOpsModelRegistry` connect `test_mlops_drift_and_swap.py` to `main.py`, `prepare_training_features`, `MedallionEngine`, `PrometheusMetricsManager`, `app.py`, `.__init__`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `MedallionEngine` (e.g. with `init_system_resources()` and `DualModeStreamBroker`) actually correct?**
  _`MedallionEngine` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MLOpsModelRegistry` (e.g. with `init_system_resources()` and `MedallionEngine`) actually correct?**
  _`MLOpsModelRegistry` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `PrometheusMetricsManager` (e.g. with `init_system_resources()` and `MLOpsModelRegistry`) actually correct?**
  _`PrometheusMetricsManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `DualModeStreamBroker` (e.g. with `init_system_resources()` and `RuntimeMode`) actually correct?**
  _`DualModeStreamBroker` has 4 INFERRED edges - model-reasoned connections that need verification._