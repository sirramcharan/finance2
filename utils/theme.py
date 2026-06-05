"""utils/theme.py — Shared CSS injection for glassmorphism dark theme."""
import streamlit as st

CSS = """
/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Background */
.stApp {
    background: radial-gradient(ellipse at top left, #1a0533 0%, #0a0a0f 50%, #001a33 100%) !important;
    background-attachment: fixed !important;
}

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1);
}
.glass-card:hover {
    border-color: rgba(255,255,255,0.20);
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
}

/* KPI cards */
.kpi-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    backdrop-filter: blur(20px);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    margin: 0.25rem 0;
}
.kpi-label {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.kpi-sublabel {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.35);
    margin-top: 0.2rem;
}

/* Accent colors */
.color-violet  { color: #7c3aed; }
.color-cyan    { color: #06b6d4; }
.color-emerald { color: #10b981; }
.color-amber   { color: #f59e0b; }
.color-red     { color: #ef4444; }
.color-gold    { color: #fbbf24; }

/* Alert cards */
.alert-emerald {
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}
.alert-amber {
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.3);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}
.alert-red {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}
.alert-cyan {
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.3);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}
.alert-violet {
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.3);
    border-radius: 12px; padding: 0.75rem 1rem; margin: 0.5rem 0;
}

/* Progress bars */
.progress-bar-container {
    background: rgba(255,255,255,0.08);
    border-radius: 999px; height: 8px; margin: 0.5rem 0;
}
.progress-bar-fill {
    height: 8px; border-radius: 999px;
    transition: width 0.8s ease;
}

/* Streamlit widget overrides */
.stNumberInput input, .stTextInput input, .stSelectbox select {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
}
div[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums !important;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,0.6) !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,58,237,0.3) !important;
    color: white !important;
    border-bottom: 2px solid #7c3aed !important;
}
.stButton > button {
    background: rgba(124,58,237,0.3) !important;
    border: 1px solid rgba(124,58,237,0.5) !important;
    border-radius: 10px !important;
    color: white !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(124,58,237,0.5) !important;
    transform: translateY(-1px) !important;
}
.stDataFrame { background: rgba(255,255,255,0.03) !important; }

/* Section headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Timeline */
.timeline-item {
    border-left: 2px solid rgba(124,58,237,0.5);
    padding-left: 1rem;
    margin-bottom: 1rem;
    position: relative;
}
.timeline-dot {
    width: 10px; height: 10px;
    background: #7c3aed;
    border-radius: 50%;
    position: absolute; left: -6px; top: 4px;
}

/* Page title */
.page-title {
    font-size: 1.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #7c3aed, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}

/* Edit hint */
.edit-hint {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.3);
    margin-top: 0.2rem;
}

/* Comparison table */
.compare-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}
.compare-table th {
    background: rgba(124,58,237,0.2);
    padding: 0.6rem 1rem;
    text-align: left;
    color: rgba(255,255,255,0.9);
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.compare-table td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.8);
}
.compare-table tr:hover td {
    background: rgba(255,255,255,0.03);
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def kpi_card(label: str, value: str, sublabel: str = "", color: str = "#06b6d4") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-sublabel">{sublabel}</div>
    </div>"""


def alert_card(alert_type: str, message: str) -> str:
    return f'<div class="alert-{alert_type}">{message}</div>'


def progress_bar(pct: float, color: str = "#10b981") -> str:
    pct = min(100, max(0, pct))
    return f"""
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width:{pct}%;background:{color};"></div>
    </div>"""


def svg_arc(score: int, size: int = 160) -> str:
    """Render a circular arc progress indicator for health score."""
    import math
    r = 60
    cx = cy = size // 2
    circumference = 2 * math.pi * r
    offset = circumference * (1 - score / 100)

    if score >= 80:
        color = "#10b981"
    elif score >= 60:
        color = "#06b6d4"
    elif score >= 40:
        color = "#f59e0b"
    else:
        color = "#ef4444"

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="12"/>
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="{color}" stroke-width="12"
              stroke-linecap="round"
              stroke-dasharray="{circumference:.2f}"
              stroke-dashoffset="{offset:.2f}"
              transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy - 6}" text-anchor="middle"
            fill="white" font-size="22" font-weight="700">{score}</text>
      <text x="{cx}" y="{cy + 14}" text-anchor="middle"
            fill="rgba(255,255,255,0.5)" font-size="10">/100</text>
    </svg>"""


def svg_ring(progress: float, label: str = "", size: int = 110) -> str:
    """SVG circular progress ring for savings goals."""
    import math
    r = 45
    cx = cy = size // 2
    circumference = 2 * math.pi * r
    offset = circumference * (1 - min(1.0, max(0.0, progress)))
    pct_int = int(progress * 100)

    if progress >= 1.0:
        color = "#10b981"
    elif progress >= 0.5:
        color = "#06b6d4"
    else:
        color = "#7c3aed"

    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10"/>
      <circle cx="{cx}" cy="{cy}" r="{r}"
              fill="none" stroke="{color}" stroke-width="10"
              stroke-linecap="round"
              stroke-dasharray="{circumference:.2f}"
              stroke-dashoffset="{offset:.2f}"
              transform="rotate(-90 {cx} {cy})"/>
      <text x="{cx}" y="{cy + 5}" text-anchor="middle"
            fill="white" font-size="14" font-weight="700">{pct_int}%</text>
    </svg>"""
