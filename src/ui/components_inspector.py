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
    # Top Inverted Center Notch Tab Switcher
    active_tab = st.session_state.get("obsidian_tab", "Active Incidents")
    inc_count = len(incidents_df)
    dlq_count = len(dlq_df)

    n_cols = st.columns([1, 2, 1])
    with n_cols[1]:
        tab_cols = st.columns(3)
        with tab_cols[0]:
            if st.button("All Telemetry Racks", key="tab_all_racks", use_container_width=True):
                st.session_state["obsidian_tab"] = "All Racks"
                st.rerun()
        with tab_cols[1]:
            if st.button(f"DLQ Alerts [{dlq_count}]", key="tab_dlq", use_container_width=True):
                st.session_state["obsidian_tab"] = "DLQ Alerts"
                st.rerun()
        with tab_cols[2]:
            if st.button(f"Active Incidents [{inc_count}]", key="tab_incidents", type="primary", use_container_width=True):
                st.session_state["obsidian_tab"] = "Active Incidents"
                st.rerun()

    # Obsidian Workspace Container
    st.markdown('<div class="finnova-obsidian-workspace">', unsafe_allow_html=True)

    if active_tab == "DLQ Alerts":
        st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 1rem;'>Dead-Letter Queue (DLQ) Isolated Packets</h3>", unsafe_allow_html=True)
        if dlq_df.empty:
            st.info("No corrupted packets trapped in DLQ. All ingested packets are physically valid.")
        else:
            st.dataframe(
                dlq_df[["dlq_id", "ingested_at", "error_type", "error_detail", "source_topic", "raw_payload"]],
                use_container_width=True,
                height=400,
            )
        st.markdown('</div>', unsafe_allow_html=True)
        return

    elif active_tab == "All Racks":
        st.markdown("<h3 style='color: #FFFFFF; margin-bottom: 1rem;'>All Racks Telemetry Live Stream</h3>", unsafe_allow_html=True)
        if all_telemetry_df.empty:
            st.info("No telemetry records found.")
        else:
            display_cols = [
                "timestamp", "rack_id", "datacenter_region", "server_type", "cooling_type",
                "inlet_temperature_c", "cooling_efficiency", "power_consumption_kw", "pue",
                "cooling_stress_index", "thermal_velocity_delta_c"
            ]
            cols_avail = [c for c in display_cols if c in all_telemetry_df.columns]
            st.dataframe(all_telemetry_df[cols_avail], use_container_width=True, height=400)
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
            <span style="color: #A5A8C4; font-size: 0.85rem; font-weight: 600;">ACTIVE INCIDENT QUEUE</span>
            <span style="color: #5B4FE9; font-size: 0.75rem; font-weight: 700; background: rgba(91, 79, 233, 0.15); padding: 0.2rem 0.5rem; border-radius: 9999px;">Real-Time</span>
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
                is_selected = (selected_record and selected_record.get("incident_id") == inc_id)

                badge_bg = "#4A3BDC" if stype == "GPU" else "#2563EB"
                row_bg = "#5B4FE9" if is_selected else "#25283D"
                border_color = "#7B78D8" if is_selected else "rgba(255, 255, 255, 0.05)"

                row_html = f"""
                <div style="background: {row_bg}; border-radius: 14px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
                     border: 1px solid {border_color}; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 0.65rem;">
                        <span style="background: {badge_bg}; color: #FFFFFF; font-size: 0.68rem; font-weight: 800;
                              padding: 0.2rem 0.45rem; border-radius: 6px;">{stype[:3]}</span>
                        <div>
                            <div style="color: #FFFFFF; font-weight: 700; font-size: 0.85rem;">#{inc_id} · {rack_id}</div>
                            <div style="color: {'#DFDCFF' if is_selected else '#8E92BC'}; font-size: 0.72rem;">
                                {temp_c:.1f}°C inlet · {row.get('incident_status', 'Anomaly')}
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: rgba(255, 255, 255, 0.18); color: #FFFFFF; font-weight: 700;
                              font-size: 0.78rem; padding: 0.25rem 0.55rem; border-radius: 9999px;">{pue_val:.2f} PUE</span>
                    </div>
                </div>
                """
                st.markdown(row_html, unsafe_allow_html=True)
                if st.button(f"Inspect #{inc_id}", key=f"btn_sel_{inc_id}", use_container_width=True):
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

            # Card Header
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
                            <div style="font-size: 0.72rem; opacity: 0.8; font-weight: 600;">THERMAL & POWER METRICS</div>
                            <div style="font-size: 1.35rem; font-weight: 800; margin-top: 0.2rem;">{temp_c:.1f}°C <span style="font-size: 0.85rem; font-weight: 500;">Inlet</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                                Cooling Efficiency: <b>{cooling_eff:.2f}</b><br>
                                Power Draw: <b>{power_kw:.1f} kW</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 2: Shadow Model Verdict -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.8; font-weight: 600;">SHADOW MODEL VERDICT</div>
                            <div style="font-size: 1.35rem; font-weight: 800; margin-top: 0.2rem;">{chall_pue:.2f} <span style="font-size: 0.85rem; font-weight: 500;">XGB PUE</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                                Champion LGBM: <b>{champ_pue:.2f} PUE</b><br>
                                Top SHAP Driver: <b>{top_shap}</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 3: Financial & Carbon Burn -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.8; font-weight: 600;">FINANCIAL & CARBON BURN</div>
                            <div style="font-size: 1.35rem; font-weight: 800; margin-top: 0.2rem;">${waste_usd:.2f}/hr <span style="font-size: 0.85rem; font-weight: 500;">Waste</span></div>
                            <div style="font-size: 0.75rem; opacity: 0.9; margin-top: 0.25rem;">
                                Est. Carbon Penalty: <b>{plan.estimated_carbon_reduction_kg:.1f} kg CO2/hr</b>
                            </div>
                        </div>

                        <!-- Glass Sub-Card 4: SRE Copilot Action -->
                        <div class="finnova-glass-card">
                            <div style="font-size: 0.72rem; opacity: 0.8; font-weight: 600;">AGENTIC SRE ROOT-CAUSE</div>
                            <div style="font-size: 0.78rem; font-weight: 600; line-height: 1.3; margin-top: 0.2rem;">
                                {plan.root_cause_summary[:110]}...
                            </div>
                            <div style="font-size: 0.72rem; opacity: 0.9; margin-top: 0.25rem; color: #FFE79A;">
                                Action: {plan.recommended_cooling_action[:75]}...
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Summary Row & Execute Remediation CTA -->
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 1rem;">
                    <div style="display: flex; gap: 1.5rem; align-items: center;">
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">BASELINE PUE</div>
                            <div style="font-size: 1.05rem; font-weight: 700;">1.15</div>
                        </div>
                        <div style="color: rgba(255, 255, 255, 0.4); font-size: 1.2rem;">→</div>
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">CURRENT ANOMALY</div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #FFD4D5;">{actual_pue:.2f}</div>
                        </div>
                        <div style="color: rgba(255, 255, 255, 0.4); font-size: 1.2rem;">→</div>
                        <div>
                            <div style="font-size: 0.68rem; opacity: 0.75;">PROJECTED TARGET</div>
                            <div style="font-size: 1.05rem; font-weight: 700; color: #B3F5E7;">{plan.projected_pue_after_action:.2f}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Remediation Button Trigger
            if st.button("Execute Remediation / Normalize Cooling Loop", key="btn_remediate", type="primary", use_container_width=True):
                if on_remediate_callback:
                    on_remediate_callback(inc_id, plan.projected_pue_after_action)
                st.success(f"Remediation executed for #{inc_id}! Projected PUE reduced to {plan.projected_pue_after_action:.2f}.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
