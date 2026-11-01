"""Finnova Filter Bar & Obsidian Split-View Master-Detail Workspace.

Implements:
- Horizontal Pill Filter Bar (Region, Server, Cooling, Severity, Search)
- Obsidian Workspace (#1E2132, radius 28px) with Top Inverted Center Notch
- Left Pane (38%): Interactive Incident Queue with #5B4FE9 Selected Pill Highlight
- Right Pane (62%): Periwinkle-Indigo (#5E5CE6) Inspector Card with 4 Glass Sub-Cards & Execute Remediation CTA
"""

from typing import Any, Dict, Optional
import pandas as pd
import streamlit as st

from src.copilot.sre_rca_agent import AgenticSREIncidentCopilot

copilot = AgenticSREIncidentCopilot()


def render_filter_bar(total_count: int = 50) -> Dict[str, Any]:
    """Renders Zone 4: Horizontal Pill Filter Bar."""
    fcols = st.columns([1.2, 1.2, 1.2, 1.2, 1.2, 2.0])

    with fcols[0]:
        st.markdown(
            f"""<div style="background: #EFEFFC; color: #4A3BDC; font-weight: 700; font-size: 0.8rem;
            padding: 0.55rem 0.8rem; border-radius: 9999px; text-align: center; border: 1px solid #DFDCFF;">
            Active filters ({total_count})</div>""",
            unsafe_allow_html=True,
        )

    with fcols[1]:
        region_filter = st.selectbox(
            "Region",
            ["All", "NA", "EU", "APAC", "ME"],
            index=0,
            label_visibility="collapsed",
            key="filter_region",
        )

    with fcols[2]:
        server_filter = st.selectbox(
            "Server Type",
            ["All", "GPU", "Compute", "Storage", "Edge"],
            index=0,
            label_visibility="collapsed",
            key="filter_server",
        )

    with fcols[3]:
        cooling_filter = st.selectbox(
            "Cooling Type",
            ["All", "Liquid", "Hybrid", "Air"],
            index=0,
            label_visibility="collapsed",
            key="filter_cooling",
        )

    with fcols[4]:
        severity_filter = st.selectbox(
            "Severity",
            ["All", "CRITICAL", "WARNING"],
            index=0,
            label_visibility="collapsed",
            key="filter_severity",
        )

    with fcols[5]:
        search_query = st.text_input(
            "Search",
            placeholder="Search rack or incident #",
            label_visibility="collapsed",
            key="filter_search",
        )

    return {
        "region": region_filter,
        "server_type": server_filter,
        "cooling_type": cooling_filter,
        "severity": severity_filter,
        "search": search_query,
    }


def render_obsidian_workspace(
    incidents_df: pd.DataFrame,
    dlq_df: pd.DataFrame,
    all_telemetry_df: pd.DataFrame,
    selected_incident_id: Optional[str] = None,
    on_remediate_callback=None,
):
    """Renders Zone 5: Obsidian Split-View Master-Detail Workspace."""
    inc_count = len(incidents_df)
    dlq_count = len(dlq_df)

    # Top Inverted Center Notch Tab Switcher using Segmented Control
    notch_options = [
        "All Telemetry Racks",
        f"DLQ Alerts [{dlq_count}]",
        f"Active Incidents [{inc_count}]",
    ]
    current_notch = st.session_state.get("obsidian_tab", f"Active Incidents [{inc_count}]")
    if current_notch not in notch_options:
        current_notch = f"Active Incidents [{inc_count}]"

    n_cols = st.columns([1, 2.2, 1])
    with n_cols[1]:
        chosen_notch = st.segmented_control(
            "Notch Tabs",
            notch_options,
            default=current_notch,
            label_visibility="collapsed",
            key="segmented_notch_tabs",
        )
        if chosen_notch and chosen_notch != st.session_state.get("obsidian_tab"):
            st.session_state["obsidian_tab"] = chosen_notch
            st.rerun()

    active_notch = st.session_state.get("obsidian_tab", f"Active Incidents [{inc_count}]")

    # Obsidian Workspace Container
    st.markdown('<div class="finnova-obsidian-workspace">', unsafe_allow_html=True)

    if "DLQ Alerts" in active_notch:
        st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 1rem;'>Dead-Letter Queue (DLQ) Isolated Packets</h3>", unsafe_allow_html=True)
        if dlq_df.empty:
            st.info("No corrupted packets trapped in DLQ. All ingested packets are physically valid.")
        else:
            st.dataframe(
                dlq_df[["dlq_id", "ingested_at", "error_type", "error_detail", "source_topic", "raw_payload"]],
                use_container_width=True,
                height=420,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        return

    elif "All Telemetry Racks" in active_notch:
        st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 1rem;'>All Racks Telemetry Live Stream (DuckDB Silver)</h3>", unsafe_allow_html=True)
        if all_telemetry_df.empty:
            st.info("No telemetry records found.")
        else:
            display_cols = [
                "timestamp", "rack_id", "datacenter_region", "server_type", "cooling_type",
                "inlet_temperature_c", "cooling_efficiency", "power_consumption_kw", "pue",
                "cooling_stress_index", "thermal_velocity_delta_c"
            ]
            cols_avail = [c for c in display_cols if c in all_telemetry_df.columns]
            st.dataframe(all_telemetry_df[cols_avail], use_container_width=True, height=420)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Master-Detail Columns: 38% Left Queue, 62% Right Indigo Card
    col_left, col_right = st.columns([1.15, 1.85])

    # Determine currently selected record
    if incidents_df.empty:
        selected_record = None
    else:
        if selected_incident_id:
            match = incidents_df[incidents_df["incident_id"] == selected_incident_id]
            selected_record = match.iloc[0].to_dict() if not match.empty else incidents_df.iloc[0].to_dict()
        else:
            selected_record = incidents_df.iloc[0].to_dict()

    # ----------------------------------------------------
    # LEFT PANE (38%): Interactive Incident Queue
    # ----------------------------------------------------
    with col_left:
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
            <span style="color: #A5A8C4; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.05em;">LIVE INCIDENT QUEUE</span>
            <span style="color: #5B4FE9; font-size: 0.75rem; font-weight: 700; background: rgba(91, 79, 233, 0.2); padding: 0.2rem 0.6rem; border-radius: 9999px;">Prioritized</span>
        </div>
        """, unsafe_allow_html=True)

        if incidents_df.empty:
            st.markdown("<p style='color: #A5A8C4;'>No active thermal or power incidents. All racks nominal!</p>", unsafe_allow_html=True)
        else:
            for idx, row in incidents_df.head(6).iterrows():
                inc_id = row["incident_id"]
                rack_id = row["rack_id"]
                pue_val = float(row.get("actual_pue", 1.25))
                temp_c = float(row.get("inlet_temperature_c", 28.0))
                stype = row.get("server_type", "GPU")
                status = row.get("incident_status", "Thermal Spike")
                is_selected = (selected_record and selected_record.get("incident_id") == inc_id)

                btn_label = f"[{stype[:3]}]  #{inc_id} · {rack_id}   |   {temp_c:.1f}°C   |   {pue_val:.2f} PUE"
                if st.button(
                    btn_label,
                    key=f"inc_btn_{inc_id}",
                    type="primary" if is_selected else "secondary",
                    use_container_width=True,
                ):
                    st.session_state["selected_incident_id"] = inc_id
                    st.rerun()

    # ----------------------------------------------------
    # RIGHT PANE (62%): Large Periwinkle-Indigo Inspector Card
    # ----------------------------------------------------
    with col_right:
        if not selected_record:
            st.info("Select an incident from the left queue to inspect details.")
        else:
            inc_id = selected_record.get("incident_id")
            rack_id = selected_record.get("rack_id")
            reg = selected_record.get("datacenter_region", "NA")
            stype = selected_record.get("server_type", "GPU")
            ctype = selected_record.get("cooling_type", "Liquid")
            temp_c = float(selected_record.get("inlet_temperature_c", 38.0))
            cooling_eff = float(selected_record.get("cooling_efficiency", 0.50))
            power_kw = float(selected_record.get("power_consumption_kw", 85.0))
            actual_pue = float(selected_record.get("actual_pue", 1.45))
            champ_pue = float(selected_record.get("predicted_pue_champion", 1.47))
            chall_pue = float(selected_record.get("predicted_pue_challenger", 1.44))
            status_text = selected_record.get("incident_status", "Thermal Spike")
            top_shap = selected_record.get("top_shap_feature", "inlet_temperature_c")
            waste_usd = float(selected_record.get("estimated_hourly_waste_usd", 38.4))

            # Run SRE RCA plan
            plan = copilot.analyze_incident(selected_record)

            # Inspector Card
            st.markdown(f"""
            <div class="finnova-indigo-inspector">
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem;">
                        <div>
                            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.85;">INCIDENT DEEP INSPECTOR</span>
                            <h2 style="margin: 0.15rem 0 0 0; font-size: 1.6rem; font-weight: 800; color: #FFFFFF;">#{inc_id} · {rack_id}</h2>
                            <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.2rem;">
                                Cluster: <b>{reg}-{stype}-{ctype}</b> · Model Regime: <b>Shadow LGBM vs XGBoost</b>
                            </div>
                        </div>
                        <span style="background: rgba(229, 72, 77, 0.35); border: 1px solid rgba(255, 255, 255, 0.4);
                              color: #FFFFFF; font-weight: 800; font-size: 0.75rem; padding: 0.35rem 0.85rem; border-radius: 9999px;">
                            {status_text.upper()}
                        </span>
                    </div>

                    <!-- 4 Translucent Glass Sub-Cards (2x2 Grid) -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1.25rem;">
                        <!-- Glass Sub-Card 1: Thermal & Power State -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.85; font-weight: 700;">THERMAL & POWER METRICS</div>
                            <div style="font-size: 1.4rem; font-weight: 800; margin-top: 0.2rem;">{temp_c:.1f}°C <span style="font-size: 0.85rem; font-weight: 500;">Inlet</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.95; margin-top: 0.25rem;">
                                Cooling Efficiency: <b>{cooling_eff:.2f}</b><br>
                                Power Draw: <b>{power_kw:.1f} kW</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 2: Shadow Model Verdict -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.85; font-weight: 700;">SHADOW MODEL VERDICT</div>
                            <div style="font-size: 1.4rem; font-weight: 800; margin-top: 0.2rem;">{chall_pue:.2f} <span style="font-size: 0.85rem; font-weight: 500;">XGB PUE</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.95; margin-top: 0.25rem;">
                                Champion LGBM: <b>{champ_pue:.2f} PUE</b><br>
                                Top SHAP Driver: <b>{top_shap}</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 3: Financial & Carbon Burn -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.85; font-weight: 700;">FINANCIAL & CARBON BURN</div>
                            <div style="font-size: 1.4rem; font-weight: 800; margin-top: 0.2rem;">${waste_usd:.2f}/hr <span style="font-size: 0.85rem; font-weight: 500;">Waste</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.95; margin-top: 0.25rem;">
                                Est. Carbon Penalty: <b>{plan.estimated_carbon_reduction_kg:.1f} kg CO2/hr</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 4: SRE Copilot Action -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.85; font-weight: 700;">AGENTIC SRE ROOT-CAUSE</div>
                            <div style="font-size: 0.76rem; font-weight: 600; line-height: 1.35; margin-top: 0.2rem;">
                                {plan.root_cause_summary[:110]}...
                            </div>
                            <div style="font-size: 0.72rem; opacity: 0.95; margin-top: 0.25rem; color: #FFE79A;">
                                Action: {plan.recommended_cooling_action[:75]}...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Summary Row -->
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 0.85rem; margin-top: 0.5rem;">
                    <div style="display: flex; gap: 1.5rem; align-items: center;">
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">BASELINE PUE</div>
                            <div style="font-size: 1.1rem; font-weight: 800;">1.15</div>
                        </div>
                        <div style="color: rgba(255, 255, 255, 0.4); font-size: 1.2rem;">→</div>
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">CURRENT ANOMALY</div>
                            <div style="font-size: 1.1rem; font-weight: 800; color: #FFD4D5;">{actual_pue:.2f}</div>
                        </div>
                        <div style="color: rgba(255, 255, 255, 0.4); font-size: 1.2rem;">→</div>
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">PROJECTED TARGET</div>
                            <div style="font-size: 1.1rem; font-weight: 800; color: #B3F5E7;">{plan.projected_pue_after_action:.2f}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Remediation Button Trigger
            st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)
            if st.button(f"⚡ Execute SRE Remediation for #{inc_id} (Target PUE: {plan.projected_pue_after_action:.2f})", key="btn_remediate_main", type="primary", use_container_width=True):
                if on_remediate_callback:
                    on_remediate_callback(inc_id, plan.projected_pue_after_action)
                st.toast(f"Remediation executed for #{inc_id}! Target PUE normalized to {plan.projected_pue_after_action:.2f}.", icon="✅")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
