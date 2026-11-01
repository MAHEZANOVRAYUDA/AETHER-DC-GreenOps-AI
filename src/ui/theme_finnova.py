"""Finnova UI Theme & Custom CSS Generator for AETHER-DC.

Translates Finnova visual tokens into Streamlit:
- Alabaster Lavender-White canvas (#F8F9FE)
- Google Font 'Plus Jakarta Sans' & 'Inter'
- Unified Top Floating Pill Navbar Capsule (#161825, rounded-full)
- 4 Asymmetric Bento KPI Cards with crisp 1px borders (#ECEEF6)
- Obsidian Split-View Master-Detail Workspace (#161825, radius 28px)
- Periwinkle-Indigo Inspector Card (#5E5CE6) with translucent frosted glass sub-cards
- Custom styled button overrides, pill filters, and seamless responsive layout.
"""

import textwrap
import streamlit as st

FINNOVA_CSS = textwrap.dedent("""
<style>
/* 1. Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* 2. Global Document Reset & Base Styling */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #F8F9FE !important;
    color: #161825 !important;
}

/* Hide Default Streamlit Header, Footer, and Sidebar */
header[data-testid="stHeader"] {
    display: none !important;
}
footer {
    display: none !important;
}
[data-testid="stSidebar"] {
    display: none !important;
}

/* Main Block Container Dimensions & Fluid Padding */
.main .block-container {
    max-width: 1440px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    padding-left: 2.25rem !important;
    padding-right: 2.25rem !important;
}

/* 3. Top Floating Navbar (Zone 1) */
.finnova-navbar-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 1.2rem;
    padding: 0.25rem 0;
}

.finnova-brand-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.finnova-brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: linear-gradient(135deg, #5B4FE9 0%, #7B78D8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 1.15rem;
    box-shadow: 0 4px 12px rgba(91, 79, 233, 0.3);
}

.finnova-brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #161825;
    line-height: 1.1;
}

.finnova-brand-subtitle {
    font-size: 0.72rem;
    color: #6E7191;
    font-weight: 500;
}

.finnova-badge-capsule {
    background: #EFEFFC;
    color: #4A3BDC;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    border: 1px solid #DFDCFF;
}

.finnova-counter-pill {
    background: #F4F3FA;
    color: #161825;
    font-size: 0.75rem;
    font-weight: 800;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    border: 1px solid #EAE8F6;
}

/* Top Dark Segmented Control Styling (Using actual Streamlit testid: stButtonGroup) */
div[data-testid="stButtonGroup"] {
    background-color: #161825 !important;
    padding: 4px 6px !important;
    border-radius: 9999px !important;
    display: inline-flex !important;
    justify-content: center !important;
    box-shadow: 0 4px 20px rgba(22, 24, 37, 0.16) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    gap: 4px !important;
}
div[data-testid="stButtonGroup"] button {
    border-radius: 9999px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #A5A8C4 !important;
    border: none !important;
    background: transparent !important;
    padding: 6px 16px !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
div[data-testid="stButtonGroup"] button:hover {
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.08) !important;
}
div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] {
    background-color: #5B4FE9 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(91, 79, 233, 0.5) !important;
}

/* Navbar Right Icon Cluster & Avatar */
.finnova-nav-cluster {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.finnova-icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid #ECEEF6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6E7191;
    font-size: 0.85rem;
    box-shadow: 0 2px 6px rgba(22, 24, 37, 0.02);
    position: relative;
    cursor: default;
}
.finnova-icon-dot {
    position: absolute;
    top: 6px;
    right: 7px;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #E5484D;
}

.finnova-status-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid #ECEEF6;
    background: #FFFFFF;
}

.finnova-avatar-circle {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5B4FE9 0%, #8E8BEE 100%);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(91, 79, 233, 0.3);
    border: 2px solid #FFFFFF;
}

/* 4. Action Header Row (Zone 2) */
.finnova-action-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.35rem;
    margin-top: 0.2rem;
}
.finnova-header-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.finnova-back-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 1px solid #ECEEF6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #161825;
    font-size: 1.1rem;
    box-shadow: 0 2px 6px rgba(22, 24, 37, 0.03);
    cursor: pointer;
}
.finnova-page-title {
    font-size: 1.95rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #161825;
    margin: 0;
    line-height: 1.15;
}
.finnova-page-subtitle {
    font-size: 0.85rem;
    color: #6E7191;
    margin-top: 0.2rem;
    margin-bottom: 0;
}

/* 5. 4 Asymmetric Bento KPI Cards (Zone 3) */
.finnova-bento-card {
    background: #FFFFFF;
    border: 1px solid #ECEEF6;
    border-radius: 22px;
    padding: 1.35rem 1.45rem;
    height: 255px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(22, 24, 37, 0.03);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.finnova-bento-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 26px rgba(22, 24, 37, 0.06);
}

.finnova-bento-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.finnova-bento-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #6E7191;
}
.finnova-bento-icon-badge {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
}
.finnova-bento-metric {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #161825;
    margin-top: 0.35rem;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
}
.finnova-bento-delta {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 0.3rem;
}
.delta-danger { color: #E5484D; }
.delta-success { color: #12A594; }
.delta-neutral { color: #5B4FE9; }

/* Bento 2: 7 Vertical Gradient Bars */
.finnova-bars-container {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 75px;
    width: 100%;
    padding-top: 0.25rem;
}
.finnova-bar-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
    flex: 1;
}
.finnova-bar-pillar {
    width: 15px;
    border-radius: 6px;
    background: linear-gradient(180deg, #5B4FE9 0%, #DFDCFF 100%);
    transition: height 0.4s ease;
}
.finnova-bar-label {
    font-size: 0.65rem;
    color: #8E92BC;
    font-weight: 600;
}

/* Bento 4: 3 Mini Cards & CTA */
.finnova-mini-cards-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    width: 100%;
    margin-top: 0.25rem;
    margin-bottom: 0.5rem;
}
.finnova-mini-card {
    flex: 1;
    padding: 0.45rem 0.25rem;
    border-radius: 12px;
    background: #F4F3FA;
    text-align: center;
    font-size: 0.72rem;
    font-weight: 700;
    color: #161825;
    border: 1px solid transparent;
}
.finnova-mini-card.active-challenger {
    background: linear-gradient(135deg, #5B4FE9 0%, #7B78D8 100%);
    color: #FFFFFF;
    box-shadow: 0 3px 10px rgba(91, 79, 233, 0.3);
}
.finnova-mini-card-sub {
    font-size: 0.58rem;
    font-weight: 500;
    opacity: 0.85;
}

/* 6. Filter Bar (Zone 4) */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border-radius: 9999px !important;
    background-color: #FFFFFF !important;
    border: 1px solid #ECEEF6 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 6px rgba(22, 24, 37, 0.02) !important;
}
div[data-testid="stTextInput"] input {
    border-radius: 9999px !important;
    background-color: #FFFFFF !important;
    border: 1px solid #ECEEF6 !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 2px 6px rgba(22, 24, 37, 0.02) !important;
}

/* 7. Obsidian Split-View Master-Detail Workspace (Zone 5) */
/* Targets ONLY the specific layout wrapper enclosing the obsidian workspace anchor */
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) {
    background-color: #161825 !important;
    border-radius: 28px !important;
    padding: 1.85rem !important;
    margin-top: 1.25rem !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    box-shadow: 0 16px 48px rgba(22, 24, 37, 0.22) !important;
}
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) > div {
    background-color: transparent !important;
    border: none !important;
}

/* Obsidian Notch Styled Button Group */
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) div[data-testid="stButtonGroup"] {
    background-color: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
}
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) div[data-testid="stButtonGroup"] button[data-testid="stBaseButton-segmented_controlActive"] {
    background-color: #5E5CE6 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 10px rgba(94, 92, 230, 0.5) !important;
}

/* Master Queue Row Buttons inside Obsidian Workspace */
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) div[data-testid="stColumn"]:first-child button[data-testid="stBaseButton-secondary"] {
    text-align: left !important;
    justify-content: space-between !important;
    padding: 0.85rem 1.1rem !important;
    margin-bottom: 0.45rem !important;
    font-size: 0.825rem !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #E2E4F0 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) div[data-testid="stColumn"]:first-child button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
}
div[data-testid="stLayoutWrapper"]:has(.obsidian-workspace-marker) div[data-testid="stColumn"]:first-child button[data-testid="stBaseButton-primary"] {
    text-align: left !important;
    justify-content: space-between !important;
    padding: 0.85rem 1.1rem !important;
    margin-bottom: 0.45rem !important;
    font-size: 0.825rem !important;
    font-weight: 700 !important;
    border-radius: 14px !important;
    background: linear-gradient(90deg, #5B4FE9 0%, #7B78D8 100%) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    box-shadow: 0 4px 16px rgba(91, 79, 233, 0.45) !important;
}

/* Right Detail Inspector Card (Periwinkle-Indigo) */
.finnova-indigo-inspector {
    background: linear-gradient(135deg, #5E5CE6 0%, #6460D9 50%, #7673DE 100%);
    border-radius: 22px;
    padding: 1.65rem;
    color: #FFFFFF;
    box-shadow: 0 10px 30px rgba(94, 92, 230, 0.32);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 485px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.finnova-glass-card {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 0.95rem 1rem;
    color: #FFFFFF;
}

/* Primary Button Styling (Vibrant Indigo Pill) */
button[kind="primary"] {
    background: #5B4FE9 !important;
    border-radius: 9999px !important;
    font-weight: 700 !important;
    border: none !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(91, 79, 233, 0.35) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    background: #4A3BDC !important;
    box-shadow: 0 6px 18px rgba(91, 79, 233, 0.5) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button Styling */
button[kind="secondary"] {
    border-radius: 9999px !important;
    font-weight: 600 !important;
    border: 1px solid #ECEEF6 !important;
}

/* Dataframe Clean Styling */
div[data-testid="stDataFrame"] {
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #ECEEF6 !important;
}
</style>
""").strip()


def inject_finnova_theme():
    """Injects custom Finnova styling into Streamlit application using native st.html."""
    st.html(FINNOVA_CSS)
