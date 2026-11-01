"""Finnova Top Navigation, Action Header & 4 Asymmetric Bento KPI Cards.

Implements pixel-accurate Finnova visual components:
- Top Floating Pill Navbar (5 tabs + runtime mode pill)
- Action Row with Scenario Injector
- Bento Card 1: Thermal Alerts + Server Rack Thermal Health Bar
- Bento Card 2: Facility Power & PUE + 7 Vertical Gradient Bars (#5B4FE9 -> #DFDCFF)
- Bento Card 3: PSI Drift + Connected Node-Line Sparkline (o-o-o)
- Bento Card 4: Model Regime + 3 Vertical Mini-Cards (LGBM, XGBoost highlighted, IsoForest) + Hot-Swap Now CTA
"""

from typing import Any, Dict, List
import streamlit as st


def render_top_navbar(active_tab: str, runtime_mode_label: str = "Cloud Stream"):
    """Renders Zone 1: Top Floating Pill Navbar."""
    is_docker = "Docker" in runtime_mode_label
    status_bg = "#E6F8F5" if is_docker else "#EFEFFC"
    status_color = "#12A594" if is_docker else "#5B4FE9"
    status_dot = "🟢" if is_docker else "🟣"

    html = f"""
    <div class="finnova-navbar-container">
        <div class="finnova-brand">
            <div class="finnova-brand-logo">AETHER-DC</div>
            <span class="finnova-brand-badge">GreenOps AI</span>
            <span style="font-size: 0.75rem; color: #6E7191; font-weight: 500;">v2.4.0</span>
        </div>

        <div class="finnova-nav-capsule">
            <span class="finnova-nav-tab {'active' if active_tab == 'Telemetry Hub' else ''}">+ Telemetry Hub</span>
            <span class="finnova-nav-tab {'active' if active_tab == 'Lakehouse & DLQ' else ''}">Lakehouse & DLQ</span>
            <span class="finnova-nav-tab {'active' if active_tab == 'Drift & MLOps' else ''}">Drift & MLOps</span>
            <span class="finnova-nav-tab {'active' if active_tab == 'SRE Copilot' else ''}">SRE Copilot</span>
            <span class="finnova-nav-tab {'active' if active_tab == 'Prometheus & Infra' else ''}">Prometheus & Infra</span>
        </div>

        <div class="finnova-nav-right">
            <div class="finnova-status-pill" style="background: {status_bg}; color: {status_color}; border-color: {status_color}33;">
                <span>{status_dot}</span>
                <span>{runtime_mode_label}</span>
            </div>
            <div class="finnova-status-pill" style="background: #FFF7EB; color: #D97706; border-color: #FDE68A;">
                <span>⚡</span>
                <span>Prometheus :9090</span>
            </div>
            <div class="finnova-avatar" title="Maheza Novrayuda (Lead Engineer)">MN</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_action_header(active_tab: str):
    """Renders Zone 2: Action Header Row."""
    descriptions = {
        "Telemetry Hub": "Real-time GPU rack telemetry, PUE efficiency, and MLOps drift control in one place.",
        "Lakehouse & DLQ": "DuckDB Medallion Lakehouse (Bronze -> Silver -> Gold) and Pydantic v2 Dead-Letter Queue.",
        "Drift & MLOps": "10-bin Population Stability Index (PSI), Kolmogorov-Smirnov test, and Shadow Evaluation.",
        "SRE Copilot": "Agentic SRE Incident Root-Cause Analysis, TreeSHAP, and counterfactual cooling simulation.",
        "Prometheus & Infra": "Production Prometheus telemetry metrics, scrape targets, and dual-mode architecture.",
    }
    desc = descriptions.get(active_tab, descriptions["Telemetry Hub"])

    html = f"""
    <div class="finnova-header-row">
        <div>
            <h1 class="finnova-page-title">{active_tab}</h1>
            <p class="finnova-page-subtitle">{desc}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_bento_kpi_cards(
    kpis: Dict[str, Any],
    drift_data: Dict[str, Any],
    active_champion: str,
    challenger_name: str,
    on_hotswap_clicked=None,
):
    """Renders Zone 3: 4 Asymmetric Bento KPI Cards with micro-visualizations."""
    cols = st.columns(4)

    # ----------------------------------------------------
    # BENTO CARD 1: Thermal & DLQ Alerts + Health Bar
    # ----------------------------------------------------
    with cols[0]:
        alerts_count = kpis.get("active_alerts_count", 0)
        dlq_count = kpis.get("dlq_count", 0)

        card1_html = f"""
        <div class="finnova-bento-card">
            <div>
                <div class="finnova-bento-header">
                    <span class="finnova-bento-title">Active Thermal & DLQ Alerts</span>
                    <span class="finnova-bento-icon-badge" style="background: #FFF0F0; color: #E5484D;">⚠️</span>
                </div>
                <div class="finnova-bento-metric">{alerts_count} Racks</div>
                <div class="finnova-bento-delta delta-danger">
                    <span>↑ 12.5%</span>
                    <span style="color: #6E7191; font-weight: 500;">· {dlq_count} DLQ trapped</span>
                </div>
            </div>

            <!-- Server Rack Thermal Health Visual Bar -->
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: #6E7191; margin-bottom: 0.3rem;">
                    <span>Healthy (18)</span>
                    <span>Warning (4)</span>
                    <span>Critical (2)</span>
                </div>
                <div style="display: flex; height: 10px; border-radius: 9999px; overflow: hidden; background: #EAE8F6; gap: 2px;">
                    <div style="flex: 18; background: #12A594; border-radius: 4px;"></div>
                    <div style="flex: 4; background: #F59E0B; border-radius: 4px;"></div>
                    <div style="flex: 2; background: #E5484D; border-radius: 4px;"></div>
                </div>
                <div style="font-size: 0.65rem; color: #8E92BC; margin-top: 0.35rem; text-align: center;">
                    24 Racks Online · ASHRAE 32°C Cap
                </div>
            </div>
        </div>
        """
        st.markdown(card1_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # BENTO CARD 2: Facility Power & Mean PUE + 7 Vertical Bars
    # ----------------------------------------------------
    with cols[1]:
        mean_pue = kpis.get("mean_pue", 1.18)
        total_kw = kpis.get("total_power_kw", 482.6)
        clusters = kpis.get("cluster_pue_bars", [
            {"cluster_label": "APAC-GPU", "cluster_pue": 1.45},
            {"cluster_label": "ME-CMP", "cluster_pue": 1.35},
            {"cluster_label": "NA-GPU", "cluster_pue": 1.25},
            {"cluster_label": "EU-CMP", "cluster_pue": 1.18},
            {"cluster_label": "APAC-EDG", "cluster_pue": 1.15},
            {"cluster_label": "NA-STR", "cluster_pue": 1.12},
            {"cluster_label": "EU-LIQ", "cluster_pue": 1.09},
        ])

        bars_html = ""
        for item in clusters[:7]:
            lbl = item.get("cluster_label", "RACK")[-7:]
            pue_val = float(item.get("cluster_pue", 1.20))
            # Height normalized between 25px and 65px
            norm_h = int(max(20, min(65, (pue_val - 1.0) * 100)))
            bars_html += f"""
            <div class="finnova-bar-wrapper">
                <div class="finnova-bar-pillar" style="height: {norm_h}px;" title="{item.get('cluster_label')}: {pue_val:.2f} PUE"></div>
                <span class="finnova-bar-label">{lbl}</span>
            </div>
            """

        card2_html = f"""
        <div class="finnova-bento-card">
            <div>
                <div class="finnova-bento-header">
                    <span class="finnova-bento-title">Facility Power & Mean PUE</span>
                    <span class="finnova-bento-icon-badge" style="background: #EFEFFC; color: #5B4FE9;">⚡</span>
                </div>
                <div class="finnova-bento-metric">{mean_pue:.2f} PUE</div>
                <div class="finnova-bento-delta delta-success">
                    <span>↓ 4.2%</span>
                    <span style="color: #6E7191; font-weight: 500;">· {total_kw:.1f} kW total load</span>
                </div>
            </div>

            <!-- 7 Vertical Gradient Bars -->
            <div class="finnova-bars-container">
                {bars_html}
            </div>
        </div>
        """
        st.markdown(card2_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # BENTO CARD 3: Feature Drift (PSI) & Latency + Node-Line Sparkline
    # ----------------------------------------------------
    with cols[2]:
        max_psi = drift_data.get("max_psi", 0.084)
        is_drift = max_psi >= 0.20
        psi_delta_class = "delta-danger" if is_drift else "delta-success"
        psi_status = "Critical Drift" if is_drift else "Stable Distribution"

        # SVG Connected Node-Line Sparkline (o-o-o)
        sparkline_svg = """
        <svg viewBox="0 0 200 45" style="width: 100%; height: 45px; overflow: visible;">
            <defs>
                <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#5B4FE9" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="#5B4FE9" stop-opacity="0.0"/>
                </linearGradient>
            </defs>
            <path d="M 5,32 Q 35,15 70,26 T 135,12 T 195,18" fill="none" stroke="#5B4FE9" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="5" cy="32" r="3.5" fill="#FFFFFF" stroke="#5B4FE9" stroke-width="2.5"/>
            <circle cx="70" cy="26" r="3.5" fill="#FFFFFF" stroke="#5B4FE9" stroke-width="2.5"/>
            <circle cx="135" cy="12" r="3.5" fill="#FFFFFF" stroke="#5B4FE9" stroke-width="2.5"/>
            <circle cx="195" cy="18" r="4.5" fill="#5B4FE9" stroke="#FFFFFF" stroke-width="2.5"/>
        </svg>
        """

        card3_html = f"""
        <div class="finnova-bento-card">
            <div>
                <div class="finnova-bento-header">
                    <span class="finnova-bento-title">Feature Drift (PSI) & Latency</span>
                    <span class="finnova-bento-icon-badge" style="background: #EFEFFC; color: #5B4FE9;">⏱</span>
                </div>
                <div class="finnova-bento-metric">{max_psi:.3f} PSI</div>
                <div class="finnova-bento-delta {psi_delta_class}">
                    <span>{psi_status}</span>
                    <span style="color: #6E7191; font-weight: 500;">· 8.4ms latency</span>
                </div>
            </div>

            <!-- Connected Node-Line Sparkline -->
            <div style="margin-top: 0.5rem;">
                {sparkline_svg}
                <div style="display: flex; justify-content: space-between; font-size: 0.65rem; color: #8E92BC; margin-top: 0.2rem;">
                    <span>T-4h</span>
                    <span>T-2h</span>
                    <span>Live Window</span>
                </div>
            </div>
        </div>
        """
        st.markdown(card3_html, unsafe_allow_html=True)

    # ----------------------------------------------------
    # BENTO CARD 4: Model & Cooling Regime + 3 Mini Cards & Hot-Swap Button
    # ----------------------------------------------------
    with cols[3]:
        is_lgbm = "lgbm" in active_champion

        card4_html = f"""
        <div class="finnova-bento-card">
            <div>
                <div class="finnova-bento-header">
                    <span class="finnova-bento-title">Model & Cooling Regime</span>
                    <span class="finnova-bento-icon-badge" style="background: #E6F8F5; color: #12A594;">↗</span>
                </div>
                <div class="finnova-bento-metric">+18.4% Saved</div>
                <div class="finnova-bento-delta delta-success">
                    <span>98.4% Rolling F1</span>
                    <span style="color: #6E7191; font-weight: 500;">· Shadow Arena</span>
                </div>
            </div>

            <!-- 3 Side-by-Side Mini-Cards -->
            <div>
                <div class="finnova-mini-cards-row">
                    <div class="finnova-mini-card {'active-challenger' if is_lgbm else ''}">
                        <div>LGBM</div>
                        <div class="finnova-mini-card-sub">{'Champion' if is_lgbm else 'Shadow'}</div>
                    </div>
                    <div class="finnova-mini-card {'active-challenger' if not is_lgbm else ''}">
                        <div>XGBoost</div>
                        <div class="finnova-mini-card-sub">{'Champion' if not is_lgbm else 'Challenger'}</div>
                    </div>
                    <div class="finnova-mini-card">
                        <div>IsoForest</div>
                        <div class="finnova-mini-card-sub">Guard</div>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(card4_html, unsafe_allow_html=True)
