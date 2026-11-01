"""AETHER-DC (GreenOps AI) — Main Streamlit Application Entrypoint.

Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform.
Dual-Mode Architecture: Runs on Docker Compose (Redpanda + FastAPI + Prometheus)
and features auto-fallback for 1-click deployment on Streamlit Community Cloud.
"""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd

from src.config.runtime import detect_runtime_mode, RuntimeMode
from src.ingestion.stream_broker import DualModeStreamBroker
from src.lakehouse.medallion_engine import MedallionEngine
from src.mlops.drift_detector import MultiFeatureDriftDetector
from src.mlops.model_registry import MLOpsModelRegistry
from src.mlops.prometheus_metrics import PrometheusMetricsManager
from src.copilot.sre_rca_agent import AgenticSREIncidentCopilot
from src.ui.theme_finnova import inject_finnova_theme
from src.ui.components_bento import (
    render_action_header,
    render_bento_kpi_cards,
    render_top_navbar,
)
from src.ui.components_inspector import (
    render_filter_bar,
    render_obsidian_workspace,
)
from scripts.bootstrap_datasets import ensure_dataset_and_lakehouse_ready

# Page Configuration
st.set_page_config(
    page_title="AETHER-DC | Autonomous Green AI Data Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# Initialize Lakehouse & Models once per session
@st.cache_resource
def init_system_resources():
    ensure_dataset_and_lakehouse_ready()
    medallion = MedallionEngine()
    broker = DualModeStreamBroker(medallion_engine=medallion)
    registry = MLOpsModelRegistry.get_instance()
    drift_detector = MultiFeatureDriftDetector()
    prom_manager = PrometheusMetricsManager.get_instance()
    copilot = AgenticSREIncidentCopilot()
    return medallion, broker, registry, drift_detector, prom_manager, copilot


medallion, broker, registry, drift_detector, prom_manager, copilot = init_system_resources()

# Inject Finnova Custom CSS Theme
inject_finnova_theme()

# Session State Tracking
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Telemetry Hub"
if "selected_incident_id" not in st.session_state:
    st.session_state["selected_incident_id"] = None

runtime_mode = detect_runtime_mode()
runtime_label = "Docker Kafka Broker" if runtime_mode == RuntimeMode.DOCKER_KAFKA else "Cloud Stream In-Memory"

# -------------------------------------------------------------------
# ZONE 1: TOP FLOATING PILL NAVBAR
# -------------------------------------------------------------------
render_top_navbar(
    active_tab=st.session_state["active_tab"],
    runtime_mode_label=runtime_label,
)

# Tab Selector Row (Integrated seamlessly into header navigation)
tab_options = ["Telemetry Hub", "Lakehouse & DLQ", "Drift & MLOps", "SRE Copilot", "Prometheus & Infra"]
tab_select_cols = st.columns([1, 1, 1, 1, 1])
for idx, t_name in enumerate(tab_options):
    with tab_select_cols[idx]:
        is_current = (st.session_state["active_tab"] == t_name)
        if st.button(
            f"{'• ' if is_current else ''}{t_name}",
            key=f"nav_btn_{t_name}",
            type="primary" if is_current else "secondary",
            use_container_width=True,
        ):
            st.session_state["active_tab"] = t_name
            st.rerun()

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# ZONE 2: ACTION HEADER ROW + LIVE SCENARIO INJECTION TRIGGER
# -------------------------------------------------------------------
header_cols = st.columns([2.2, 1.2, 0.9])
with header_cols[0]:
    render_action_header(active_tab=st.session_state["active_tab"])

with header_cols[1]:
    scenario_choice = st.selectbox(
        "Inject Scenario",
        [
            "Thermal Runaway",
            "Cooling Degradation",
            "Workload Surge",
            "Corrupted DLQ Burst",
        ],
        index=0,
        label_visibility="collapsed",
        key="scenario_select",
    )

with header_cols[2]:
    if st.button("+ Inject Anomaly", key="btn_inject_anomaly", type="primary", use_container_width=True):
        receipt = broker.inject_scenario(scenario_choice)
        st.toast(f"Injected: {scenario_choice}!", icon="⚡")
        st.rerun()

# -------------------------------------------------------------------
# REACIVE DATA RETRIEVAL (DUCKDB + MLOPS)
# -------------------------------------------------------------------
kpis = medallion.get_facility_kpis()
live_silver = medallion.get_silver_features(limit=250)
drift_data = drift_detector.compute_drifts(live_silver)

# Update Prometheus Gauges
for feat, metrics in drift_data["feature_metrics"].items():
    prom_manager.record_psi(feat, metrics["psi_score"])
prom_manager.facility_pue_gauge.labels(region="Global", cooling_type="All").set(kpis["mean_pue"])

# -------------------------------------------------------------------
# ZONE 3: 4 ASYMMETRIC BENTO KPI CARDS
# -------------------------------------------------------------------
render_bento_kpi_cards(
    kpis=kpis,
    drift_data=drift_data,
    active_champion=registry.active_champion_name,
    challenger_name=registry.challenger_name,
)

# Inline Hot-Swap Action Row under Bento 4
swap_cols = st.columns([3, 1])
with swap_cols[1]:
    if st.button("⚡ Hot-Swap Champion/Challenger Now", key="btn_quick_swap", use_container_width=True):
        swap_res = registry.hot_swap_now(
            reason="Operator Triggered Hot-Swap via Bento Card",
            psi=drift_data.get("max_psi", 0.22),
        )
        st.toast(f"Hot-Swap Complete! New Champion: {swap_res['new_champion']}", icon="🚀")
        st.rerun()

st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# VIEW ROUTING BASED ON ACTIVE TAB
# -------------------------------------------------------------------
if st.session_state["active_tab"] == "Telemetry Hub":
    # ZONE 4: HORIZONTAL PILL FILTER BAR
    filters = render_filter_bar(total_count=kpis.get("active_alerts_count", 14))

    # Reactive Query to DuckDB Gold Mart
    incidents_df = medallion.get_active_incidents(
        severity=filters["severity"],
        region=filters["region"],
        server_type=filters["server_type"],
        cooling_type=filters["cooling_type"],
        search=filters["search"],
        limit=50,
    )
    dlq_df = medallion.get_dlq_events(limit=50)

    # Remediation callback function
    def handle_remediation(inc_id: str, target_pue: float):
        medallion.remediate_incident(inc_id, new_target_pue=target_pue)

    # ZONE 5: OBSIDIAN SPLIT-VIEW MASTER-DETAIL WORKSPACE
    render_obsidian_workspace(
        incidents_df=incidents_df,
        dlq_df=dlq_df,
        all_telemetry_df=live_silver,
        selected_incident_id=st.session_state["selected_incident_id"],
        on_remediate_callback=handle_remediation,
    )

elif st.session_state["active_tab"] == "Lakehouse & DLQ":
    st.markdown("### DuckDB Medallion Lakehouse Architecture & Dead-Letter Queue (DLQ)")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE8F6; border-radius: 18px; padding: 1.25rem;">
            <div style="color: #6E7191; font-size: 0.8rem; font-weight: 700;">BRONZE LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825;">Raw Append-Only</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem;">
                Validated JSON telemetry ingested via Pydantic v2 contract gate.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE8F6; border-radius: 18px; padding: 1.25rem;">
            <div style="color: #4A3BDC; font-size: 0.8rem; font-weight: 700;">SILVER LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825;">Rolling Window View</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem;">
                Window SQL functions: IT Power, Cooling Overhead, Cooling Stress, Thermal dT/dt.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE8F6; border-radius: 18px; padding: 1.25rem;">
            <div style="color: #12A594; font-size: 0.8rem; font-weight: 700;">GOLD LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825;">Analytical Incident Marts</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem;">
                Prioritized anomalies, TreeSHAP attributions, and SRE remediation state.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### Dead-Letter Queue (DLQ) Isolated Packets")
    dlq_data = medallion.get_dlq_events(limit=50)
    if dlq_data.empty:
        st.info("DLQ is currently clean. No corrupted packets detected.")
    else:
        st.dataframe(dlq_data, use_container_width=True, height=350)

elif st.session_state["active_tab"] == "Drift & MLOps":
    st.markdown("### Production MLOps Arena: PSI Drift & Shadow Evaluation")
    eval_metrics = registry.evaluate_shadow_arena(live_silver)

    d_col1, d_col2 = st.columns([1.2, 1.8])
    with d_col1:
        st.markdown("#### 10-Bin Population Stability Index (PSI)")
        drift_records = []
        for feat, d_vals in drift_data["feature_metrics"].items():
            drift_records.append({
                "Feature": feat,
                "PSI Score": d_vals["psi_score"],
                "KS Stat": d_vals["ks_stat"],
                "P-Value": d_vals["p_value"],
                "Status": d_vals["status"],
            })
        st.dataframe(pd.DataFrame(drift_records), use_container_width=True, height=300)

    with d_col2:
        st.markdown("#### Shadow Evaluation: Champion (LightGBM) vs Challenger (XGBoost)")
        shadow_records = [
            {"Model Role": "Champion", "Algorithm": registry.active_champion_name, "Rolling F1": eval_metrics["champion_f1"], "RMSE (PUE)": eval_metrics["champion_rmse"]},
            {"Model Role": "Challenger (Shadow)", "Algorithm": registry.challenger_name, "Rolling F1": eval_metrics["challenger_f1"], "RMSE (PUE)": eval_metrics["challenger_rmse"]},
        ]
        st.dataframe(pd.DataFrame(shadow_records), use_container_width=True)

        if eval_metrics["is_promotion_ready"]:
            st.warning("⚠️ Promotion Ready: Challenger XGBoost is outperforming Champion on drifted distribution!")
        else:
            st.success("✅ Champion model performance remains optimal on current baseline distribution.")

    st.markdown("#### Model Hot-Swap Audit Log (DuckDB `mlops_model_audit_log`)")
    audit_logs = medallion.get_hotswap_audit_logs()
    if audit_logs.empty:
        st.info("No hot-swaps executed yet.")
    else:
        st.dataframe(audit_logs, use_container_width=True)

elif st.session_state["active_tab"] == "SRE Copilot":
    st.markdown("### Autonomous SRE Incident Copilot & Counterfactual Cooling Optimizer")
    active_incidents = medallion.get_active_incidents(limit=10)
    if active_incidents.empty:
        st.info("All data center racks are running nominal. SRE Copilot in standby mode.")
    else:
        selected_inc = st.selectbox(
            "Select Incident for SRE Root-Cause Analysis (RCA)",
            active_incidents["incident_id"].tolist(),
            format_func=lambda x: f"Incident #{x} ({active_incidents[active_incidents['incident_id'] == x]['rack_id'].iloc[0]})",
        )
        rec = active_incidents[active_incidents["incident_id"] == selected_inc].iloc[0].to_dict()
        plan = copilot.analyze_incident(rec)

        sre_col1, sre_col2 = st.columns([1.5, 1])
        with sre_col1:
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #EAE8F6; border-radius: 20px; padding: 1.5rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #161825;">Root-Cause Analysis (RCA) Report</h4>
                <p style="color: #6E7191; font-size: 0.9rem;">{plan.root_cause_summary}</p>
                <div style="margin-top: 1rem; padding: 1rem; background: #F8F7FD; border-radius: 12px;">
                    <div style="font-weight: 700; color: #4A3BDC; font-size: 0.85rem;">RECOMMENDED ACTIONS:</div>
                    <ul style="margin: 0.5rem 0 0 1rem; color: #161825; font-size: 0.85rem;">
                        <li><b>Cooling Loop:</b> {plan.recommended_cooling_action}</li>
                        <li><b>Workload Distribution:</b> {plan.recommended_workload_action}</li>
                        <li><b>MLOps Strategy:</b> {plan.recommended_mlops_action}</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with sre_col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #5E5CE6 0%, #7B78D8 100%); color: #FFFFFF; border-radius: 20px; padding: 1.5rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF;">Counterfactual Impact</h4>
                <div style="margin-top: 1rem;">
                    <div style="font-size: 0.8rem; opacity: 0.8;">CURRENT PUE</div>
                    <div style="font-size: 1.6rem; font-weight: 800;">{rec.get('actual_pue', 1.45):.2f}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.75rem;">PROJECTED TARGET PUE</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #B3F5E7;">{plan.projected_pue_after_action:.2f}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.75rem;">ESTIMATED SAVINGS</div>
                    <div style="font-size: 1.3rem; font-weight: 700;">${plan.estimated_hourly_savings_usd:.2f}/hr · {plan.estimated_carbon_reduction_kg:.1f} kg CO2/hr</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state["active_tab"] == "Prometheus & Infra":
    st.markdown("### Production Prometheus Metrics & Dual-Mode Infrastructure")
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #EAE8F6; border-radius: 18px; padding: 1.25rem;">
            <h4 style="margin: 0 0 0.5rem 0;">Exposed Prometheus Telemetry Metrics</h4>
            <ul style="font-size: 0.85rem; color: #6E7191; line-height: 1.6;">
                <li><code>aether_telemetry_events_total</code> [Counter]</li>
                <li><code>aether_facility_pue_gauge</code> [Gauge]</li>
                <li><code>aether_rack_inlet_temp_celsius</code> [Gauge]</li>
                <li><code>aether_feature_drift_psi</code> [Gauge]</li>
                <li><code>aether_model_inference_latency_ms</code> [Histogram]</li>
                <li><code>aether_model_rolling_f1_score</code> [Gauge]</li>
                <li><code>aether_model_hotswap_total</code> [Counter]</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"""
        <div style="background: #1E2132; color: #FFFFFF; border-radius: 18px; padding: 1.25rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF;">Runtime Infrastructure Status</h4>
            <p style="font-size: 0.85rem; color: #A5A8C4;">Active Mode: <b>{runtime_label}</b></p>
            <p style="font-size: 0.85rem; color: #A5A8C4;">Lakehouse Path: <code>{medallion.db_path}</code></p>
            <p style="font-size: 0.85rem; color: #A5A8C4;">FastAPI MLOps: <code>http://localhost:8000/metrics</code></p>
            <p style="font-size: 0.85rem; color: #A5A8C4;">Prometheus Server: <code>http://localhost:9090</code></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### Live Prometheus Metrics Text Output (GET `/metrics`)")
    raw_prom = prom_manager.export_metrics().decode("utf-8")
    st.code(raw_prom[:1500] + ("\n... [truncated]" if len(raw_prom) > 1500 else ""), language="text")
