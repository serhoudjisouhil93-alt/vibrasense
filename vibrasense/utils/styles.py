"""
Industrial Oil & Gas Dashboard Styles
Dark theme with warning indicators and real-time monitoring feel
"""

import streamlit as st


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

    /* ── Base ─────────────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        background-color: #060912 !important;
        color: #8ab0d0 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    .stApp { background: #060912 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* ── Hide Streamlit top toolbar & eliminate header gap ───────────── */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    #MainMenu,
    header[data-testid="stHeader"] { visibility: hidden !important; height: 0 !important; }
    .stApp > header { display: none !important; }
    .appview-container .main .block-container { padding-top: 0 !important; }
    [data-testid="stSidebar"] {
        background: #08091a !important;
        border-right: 1px solid #1a2540 !important;
    }
    [data-testid="stSidebar"] * { color: #8ab0d0 !important; }
    .stButton > button {
        background: #0a1020 !important;
        border: 1px solid #1a3050 !important;
        color: #00d4ff !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 12px !important;
        letter-spacing: 1px !important;
        border-radius: 4px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        border-color: #00d4ff !important;
        box-shadow: 0 0 12px #00d4ff44 !important;
        background: #00d4ff11 !important;
    }
    [data-testid="baseButton-primary"] {
        background: #00d4ff15 !important;
        border-color: #00d4ff66 !important;
        color: #00d4ff !important;
    }
    .stSlider [data-baseweb="slider"] { accent-color: #00d4ff; }
    .stSelectbox, .stRadio { color: #8ab0d0 !important; }
    .stRadio label { color: #8ab0d0 !important; font-family: 'Share Tech Mono', monospace !important; font-size: 12px !important; }
    div[data-baseweb="select"] > div { background: #0a1020 !important; border-color: #1a2540 !important; color: #8ab0d0 !important; }
    hr { border-color: #1a2540 !important; }
    ::-webkit-scrollbar { width: 4px; background: #060912; }
    ::-webkit-scrollbar-thumb { background: #1a2540; border-radius: 2px; }

    /* ── Animations ───────────────────────────────────────────────────── */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.2; }
    }
    @keyframes pulse-border {
        0%, 100% { box-shadow: 0 0 8px #ff224444; }
        50%       { box-shadow: 0 0 24px #ff224488; }
    }
    .blink { animation: blink 1.4s infinite; }

    /* ── Header ───────────────────────────────────────────────────────── */
    .header-bar {
        display: flex; align-items: center; justify-content: space-between;
        background: linear-gradient(180deg, #0c1020 0%, #060912 100%);
        border-bottom: 1px solid #1a2540;
        padding: 12px 24px; margin-bottom: 0;
    }
    .header-left  { display: flex; align-items: center; gap: 14px; }
    .header-right { display: flex; align-items: center; gap: 14px; }
    .header-icon {
        width: 40px; height: 40px; border-radius: 8px;
        background: linear-gradient(135deg, #00d4ff22, #00d4ff44);
        border: 1px solid #00d4ff66;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
    }
    .header-title {
        color: #00d4ff; font-size: 20px; font-weight: 700;
        letter-spacing: 4px; font-family: 'Share Tech Mono', monospace;
    }
    .header-sub {
        color: #2a4060; font-size: 10px; letter-spacing: 2px;
        font-family: 'Share Tech Mono', monospace;
    }
    .status-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #00ff88; box-shadow: 0 0 8px #00ff88;
    }
    .status-text { color: #00ff88; font-size: 11px; letter-spacing: 2px; font-family: 'Share Tech Mono', monospace; }
    .header-badges { display: flex; gap: 6px; }
    .badge {
        padding: 3px 8px; border-radius: 3px; font-size: 9px;
        letter-spacing: 1px; font-family: 'Share Tech Mono', monospace;
    }
    .badge-blue   { background: #00d4ff15; border: 1px solid #00d4ff44; color: #00d4ff; }
    .badge-green  { background: #00ff8815; border: 1px solid #00ff8844; color: #00ff88; }
    .badge-orange { background: #ff6b3515; border: 1px solid #ff6b3544; color: #ff6b35; }

    /* ── Alert Banner ─────────────────────────────────────────────────── */
    .alert-banner {
        display: flex; align-items: center; gap: 14px;
        background: #ff224408; border: 1px solid #ff2244;
        border-radius: 4px; padding: 10px 18px; margin: 10px 8px;
        animation: pulse-border 2s infinite;
    }
    .alert-icon  { font-size: 18px; color: #ff2244; }
    .alert-text  { flex: 1; color: #ff8888; font-size: 12px; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }
    .alert-badge {
        padding: 4px 10px; border-radius: 3px; font-size: 10px;
        font-family: 'Share Tech Mono', monospace; letter-spacing: 1px;
        border: 1px solid; white-space: nowrap;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────── */
    .sidebar-title {
        color: #00d4ff; font-size: 13px; letter-spacing: 3px;
        font-family: 'Share Tech Mono', monospace; margin-bottom: 16px;
        padding-bottom: 8px; border-bottom: 1px solid #1a2540;
    }
    .sidebar-section {
        color: #2a4060; font-size: 10px; letter-spacing: 2px;
        font-family: 'Share Tech Mono', monospace;
        margin: 14px 0 8px; border-top: 1px solid #1a2540; padding-top: 10px;
    }
    .log-box {
        background: #040608; border: 1px solid #1a2540; border-radius: 4px;
        padding: 10px; font-family: 'Share Tech Mono', monospace;
        font-size: 10px; color: #3a6090; max-height: 180px; overflow-y: auto;
    }
    .log-box pre { margin: 0; white-space: pre-wrap; word-break: break-all; }
    .sidebar-footer {
        margin-top: 20px; padding-top: 12px; border-top: 1px solid #1a2540;
        font-family: 'Share Tech Mono', monospace; font-size: 9px;
        color: #1a2540; text-align: center; line-height: 1.8;
    }

    /* ── KPI Cards ────────────────────────────────────────────────────── */
    .kpi-card {
        background: #0a0e1a; border: 1px solid #1a2540; border-radius: 6px;
        padding: 14px 10px; text-align: center; margin-bottom: 8px;
    }
    .kpi-icon  { font-size: 16px; margin-bottom: 4px; opacity: 0.7; }
    .kpi-value { font-size: 20px; font-family: 'Share Tech Mono', monospace; font-weight: bold; }
    .kpi-unit  { font-size: 9px; color: #2a4060; margin-top: 1px; font-family: 'Share Tech Mono', monospace; }
    .kpi-label { font-size: 11px; color: #4a6080; margin-top: 6px; letter-spacing: 1px; }

    /* ── Section Divider ──────────────────────────────────────────────── */
    .section-divider { border-top: 1px solid #1a2540; margin: 4px 0; }

    /* ── Panel Header ─────────────────────────────────────────────────── */
    .panel-header {
        color: #2a4060; font-size: 11px; letter-spacing: 2px;
        font-family: 'Share Tech Mono', monospace;
        margin-bottom: 8px; padding: 8px 0 4px;
        border-bottom: 1px solid #1a2540;
    }

    /* ── Empty Chart Placeholder ──────────────────────────────────────── */
    .empty-chart {
        background: #0a0e1a; border: 1px solid #1a2540; border-radius: 6px;
        padding: 40px; text-align: center; color: #1a2540;
        font-family: 'Share Tech Mono', monospace; font-size: 11px;
        min-height: 200px; display: flex; align-items: center; justify-content: center;
    }

    /* ── Feature Rows ─────────────────────────────────────────────────── */
    .feature-row {
        display: flex; align-items: center; gap: 10px;
        padding: 7px 10px; margin-bottom: 4px;
        background: #0a0e1a; border: 1px solid #1a2540; border-radius: 4px;
    }
    .feature-dot  { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
    .feature-name { font-family: 'Share Tech Mono', monospace; font-size: 11px; color: #4a6080; width: 110px; flex-shrink: 0; }
    .feature-val  { font-family: 'Share Tech Mono', monospace; font-size: 13px; color: #00d4ff; font-weight: bold; width: 110px; flex-shrink: 0; }
    .feature-desc { font-size: 10px; color: #2a3550; }

    /* ── Prediction Card ─────────────────────────────────────────────── */
    .pred-card {
        text-align: center; padding: 20px;
        background: #0a0e1a; border: 1px solid; border-radius: 8px;
        margin-bottom: 14px;
    }
    .pred-icon  { font-size: 32px; margin-bottom: 6px; }
    .pred-label { font-size: 22px; font-weight: 700; letter-spacing: 3px; margin-bottom: 6px; font-family: 'Share Tech Mono', monospace; }
    .pred-conf  { font-size: 13px; color: #4a6080; margin-bottom: 10px; font-family: 'Share Tech Mono', monospace; }
    .pred-sev   { display: inline-block; padding: 4px 14px; border-radius: 3px; font-size: 11px; border: 1px solid; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }

    /* ── Probability Bars ─────────────────────────────────────────────── */
    .prob-header { color: #2a4060; font-size: 10px; letter-spacing: 2px; font-family: 'Share Tech Mono', monospace; margin: 12px 0 8px; }
    .prob-row    { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
    .prob-label  { font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #4a6080; width: 90px; flex-shrink: 0; }
    .prob-bar-bg { flex: 1; height: 8px; background: #0a0e1a; border-radius: 4px; overflow: hidden; border: 1px solid #1a2540; }
    .prob-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease; }
    .prob-pct    { font-family: 'Share Tech Mono', monospace; font-size: 11px; font-weight: bold; width: 42px; text-align: right; }

    /* ── Diagnosis Box ────────────────────────────────────────────────── */
    .diag-box {
        background: #040608; border: 1px solid #1a2540; border-radius: 6px;
        padding: 14px; margin-top: 10px;
    }
    .diag-title { color: #2a4060; font-size: 10px; letter-spacing: 2px; font-family: 'Share Tech Mono', monospace; margin-bottom: 6px; }
    .diag-text  { color: #8ab0d0; font-size: 12px; line-height: 1.5; }

    /* ── Health Box ───────────────────────────────────────────────────── */
    .health-box {
        text-align: center; padding: 20px;
        background: #0a0e1a; border: 1px solid; border-radius: 8px;
        margin-top: 10px;
    }

    /* ── Footer ───────────────────────────────────────────────────────── */
    .footer {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 24px; margin-top: 20px;
        border-top: 1px solid #1a2540;
        font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #1a2540;
    }
    </style>
    """, unsafe_allow_html=True)
