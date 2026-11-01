"""FastAPI MLOps & Data Center Observability Service for AETHER-DC.

Exposes REST and Prometheus endpoints:
- GET  /health     : Healthcheck & lakehouse event counters
- POST /ingest     : Pydantic v2 contract gate ingestion into Bronze/DLQ
- POST /predict    : Shadow evaluation inference (Champion, Challenger, Guard)
- GET  /drift      : 10-bin PSI & KS-test drift metrics
- POST /swap       : Zero-downtime hot-swap between Champion & Challenger
- POST /remediate  : Execute SRE RCA & remediation action on incident
- POST /inject     : Inject live real-time scenario
- GET  /incidents  : Active gold incident queue
- GET  /metrics    : Prometheus metrics scrape endpoint
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from src.config.runtime import detect_runtime_mode
from src.copilot.sre_rca_agent import AgenticSREIncidentCopilot
from src.ingestion.stream_broker import DualModeStreamBroker
from src.lakehouse.medallion_engine import MedallionEngine
from src.mlops.drift_detector import MultiFeatureDriftDetector
from src.mlops.model_registry import MLOpsModelRegistry
from src.mlops.prometheus_metrics import PrometheusMetricsManager
from scripts.bootstrap_datasets import ensure_dataset_and_lakehouse_ready


# App lifespan: ensure lakehouse and models ready on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify dataset, schema, and initial models
    try:
        ensure_dataset_and_lakehouse_ready()
    except Exception as e:
        print(f"[-] Bootstrap check error: {e}")
    yield


app = FastAPI(
    title="AETHER-DC (GreenOps AI) MLOps API",
    description="Autonomous Green AI Data Center Telemetry, Streaming Lakehouse & Self-Healing MLOps Engine",
    version="2.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core singletons
medallion = MedallionEngine()
broker = DualModeStreamBroker(medallion_engine=medallion)
registry = MLOpsModelRegistry.get_instance()
drift_detector = MultiFeatureDriftDetector()
prom_manager = PrometheusMetricsManager.get_instance()
copilot = AgenticSREIncidentCopilot()


# Request / Response Schemas
class RemediateRequest(BaseModel):
    incident_id: str
    target_pue: Optional[float] = 1.16


class SwapRequest(BaseModel):
    reason: Optional[str] = "Operator Triggered Hot-Swap"
    psi_score: Optional[float] = 0.22


class ScenarioRequest(BaseModel):
    scenario_name: str  # 'thermal_runaway', 'cooling_degradation', 'workload_surge', 'corrupted_sensor_burst'


@app.get("/health")
def healthcheck():
    """Returns application health status and lakehouse summary."""
    kpis = medallion.get_facility_kpis()
    return {
        "status": "healthy",
        "service": "AETHER-DC MLOps Engine",
        "runtime_mode": detect_runtime_mode().value,
        "active_champion": registry.active_champion_name,
        "active_alerts": kpis["active_alerts_count"],
        "dlq_events": kpis["dlq_count"],
        "mean_facility_pue": kpis["mean_pue"],
    }


@app.post("/ingest")
def ingest_telemetry(payload: Dict[str, Any]):
    """Ingests a telemetry packet through Pydantic v2 contract gate."""
    is_valid, msg = broker.publish_telemetry(payload)
    reg = payload.get("datacenter_region", "NA")
    stype = payload.get("server_type", "GPU")
    prom_manager.record_ingest(region=reg, server_type=stype, is_valid=is_valid)

    if not is_valid:
        return {"status": "DLQ_ISOLATED", "message": msg}
    return {"status": "SUCCESS", "event_id": msg}


@app.post("/predict")
def predict_shadow(payload: Dict[str, Any]):
    """Executes multi-task shadow predictions across Champion, Challenger, and Guard."""
    df_single = pd.DataFrame([payload])
    preds = registry.predict_shadow(df_single)
    return preds


@app.get("/drift")
def get_drift_metrics():
    """Calculates live Population Stability Index (PSI) and KS-test metrics."""
    live_df = medallion.get_silver_features(limit=250)
    report = drift_detector.compute_drifts(live_df)

    # Update Prometheus gauges
    for feat, metrics in report["feature_metrics"].items():
        prom_manager.record_psi(feat, metrics["psi_score"])

    return report


@app.post("/swap")
def execute_hotswap(req: SwapRequest):
    """Executes atomic Zero-Downtime Hot-Swap between Champion and Challenger."""
    receipt = registry.hot_swap_now(reason=req.reason, psi=req.psi_score)
    return receipt


@app.get("/incidents")
def list_incidents(
    severity: Optional[str] = None,
    region: Optional[str] = None,
    server_type: Optional[str] = None,
    cooling_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
):
    """Returns filtered active incidents queue."""
    df = medallion.get_active_incidents(
        severity=severity,
        region=region,
        server_type=server_type,
        cooling_type=cooling_type,
        search=search,
        limit=limit,
    )
    return df.to_dict(orient="records")


@app.post("/remediate")
def remediate_incident(req: RemediateRequest):
    """Executes SRE remediation plan on active incident."""
    incidents = medallion.get_active_incidents(limit=200)
    matching = incidents[incidents["incident_id"] == req.incident_id]
    if matching.empty:
        raise HTTPException(status_code=404, detail="Incident ID not found")

    rec = matching.iloc[0].to_dict()
    plan = copilot.analyze_incident(rec)
    success = medallion.remediate_incident(req.incident_id, new_target_pue=req.target_pue or 1.16)

    return {
        "status": "REMEDIATED",
        "incident_id": req.incident_id,
        "success": success,
        "remediation_plan": plan.model_dump(),
    }


@app.post("/inject")
def inject_scenario(req: ScenarioRequest):
    """Triggers live scenario injection (Thermal Runaway, Cooling Degradation, etc.)."""
    receipt = broker.inject_scenario(req.scenario_name)
    return receipt


@app.get("/metrics")
def prometheus_metrics():
    """Prometheus scraping endpoint."""
    data = prom_manager.export_metrics()
    return Response(content=data, media_type="text/plain; version=0.0.4; charset=utf-8")
