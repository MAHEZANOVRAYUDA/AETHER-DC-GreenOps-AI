"""Finnova UI Theme & Custom CSS Generator for AETHER-DC.

Translates Finnova visual tokens into Streamlit:
- Alabaster Lavender-White canvas (#FBFAFF)
- Google Font 'Plus Jakarta Sans' & 'Inter'
- 4 Asymmetric Bento KPI Cards with crisp 1px borders (#EAE8F6)
- Obsidian Split-View Master-Detail Workspace (#1E2132, radius 28px)
- Periwinkle-Indigo Inspector Card (#5E5CE6) with translucent glass sub-cards
- Hides default Streamlit chrome & sidebar.
"""

FINNOVA_CSS = """
<style>
/* 1. Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* 2. Global Document Reset & Base Styling */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #FBFAFF !important;
    color: #161825;
}

/* Hide Streamlit Header, Footer, and Default Sidebar */
header[data-testid="stHeader"] {
    display: none !important;
}
footer {
    display: none !important;
}
[data-testid="stSidebar"] {
    display: none !important;
}

/* Adjust Main Block Container Padding */
.main .block-container {
    max-width: 1440px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 3. Zone 1: Top Floating Pill Navbar */
.finnova-navbar-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-bottom: 1.5rem;
    padding: 0.25rem 0;
}

.finnova-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.finnova-brand-logo {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #161825;
}
.finnova-brand-badge {
    background: #EFEFFC;
    color: #4A3BDC;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
}

.finnova-nav-capsule {
    display: inline-flex;
    align-items: center;
    background-color: #161825;
    padding: 0.35rem 0.45rem;
    border-radius: 9999px;
    gap: 0.35rem;
    box-shadow: 0 4px 16px rgba(22, 24, 37, 0.12);
}
.finnova-nav-tab {
    padding: 0.45rem 1.15rem;
    border-radius: 9999px;
    font-size: 0.825rem;
    font-weight: 600;
    color: #A5A8C4;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    background: transparent;
}
.finnova-nav-tab.active {
    background-color: #4A3BDC;
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(74, 59, 220, 0.35);
}

.finnova-nav-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.finnova-status-pill {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.8rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid #EAE8F6;
    background: #FFFFFF;
}
.finnova-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4A3BDC, #7B78D8);
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.85rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 4. Zone 2: Action Header Row */
.finnova-header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 1.5rem;
}
.finnova-page-title {
    font-size: 1.875rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #161825;
    margin: 0;
    line-height: 1.2;
}
.finnova-page-subtitle {
    font-size: 0.875rem;
    color: #6E7191;
    margin-top: 0.3rem;
    margin-bottom: 0;
}

/* 5. Zone 3: 4 Asymmetric Bento KPI Cards */
.finnova-bento-card {
    background: #FFFFFF;
    border: 1px solid #EAE8F6;
    border-radius: 22px;
    padding: 1.35rem;
    height: 250px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(22, 24, 37, 0.03);
    position: relative;
    overflow: hidden;
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
    font-size: 0.75rem;
    font-weight: 700;
}
.finnova-bento-metric {
    font-size: 1.85rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #161825;
    margin-top: 0.35rem;
    font-variant-numeric: tabular-nums;
}
.finnova-bento-delta {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 0.2rem;
}
.delta-danger { color: #E5484D; }
.delta-success { color: #12A594; }
.delta-neutral { color: #5B4FE9; }

/* Bento 2: 7 Vertical Gradient Bars */
.finnova-bars-container {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 80px;
    width: 100%;
    padding-top: 0.5rem;
}
.finnova-bar-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    flex: 1;
}
.finnova-bar-pillar {
    width: 14px;
    border-radius: 6px;
    background: linear-gradient(180deg, #5B4FE9 0%, #DFDCFF 100%);
    transition: height 0.4s ease;
}
.finnova-bar-label {
    font-size: 0.65rem;
    color: #8E92BC;
    font-weight: 600;
}

/* Bento 4: 3 Side-by-Side Mini Cards */
.finnova-mini-cards-row {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    width: 100%;
    margin-top: 0.6rem;
}
.finnova-mini-card {
    flex: 1;
    padding: 0.45rem 0.35rem;
    border-radius: 12px;
    background: #F4F3FA;
    text-align: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: #161825;
    border: 1px solid transparent;
}
.finnova-mini-card.active-challenger {
    background: linear-gradient(135deg, #5B4FE9 0%, #7B78D8 100%);
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(91, 79, 233, 0.3);
}
.finnova-mini-card-sub {
    font-size: 0.58rem;
    font-weight: 500;
    opacity: 0.8;
}

/* 6. Zone 5: Obsidian Split-View Master-Detail Workspace */
.finnova-obsidian-workspace {
    background: #1E2132;
    border-radius: 28px;
    padding: 1.85rem;
    margin-top: 1.5rem;
    box-shadow: 0 12px 36px rgba(22, 24, 37, 0.16);
    position: relative;
}

.finnova-notch-bar {
    display: flex;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.finnova-notch-capsule {
    background: #161825;
    padding: 0.35rem 0.5rem;
    border-radius: 9999px;
    display: inline-flex;
    gap: 0.4rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.finnova-notch-tab {
    padding: 0.4rem 1.15rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #A5A8C4;
    cursor: pointer;
}
.finnova-notch-tab.active {
    background: #5B4FE9;
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(91, 79, 233, 0.4);
}

/* Incident Queue Row (Left Pane) */
.finnova-queue-row {
    background: #25283D;
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.04);
    cursor: pointer;
    transition: all 0.2s ease;
}
.finnova-queue-row:hover {
    background: #2E324B;
    transform: translateX(2px);
}
.finnova-queue-row.selected-active {
    background: #5B4FE9 !important;
    border-color: #7B78D8 !important;
    box-shadow: 0 4px 14px rgba(91, 79, 233, 0.4);
}

/* Right Detail Inspector Card (Periwinkle-Indigo) */
.finnova-indigo-inspector {
    background: linear-gradient(135deg, #5E5CE6 0%, #6D6ACF 55%, #7B78D8 100%);
    border-radius: 22px;
    padding: 1.65rem;
    color: #FFFFFF;
    box-shadow: 0 8px 24px rgba(94, 92, 230, 0.28);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 440px;
}

.finnova-glass-card {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.24);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 1rem;
    color: #FFFFFF;
}

.finnova-white-pill-btn {
    background: #FFFFFF !important;
    color: #4A3BDC !important;
    font-weight: 700 !important;
    border-radius: 9999px !important;
    padding: 0.55rem 1.45rem !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
    cursor: pointer !important;
    font-size: 0.85rem !important;
    transition: transform 0.15s ease !important;
}
.finnova-white-pill-btn:hover {
    transform: scale(1.02);
}

/* Streamlit button style overrides for pills */
div.stButton > button {
    border-radius: 9999px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
</style>
"""


def inject_finnova_theme():
    """Injects custom Finnova styling into Streamlit application."""
    import streamlit as st
    st.markdown(FINNOVA_CSS, unsafe_allow_html=True)
