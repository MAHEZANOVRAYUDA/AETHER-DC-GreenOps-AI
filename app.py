"""AETHER-DC (GreenOps AI) — Main Streamlit Application Entrypoint.

Autonomous Green AI Data Center Telemetry, Streaming Medallion Lakehouse & Self-Healing MLOps Platform.
Pixel-accurate Finnova Visual Architecture (desain ui.jpg).
"""

import os
from pathlib import Path
import sys
import textwrap

# Fix joblib wmic deprecation on Windows
os.environ["LOKY_MAX_CPU_COUNT"] = str(os.cpu_count() or 4)

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import streamlit as st

from scripts.bootstrap_datasets import ensure_dataset_and_lakehouse_ready
from src.config.runtime import RuntimeMode, detect_runtime_mode
from src.copilot.sre_rca_agent import AgenticSREIncidentCopilot
from src.ingestion.stream_broker import DualModeStreamBroker
from src.lakehouse.medallion_engine import MedallionEngine
from src.mlops.drift_detector import MultiFeatureDriftDetector
from src.mlops.model_registry import MLOpsModelRegistry
from src.mlops.prometheus_metrics import PrometheusMetricsManager
from src.ui.components_bento import (
    render_action_header,
    render_bento_kpi_cards,
    render_brand_header,
    render_nav_right_cluster,
)
from src.ui.components_inspector import (
    render_filter_bar,
    render_obsidian_workspace,
)
from src.ui.theme_finnova import inject_finnova_theme

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
    st.session_state["active_tab"] = "+ Telemetry Hub"
if "selected_incident_id" not in st.session_state:
    st.session_state["selected_incident_id"] = None

runtime_mode = detect_runtime_mode()
runtime_label = "Docker Kafka Broker" if runtime_mode == RuntimeMode.DOCKER_KAFKA else "Cloud Stream In-Memory"

# -------------------------------------------------------------------
# PERFORMANCE MEMOIZATION HELPERS
# -------------------------------------------------------------------
@st.cache_data(ttl=3)
def get_cached_kpis(_medallion_inst):
    return _medallion_inst.get_facility_kpis()


@st.cache_data(ttl=3)
def get_cached_silver(_medallion_inst):
    return _medallion_inst.get_silver_features(limit=250)


@st.cache_data(ttl=4)
def get_cached_drift(_detector_inst, silver_df):
    return _detector_inst.compute_drifts(silver_df)


@st.cache_data(ttl=4)
def get_cached_eval(_registry_inst, silver_df):
    return _registry_inst.evaluate_shadow_arena(silver_df)


# Reactive Data Retrieval
kpis = get_cached_kpis(medallion)
live_silver = get_cached_silver(medallion)
drift_data = get_cached_drift(drift_detector, live_silver)
eval_metrics = get_cached_eval(registry, live_silver)

# Update Prometheus Gauges
for feat, metrics in drift_data["feature_metrics"].items():
    prom_manager.record_psi(feat, metrics["psi_score"])
prom_manager.facility_pue_gauge.labels(region="Global", cooling_type="All").set(kpis["mean_pue"])

# -------------------------------------------------------------------
# ZONE 1: TOP FLOATING PILL NAVBAR (Single Unified Row vs desain ui.jpg)
# -------------------------------------------------------------------
nav_options = [
    "+ Telemetry Hub",
    "Lakehouse & DLQ",
    "Drift & MLOps",
    "SRE Copilot",
    "Prometheus & Infra",
]

nav_cols = st.columns([1.15, 2.2, 1.15])
with nav_cols[0]:
    render_brand_header(alert_count=kpis.get("active_alerts_count", 54))

with nav_cols[1]:
    chosen_tab = st.segmented_control(
        "Navbar Capsule",
        nav_options,
        default=st.session_state["active_tab"],
        label_visibility="collapsed",
        key="main_nav_segmented",
    )
    if chosen_tab and chosen_tab != st.session_state["active_tab"]:
        st.session_state["active_tab"] = chosen_tab
        st.rerun()

with nav_cols[2]:
    render_nav_right_cluster(runtime_mode_label=runtime_label)

st.html("<div style='margin-bottom: 0.6rem;'></div>")

# -------------------------------------------------------------------
# ZONE 2: ACTION HEADER ROW + LIVE SCENARIO INJECTION TRIGGER
# -------------------------------------------------------------------
header_cols = st.columns([2.4, 1.1, 0.85])
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
    if st.button("⚡ Inject Anomaly", key="btn_inject_anomaly", type="primary", use_container_width=True):
        broker.inject_scenario(scenario_choice)
        st.toast(f"Injected: {scenario_choice}!", icon="⚡")
        st.rerun()

# -------------------------------------------------------------------
# ZONE 3: 4 ASYMMETRIC BENTO KPI CARDS
# -------------------------------------------------------------------
render_bento_kpi_cards(
    kpis=kpis,
    drift_data=drift_data,
    eval_metrics=eval_metrics,
    active_champion=registry.active_champion_name,
    challenger_name=registry.challenger_name,
)

# Integrated Hot-Swap Action Row directly beneath Card 4
swap_cols = st.columns([3, 1])
with swap_cols[1]:
    if st.button("⚡ Hot-Swap Champion/Challenger Now", key="btn_hotswap_card4", use_container_width=True):
        swap_res = registry.hot_swap_now(
            reason="Operator Triggered Hot-Swap via Bento Card",
            psi=drift_data.get("max_psi", 0.22),
        )
        st.toast(f"Hot-Swap Complete! New Champion: {swap_res['new_champion']}", icon="🚀")
        st.rerun()

st.html("<div style='margin-bottom: 0.75rem;'></div>")

# -------------------------------------------------------------------
# VIEW ROUTING BASED ON ACTIVE TAB
# -------------------------------------------------------------------
if st.session_state["active_tab"] == "+ Telemetry Hub":
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
    st.html("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.45rem; font-weight: 800; color: #161825; margin: 0;">DuckDB Medallion Lakehouse Architecture & Dead-Letter Queue (DLQ)</h2>
        <p style="color: #6E7191; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Unified streaming data platform with schema validation, rolling SQL views, and analytical data marts.</p>
    </div>
    """)
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 20px; padding: 1.35rem; box-shadow: 0 4px 16px rgba(22, 24, 37, 0.03);">
            <div style="color: #6E7191; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.05em;">BRONZE LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825; margin-top: 0.2rem;">Raw Append-Only</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem; line-height: 1.4;">
                Validated JSON telemetry ingested via Pydantic v2 strict contract gate with immutable lineage.
            </p>
        </div>
        """)
    with m_col2:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 20px; padding: 1.35rem; box-shadow: 0 4px 16px rgba(22, 24, 37, 0.03);">
            <div style="color: #4A3BDC; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.05em;">SILVER LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825; margin-top: 0.2rem;">Rolling Window View</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem; line-height: 1.4;">
                Window SQL functions: IT Power, Cooling Overhead, Cooling Stress Index, and Thermal velocity dT/dt.
            </p>
        </div>
        """)
    with m_col3:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 20px; padding: 1.35rem; box-shadow: 0 4px 16px rgba(22, 24, 37, 0.03);">
            <div style="color: #12A594; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.05em;">GOLD LAYER</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #161825; margin-top: 0.2rem;">Analytical Incident Marts</div>
            <p style="font-size: 0.8rem; color: #6E7191; margin-top: 0.35rem; line-height: 1.4;">
                Prioritized anomalies, TreeSHAP local attributions, and autonomous SRE remediation state tracking.
            </p>
        </div>
        """)

    st.html("<div style='margin-bottom: 1.5rem;'></div>")
    st.html("<h3 style='font-size: 1.15rem; font-weight: 800; color: #161825; margin-bottom: 0.75rem;'>Dead-Letter Queue (DLQ) Isolated Packets</h3>")
    dlq_data = medallion.get_dlq_events(limit=50)
    if dlq_data.empty:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 16px; padding: 2rem; text-align: center; color: #6E7191;">
            <div style="font-size: 1.8rem; margin-bottom: 0.3rem;">🛡️</div>
            <div style="font-weight: 700; color: #161825;">DLQ is currently clean</div>
            <div style="font-size: 0.8rem;">No corrupted or out-of-boundary packets detected.</div>
        </div>
        """)
    else:
        st.dataframe(dlq_data, use_container_width=True, height=350)

elif st.session_state["active_tab"] == "Drift & MLOps":
    st.html("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.45rem; font-weight: 800; color: #161825; margin: 0;">Production MLOps Arena: PSI Drift & Shadow Evaluation</h2>
        <p style="color: #6E7191; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Multi-feature statistical drift monitoring with automated shadow model evaluation and audit tracking.</p>
    </div>
    """)
    d_col1, d_col2 = st.columns([1.2, 1.8])
    with d_col1:
        st.html("<h4 style='margin: 0 0 0.5rem 0; font-weight: 800; font-size: 1rem;'>10-Bin Population Stability Index (PSI)</h4>")
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
        st.html("<h4 style='margin: 0 0 0.5rem 0; font-weight: 800; font-size: 1rem;'>Shadow Evaluation: Champion (LightGBM) vs Challenger (XGBoost)</h4>")
        shadow_records = [
            {"Model Role": "Champion", "Algorithm": registry.active_champion_name, "Rolling F1": f"{eval_metrics['champion_f1'] * 100:.1f}%", "RMSE (PUE)": eval_metrics["champion_rmse"]},
            {"Model Role": "Challenger (Shadow)", "Algorithm": registry.challenger_name, "Rolling F1": f"{eval_metrics['challenger_f1'] * 100:.1f}%", "RMSE (PUE)": eval_metrics["challenger_rmse"]},
        ]
        st.dataframe(pd.DataFrame(shadow_records), use_container_width=True)

        if eval_metrics["is_promotion_ready"]:
            st.warning("⚠️ Promotion Ready: Challenger XGBoost is outperforming Champion on drifted distribution!")
        else:
            st.success("✅ Champion model performance remains optimal on current baseline distribution.")

    st.html("<div style='margin-top: 1rem;'></div>")
    st.html("<h4 style='margin: 0 0 0.5rem 0; font-weight: 800; font-size: 1rem;'>Model Hot-Swap Audit Log (DuckDB mlops_model_audit_log)</h4>")
    audit_logs = medallion.get_hotswap_audit_logs()
    if audit_logs.empty:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 14px; padding: 1.5rem; text-align: center; color: #6E7191;">
            No model hot-swaps recorded yet.
        </div>
        """)
    else:
        st.dataframe(audit_logs, use_container_width=True)

elif st.session_state["active_tab"] == "SRE Copilot":
    st.html("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.45rem; font-weight: 800; color: #161825; margin: 0;">Autonomous SRE Incident Copilot & Counterfactual Cooling Optimizer</h2>
        <p style="color: #6E7191; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Thermodynamic Root-Cause Analysis grounded in TreeSHAP attributions and counterfactual simulation.</p>
    </div>
    """)
    active_incidents = medallion.get_active_incidents(limit=10)
    if active_incidents.empty:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 18px; padding: 2.5rem; text-align: center; color: #6E7191;">
            <div style="font-size: 2rem;">🌱</div>
            <div style="font-weight: 700; color: #161825; margin-top: 0.5rem;">All data center racks are running nominal</div>
            <div style="font-size: 0.8rem; margin-top: 0.2rem;">SRE Copilot is in standby monitoring mode.</div>
        </div>
        """)
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
            rca_html = textwrap.dedent(f"""
            <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 20px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(22, 24, 37, 0.03);">
                <h4 style="margin: 0 0 0.5rem 0; color: #161825; font-weight: 800;">Root-Cause Analysis (RCA) Report</h4>
                <p style="color: #6E7191; font-size: 0.88rem; line-height: 1.5;">{plan.root_cause_summary}</p>
                <div style="margin-top: 1rem; padding: 1.1rem; background: #F8F7FD; border-radius: 14px; border: 1px solid #ECEEF6;">
                    <div style="font-weight: 800; color: #4A3BDC; font-size: 0.82rem; letter-spacing: 0.05em;">RECOMMENDED ACTIONS:</div>
                    <ul style="margin: 0.5rem 0 0 1.2rem; color: #161825; font-size: 0.85rem; line-height: 1.6;">
                        <li><b>Cooling Loop:</b> {plan.recommended_cooling_action}</li>
                        <li><b>Workload Distribution:</b> {plan.recommended_workload_action}</li>
                        <li><b>MLOps Strategy:</b> {plan.recommended_mlops_action}</li>
                    </ul>
                </div>
            </div>
            """).strip()
            st.html(rca_html)

        with sre_col2:
            impact_html = textwrap.dedent(f"""
            <div style="background: linear-gradient(135deg, #5E5CE6 0%, #7B78D8 100%); color: #FFFFFF; border-radius: 20px; padding: 1.5rem; box-shadow: 0 8px 24px rgba(94, 92, 230, 0.3);">
                <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF; font-weight: 800;">Counterfactual Impact</h4>
                <div style="margin-top: 1rem;">
                    <div style="font-size: 0.75rem; opacity: 0.85; font-weight: 700;">CURRENT PUE</div>
                    <div style="font-size: 1.7rem; font-weight: 800;">{rec.get('actual_pue', 1.45):.2f}</div>
                    <div style="font-size: 0.75rem; opacity: 0.85; font-weight: 700; margin-top: 0.75rem;">PROJECTED TARGET PUE</div>
                    <div style="font-size: 1.7rem; font-weight: 800; color: #B3F5E7;">{plan.projected_pue_after_action:.2f}</div>
                    <div style="font-size: 0.75rem; opacity: 0.85; font-weight: 700; margin-top: 0.75rem;">ESTIMATED SAVINGS</div>
                    <div style="font-size: 1.35rem; font-weight: 800;">${plan.estimated_hourly_savings_usd:.2f}/hr · {plan.estimated_carbon_reduction_kg:.1f} kg CO2/hr</div>
                </div>
            </div>
            """).strip()
            st.html(impact_html)

elif st.session_state["active_tab"] == "Prometheus & Infra":
    st.html("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.45rem; font-weight: 800; color: #161825; margin: 0;">Production Prometheus Metrics & Dual-Mode Infrastructure</h2>
        <p style="color: #6E7191; font-size: 0.85rem; margin: 0.25rem 0 0 0;">Zero-external-dependency prometheus exposition for scrape targets and observability.</p>
    </div>
    """)
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.html("""
        <div style="background: #FFFFFF; border: 1px solid #ECEEF6; border-radius: 20px; padding: 1.35rem; box-shadow: 0 4px 16px rgba(22, 24, 37, 0.03);">
            <h4 style="margin: 0 0 0.5rem 0; font-weight: 800;">Exposed Prometheus Telemetry Metrics</h4>
            <ul style="font-size: 0.85rem; color: #6E7191; line-height: 1.8;">
                <li><code>aether_telemetry_events_total</code> [Counter]</li>
                <li><code>aether_facility_pue_gauge</code> [Gauge]</li>
                <li><code>aether_rack_inlet_temp_celsius</code> [Gauge]</li>
                <li><code>aether_feature_drift_psi</code> [Gauge]</li>
                <li><code>aether_model_inference_latency_ms</code> [Histogram]</li>
                <li><code>aether_model_rolling_f1_score</code> [Gauge]</li>
                <li><code>aether_model_hotswap_total</code> [Counter]</li>
            </ul>
        </div>
        """)
    with p_col2:
        st.html(f"""
        <div style="background: #161825; color: #FFFFFF; border-radius: 20px; padding: 1.35rem; box-shadow: 0 8px 24px rgba(22, 24, 37, 0.15);">
            <h4 style="margin: 0 0 0.5rem 0; color: #FFFFFF; font-weight: 800;">Runtime Infrastructure Status</h4>
            <p style="font-size: 0.85rem; color: #A5A8C4; margin: 0.4rem 0;">Active Mode: <b style="color: #FFFFFF;">{runtime_label}</b></p>
            <p style="font-size: 0.85rem; color: #A5A8C4; margin: 0.4rem 0;">Lakehouse Path: <code style="color: #B3AEF8;">{medallion.db_path}</code></p>
            <p style="font-size: 0.85rem; color: #A5A8C4; margin: 0.4rem 0;">FastAPI MLOps: <code style="color: #B3AEF8;">http://localhost:8000/metrics</code></p>
            <p style="font-size: 0.85rem; color: #A5A8C4; margin: 0.4rem 0;">Prometheus Server: <code style="color: #B3AEF8;">http://localhost:9090</code></p>
        </div>
        """)

    st.html("<div style='margin-top: 1rem;'></div>")
    st.html("<h4 style='font-size: 1rem; font-weight: 800; color: #161825; margin-bottom: 0.5rem;'>Live Prometheus Metrics Text Output (GET /metrics)</h4>")
    raw_prom = prom_manager.export_metrics().decode("utf-8")
    st.code(raw_prom[:1500] + ("\n... [truncated]" if len(raw_prom) > 1500 else ""), language="text")
