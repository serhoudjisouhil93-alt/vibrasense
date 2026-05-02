"""
VIBRA·SENSE — Predictive Maintenance System
Oil & Gas Industrial Vibration Analysis Dashboard
Author: SERHOUDJI / Next-Generation Oil Field Solutions
"""

import streamlit as st
from utils.styles import inject_css
from utils.signal_gen import generate_signal
from utils.signal_proc import compute_fft, extract_features
from utils.ml_model import load_model, predict_fault
from utils.plots import plot_time_domain, plot_fft_spectrum, plot_feature_radar, plot_probability_gauge
import numpy as np
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VIBRA·SENSE | Predictive Maintenance",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Session state init ─────────────────────────────────────────────────────────
for key, default in {
    "signal": None, "t": None, "fft_freqs": None, "fft_mags": None,
    "features": None, "prediction": None, "signal_type": "normal",
    "log": [], "alert_active": False, "run_count": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Load ML model (cached) ─────────────────────────────────────────────────────
model, scaler, label_encoder = load_model()

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-bar">
  <div class="header-left">
    <div class="header-icon">⚡</div>
    <div>
      <div class="header-title">VIBRA·SENSE</div>
      <div class="header-sub">PREDICTIVE MAINTENANCE SYSTEM · VIBRATION ANALYSIS MODULE v2.0</div>
    </div>
  </div>
  <div class="header-right">
    <div class="status-dot blink"></div>
    <span class="status-text">SYSTEM ONLINE</span>
    <div class="header-badges">
      <span class="badge badge-blue">FFT READY</span>
      <span class="badge badge-green">ML ACTIVE</span>
      <span class="badge badge-orange">SCADA LINK</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — CONTROL PANEL
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙ CONTROL PANEL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">── EQUIPMENT SELECTOR</div>', unsafe_allow_html=True)

    equipment = st.selectbox("Asset", [
        "ESP-001 · Electric Submersible Pump",
        "COMP-002 · Gas Compressor",
        "TURB-003 · Turbine Generator",
        "PUMP-004 · Centrifugal Pump",
    ], label_visibility="collapsed")

    st.markdown('<div class="sidebar-section">── FAULT SIMULATION</div>', unsafe_allow_html=True)

    fault_options = {
        "✅  Normal Operation":   "normal",
        "⚙  Bearing Fault":      "bearing",
        "⚖  Mass Imbalance":     "imbalance",
        "↗  Shaft Misalignment": "misalignment",
    }
    selected_label = st.radio(
        "Condition", list(fault_options.keys()),
        label_visibility="collapsed"
    )
    fault_type = fault_options[selected_label]
    st.session_state.signal_type = fault_type

    st.markdown('<div class="sidebar-section">── SENSOR CONFIGURATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        sample_rate = st.selectbox("Sample Rate", [1000, 2000, 5000], index=0)
    with col2:
        duration = st.selectbox("Duration (s)", [1, 2, 5], index=0)

    noise_level = st.slider("Noise Level (σ)", 0.0, 1.0, 0.1, 0.05)
    rpm = st.slider("Equipment RPM", 300, 3600, 1500, 50)

    st.markdown('<div class="sidebar-section">── ACTIONS</div>', unsafe_allow_html=True)

    btn_generate = st.button("▶  GENERATE SIGNAL", use_container_width=True, type="primary")
    btn_analyze  = st.button("⊕  EXTRACT FEATURES", use_container_width=True)
    btn_predict  = st.button("◈  PREDICT FAULT", use_container_width=True)
    btn_clear    = st.button("↺  RESET", use_container_width=True)

    st.markdown('<div class="sidebar-section">── SYSTEM LOG</div>', unsafe_allow_html=True)
    log_box = st.empty()

    def add_log(msg, level="INFO"):
        ts = time.strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ", "WARN": "⚠", "OK": "✓", "ERR": "✗"}.get(level, "·")
        st.session_state.log.append(f"[{ts}] {prefix} {msg}")
        st.session_state.log = st.session_state.log[-10:]

    log_content = "\n".join(st.session_state.log[-8:]) if st.session_state.log else "Awaiting input..."
    log_box.markdown(f'<div class="log-box"><pre>{log_content}</pre></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-footer">
      <div>⚡ VIBRA·SENSE v2.0</div>
      <div>FARES · Next-Gen Oil Field Solutions</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BUTTON ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
if btn_clear:
    for key in ["signal", "t", "fft_freqs", "fft_mags", "features", "prediction", "log", "alert_active"]:
        st.session_state[key] = None if key != "log" else []
    st.session_state.alert_active = False
    st.rerun()

if btn_generate:
    with st.spinner("Acquiring sensor data..."):
        t, signal = generate_signal(fault_type, noise_level, sample_rate, duration, rpm)
        freqs, mags = compute_fft(signal, sample_rate)
        st.session_state.t = t
        st.session_state.signal = signal
        st.session_state.fft_freqs = freqs
        st.session_state.fft_mags = mags
        st.session_state.features = None
        st.session_state.prediction = None
        st.session_state.run_count += 1
        add_log(f"Signal generated: {fault_type.upper()} @ {sample_rate}Hz", "OK")
        add_log(f"Samples: {len(signal)} | Duration: {duration}s", "INFO")

if btn_analyze and st.session_state.signal is not None:
    with st.spinner("Processing signal..."):
        feats = extract_features(
            st.session_state.signal,
            st.session_state.fft_freqs,
            st.session_state.fft_mags,
            sample_rate
        )
        st.session_state.features = feats
        st.session_state.prediction = None
        add_log(f"Features extracted: RMS={feats['rms']:.3f}, Kurt={feats['kurtosis']:.2f}", "OK")
        add_log(f"Dom.Freq={feats['dominant_freq']:.1f}Hz, Crest={feats['crest_factor']:.2f}", "INFO")

if btn_predict and st.session_state.features is not None:
    with st.spinner("Running ML classifier..."):
        result = predict_fault(model, scaler, label_encoder, st.session_state.features)
        st.session_state.prediction = result
        fault_pred = result["prediction"]
        conf = result["confidence"]
        st.session_state.alert_active = fault_pred != "normal"
        add_log(f"PREDICTION: {fault_pred.upper()} ({conf:.1%})", "WARN" if fault_pred != "normal" else "OK")
        add_log(f"Severity: {result['severity'].upper()}", "WARN" if result["severity"] != "low" else "INFO")

# ══════════════════════════════════════════════════════════════════════════════
# ALERT BANNER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.alert_active and st.session_state.prediction:
    pred = st.session_state.prediction
    sev_colors = {"high": "#ff2244", "medium": "#ffaa00", "low": "#ffee00"}
    sev_color = sev_colors.get(pred["severity"], "#ffaa00")
    st.markdown(f"""
    <div class="alert-banner" style="border-color:{sev_color}; box-shadow: 0 0 20px {sev_color}44;">
      <span class="alert-icon blink">⚠</span>
      <span class="alert-text">FAULT DETECTED — {pred['prediction'].upper().replace('_',' ')} · SEVERITY: {pred['severity'].upper()} · {pred['recommendation']}</span>
      <span class="alert-badge" style="background:{sev_color}22; border-color:{sev_color}; color:{sev_color};">
        ACTION REQUIRED
      </span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

def kpi_card(col, label, value, unit, status="normal", icon="◈"):
    status_colors = {"normal": "#00ff88", "warning": "#ffaa00", "critical": "#ff2244", "idle": "#3a5070"}
    color = status_colors.get(status, "#00d4ff")
    col.markdown(f"""
    <div class="kpi-card" style="border-top: 2px solid {color};">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-value" style="color:{color};">{value}</div>
      <div class="kpi-unit">{unit}</div>
      <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

feats = st.session_state.features
pred  = st.session_state.prediction

kpi_card(kpi1, "RMS Amplitude",   f"{feats['rms']:.3f}"           if feats else "—", "g",   "normal"   if (feats and feats['rms'] < 1.0) else "warning",  "〜")
kpi_card(kpi2, "Peak Amplitude",  f"{feats['peak']:.3f}"          if feats else "—", "g",   "normal"   if (feats and feats['peak'] < 2.0) else "warning",  "△")
kpi_card(kpi3, "Kurtosis",        f"{feats['kurtosis']:.2f}"      if feats else "—", "ratio","normal"   if (feats and feats['kurtosis'] < 5) else "critical","κ")
kpi_card(kpi4, "Dom. Frequency",  f"{feats['dominant_freq']:.1f}" if feats else "—", "Hz",  "normal",  "♦")
kpi_card(kpi5, "Crest Factor",    f"{feats['crest_factor']:.2f}"  if feats else "—", "ratio","warning"  if (feats and feats['crest_factor'] > 3) else "normal","⬡")
kpi_card(kpi6, "Fault Status",
    pred["prediction"].upper().replace("_"," ") if pred else "UNKNOWN",
    f"{pred['confidence']:.0%}" if pred else "—",
    "critical" if (pred and pred["prediction"] != "normal") else ("normal" if pred else "idle"),
    "◈"
)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHARTS ROW
# ══════════════════════════════════════════════════════════════════════════════
chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown('<div class="panel-header">📈 TIME-DOMAIN SIGNAL</div>', unsafe_allow_html=True)
    if st.session_state.signal is not None:
        fig = plot_time_domain(
            st.session_state.t,
            st.session_state.signal,
            fault_type,
            rpm
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div class="empty-chart">Generate a signal to view waveform</div>', unsafe_allow_html=True)

with chart_right:
    st.markdown('<div class="panel-header">📊 FREQUENCY SPECTRUM (FFT)</div>', unsafe_allow_html=True)
    if st.session_state.fft_freqs is not None:
        fig = plot_fft_spectrum(
            st.session_state.fft_freqs,
            st.session_state.fft_mags,
            fault_type,
            rpm,
            sample_rate
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div class="empty-chart">FFT spectrum will appear here</div>', unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FEATURES + PREDICTION ROW
# ══════════════════════════════════════════════════════════════════════════════
feat_col, pred_col, gauge_col = st.columns([1.2, 1.2, 0.8])

with feat_col:
    st.markdown('<div class="panel-header">🔬 EXTRACTED FEATURES</div>', unsafe_allow_html=True)
    if st.session_state.features:
        f = st.session_state.features
        feature_items = [
            ("RMS",            f"{f['rms']:.4f}",           "Root Mean Square amplitude",     f['rms'] < 1.5),
            ("Peak",           f"{f['peak']:.4f}",          "Maximum absolute amplitude",     f['peak'] < 3.0),
            ("Kurtosis",       f"{f['kurtosis']:.4f}",      "Statistical impulsiveness ratio", f['kurtosis'] < 5.0),
            ("Dom. Freq",      f"{f['dominant_freq']:.2f} Hz", "Dominant frequency component",f['dominant_freq'] < 200),
            ("Crest Factor",   f"{f['crest_factor']:.4f}",  "Peak-to-RMS ratio",              f['crest_factor'] < 4.0),
            ("Std Deviation",  f"{f['std_dev']:.4f}",       "Signal standard deviation",      True),
            ("Skewness",       f"{f['skewness']:.4f}",      "Statistical asymmetry",          abs(f['skewness']) < 1.0),
            ("Spectral Centroid", f"{f['spectral_centroid']:.2f} Hz", "FFT center of mass",  True),
        ]
        for name, val, desc, ok in feature_items:
            dot_color = "#00ff88" if ok else "#ff4466"
            st.markdown(f"""
            <div class="feature-row">
              <div class="feature-dot" style="background:{dot_color}; box-shadow:0 0 6px {dot_color};"></div>
              <div class="feature-name">{name}</div>
              <div class="feature-val">{val}</div>
              <div class="feature-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        # Radar chart
        fig_radar = plot_feature_radar(f)
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown('<div class="empty-chart">Run EXTRACT FEATURES to analyse signal</div>', unsafe_allow_html=True)

with pred_col:
    st.markdown('<div class="panel-header">🤖 ML CLASSIFIER OUTPUT</div>', unsafe_allow_html=True)
    if st.session_state.prediction:
        p = st.session_state.prediction
        fault_colors = {
            "normal":      "#00ff88",
            "bearing":     "#ff6b35",
            "imbalance":   "#ffd700",
            "misalignment":"#ff4466",
        }
        fault_icons = {"normal": "✓", "bearing": "⚙", "imbalance": "⚖", "misalignment": "↗"}
        p_color = fault_colors.get(p["prediction"], "#00d4ff")
        p_icon  = fault_icons.get(p["prediction"], "◈")
        sev_colors = {"high": "#ff2244", "medium": "#ffaa00", "low": "#00ff88"}
        sev_color = sev_colors.get(p["severity"], "#ffaa00")

        st.markdown(f"""
        <div class="pred-card" style="border-color:{p_color}44;">
          <div class="pred-icon" style="color:{p_color};">{p_icon}</div>
          <div class="pred-label" style="color:{p_color};">{p['prediction'].upper().replace('_',' ')}</div>
          <div class="pred-conf">{p['confidence']:.1%} CONFIDENCE</div>
          <div class="pred-sev" style="border-color:{sev_color}; color:{sev_color}; background:{sev_color}22;">
            SEVERITY: {p['severity'].upper()}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="prob-header">CLASS PROBABILITIES</div>', unsafe_allow_html=True)
        for fault, prob in p["probabilities"].items():
            fc = fault_colors.get(fault, "#00d4ff")
            pct = prob * 100
            st.markdown(f"""
            <div class="prob-row">
              <div class="prob-label">{fault.upper().replace('_',' ')}</div>
              <div class="prob-bar-bg">
                <div class="prob-bar-fill" style="width:{pct:.1f}%; background:linear-gradient(90deg,{fc}88,{fc}); box-shadow:0 0 8px {fc}88;"></div>
              </div>
              <div class="prob-pct" style="color:{fc};">{pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="diag-box">
          <div class="diag-title">◈ DIAGNOSIS</div>
          <div class="diag-text">{p['reasoning']}</div>
          <div class="diag-title" style="margin-top:10px;">⚙ RECOMMENDED ACTION</div>
          <div class="diag-text" style="color:#00ff88;">{p['recommendation']}</div>
          <div class="diag-title" style="margin-top:10px;">📅 MAINTENANCE WINDOW</div>
          <div class="diag-text" style="color:#ffd700;">{p.get('maintenance_window','Schedule inspection within 30 days')}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-chart">Run PREDICT FAULT after feature extraction</div>', unsafe_allow_html=True)

with gauge_col:
    st.markdown('<div class="panel-header">⚡ HEALTH INDEX</div>', unsafe_allow_html=True)
    if st.session_state.prediction:
        fig_gauge = plot_probability_gauge(st.session_state.prediction)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        # Condition assessment
        health = st.session_state.prediction["probabilities"].get("normal", 0) * 100
        if health > 70:
            cond, cond_color, cond_icon = "GOOD", "#00ff88", "✓"
        elif health > 40:
            cond, cond_color, cond_icon = "DEGRADED", "#ffaa00", "⚠"
        else:
            cond, cond_color, cond_icon = "CRITICAL", "#ff2244", "✗"

        st.markdown(f"""
        <div class="health-box" style="border-color:{cond_color}44;">
          <div style="font-size:28px; color:{cond_color};">{cond_icon}</div>
          <div style="color:{cond_color}; font-size:14px; font-weight:bold; letter-spacing:2px;">{cond}</div>
          <div style="color:#3a5070; font-size:11px; margin-top:4px;">EQUIPMENT CONDITION</div>
          <div style="color:{cond_color}; font-size:22px; font-weight:bold; margin-top:8px;">{health:.0f}%</div>
          <div style="color:#3a5070; font-size:10px;">HEALTH INDEX</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-chart" style="height:300px;">Health index will appear after prediction</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
  <span>⚡ VIBRA·SENSE v2.0</span>
  <span>FARES · Next-Generation Oil Field Solutions</span>
  <span>Powered by Python · scikit-learn · Streamlit · Plotly</span>
</div>
""", unsafe_allow_html=True)
