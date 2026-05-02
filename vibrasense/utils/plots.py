"""
Visualization Module — VIBRA·SENSE
Industrial dark-theme Plotly charts for oil & gas monitoring dashboard
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ── Theme constants ─────────────────────────────────────────────────────────
BG_COLOR     = "#060912"
PANEL_COLOR  = "#0a0e1a"
GRID_COLOR   = "#1a2540"
TEXT_COLOR   = "#4a6080"
ACCENT_CYAN  = "#00d4ff"
ACCENT_GREEN = "#00ff88"
FONT_MONO    = "Share Tech Mono, Courier New, monospace"

FAULT_COLORS = {
    "normal":      "#00ff88",
    "bearing":     "#ff6b35",
    "imbalance":   "#ffd700",
    "misalignment":"#ff4466",
}

BASE_LAYOUT = dict(
    paper_bgcolor=PANEL_COLOR,
    plot_bgcolor=BG_COLOR,
    font=dict(family=FONT_MONO, size=10, color=TEXT_COLOR),
    margin=dict(l=48, r=12, t=28, b=36),
    xaxis=dict(
        gridcolor=GRID_COLOR, gridwidth=1,
        linecolor=GRID_COLOR, tickfont=dict(size=9),
        showgrid=True, zeroline=False,
    ),
    yaxis=dict(
        gridcolor=GRID_COLOR, gridwidth=1,
        linecolor=GRID_COLOR, tickfont=dict(size=9),
        showgrid=True, zeroline=False,
    ),
)


def plot_time_domain(
    t: np.ndarray,
    signal: np.ndarray,
    fault_type: str,
    rpm: int,
) -> go.Figure:
    color = FAULT_COLORS.get(fault_type, ACCENT_CYAN)

    # Downsample for display (max 2000 pts)
    step = max(1, len(t) // 2000)
    t_d, s_d = t[::step], signal[::step]

    fig = go.Figure()

    # Shaded envelope
    fig.add_trace(go.Scatter(
        x=np.concatenate([t_d, t_d[::-1]]),
        y=np.concatenate([s_d, -np.abs(s_d[::-1])]),
        fill="toself", fillcolor=f"{color}08",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # Main waveform
    fig.add_trace(go.Scatter(
        x=t_d, y=s_d,
        mode="lines",
        line=dict(color=color, width=1.2),
        name=fault_type.upper(),
        hovertemplate="t=%{x:.4f}s<br>Amp=%{y:.4f}g<extra></extra>",
    ))

    # RMS line
    rms_val = float(np.sqrt(np.mean(signal ** 2)))
    for sign in [1, -1]:
        fig.add_hline(
            y=sign * rms_val,
            line=dict(color=f"{color}55", width=1, dash="dot"),
            annotation_text=f"±RMS={rms_val:.3f}" if sign == 1 else "",
            annotation_font=dict(size=9, color=f"{color}aa"),
        )

    layout = BASE_LAYOUT.copy()
    layout.update(
        height=220,
        showlegend=False,
        xaxis_title="Time (s)",
        yaxis_title="Amplitude (g)",
        xaxis=dict(**BASE_LAYOUT["xaxis"]),
        yaxis=dict(**BASE_LAYOUT["yaxis"]),
    )
    fig.update_layout(**layout)

    # Annotation: fault type label
    fig.add_annotation(
        x=0.01, y=0.95, xref="paper", yref="paper",
        text=f"● {fault_type.upper().replace('_',' ')} | {rpm} RPM",
        showarrow=False,
        font=dict(size=9, color=color, family=FONT_MONO),
        xanchor="left",
    )

    return fig


def plot_fft_spectrum(
    freqs: np.ndarray,
    mags: np.ndarray,
    fault_type: str,
    rpm: int,
    sample_rate: int,
) -> go.Figure:
    color = FAULT_COLORS.get(fault_type, ACCENT_CYAN)
    f0 = rpm / 60.0

    # Show up to Nyquist / 2 for clarity, or max 500 Hz
    max_freq = min(sample_rate // 2, 500)
    mask = freqs <= max_freq
    f_d, m_d = freqs[mask], mags[mask]

    fig = go.Figure()

    # Spectrum fill
    fig.add_trace(go.Scatter(
        x=f_d, y=m_d,
        fill="tozeroy", fillcolor=f"{color}15",
        line=dict(color=color, width=1.5),
        name="FFT",
        hovertemplate="Freq=%{x:.1f}Hz<br>Mag=%{y:.4f}<extra></extra>",
    ))

    # Harmonic markers (1x, 2x, 3x, 4x, 5x)
    for n_harm in range(1, 6):
        freq_harm = n_harm * f0
        if freq_harm <= max_freq:
            fig.add_vline(
                x=freq_harm,
                line=dict(color="#ffffff22", width=1, dash="dot"),
                annotation_text=f"{n_harm}x" if n_harm <= 3 else "",
                annotation_font=dict(size=8, color="#ffffff44"),
                annotation_position="top",
            )

    # Dominant frequency marker
    dom_idx = int(np.argmax(m_d))
    fig.add_trace(go.Scatter(
        x=[f_d[dom_idx]], y=[m_d[dom_idx]],
        mode="markers+text",
        marker=dict(color=color, size=8, symbol="diamond",
                    line=dict(color="#ffffff", width=1)),
        text=[f" {f_d[dom_idx]:.1f}Hz"],
        textfont=dict(size=9, color=color, family=FONT_MONO),
        textposition="top right",
        showlegend=False,
        hovertemplate="DOM: %{x:.1f}Hz<br>Mag=%{y:.4f}<extra></extra>",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(
        height=220,
        showlegend=False,
        xaxis_title="Frequency (Hz)",
        yaxis_title="Magnitude",
    )
    fig.update_layout(**layout)

    fig.add_annotation(
        x=0.99, y=0.95, xref="paper", yref="paper",
        text=f"Hanning Window | Δf={freqs[1]-freqs[0]:.2f}Hz",
        showarrow=False,
        font=dict(size=8, color=TEXT_COLOR, family=FONT_MONO),
        xanchor="right",
    )

    return fig


def plot_feature_radar(features: dict) -> go.Figure:
    """Normalized radar / spider chart of key features."""
    # Normalize to 0-1 scale for radar display
    norms = {
        "RMS":        min(features["rms"] / 4.0,         1.0),
        "Kurtosis":   min(features["kurtosis"] / 10.0,   1.0),
        "Crest\nFact":min(features["crest_factor"] / 6.0,1.0),
        "Dom\nFreq":  min(features["dominant_freq"] / 500,1.0),
        "Spectral\nCentroid": min(features["spectral_centroid"] / 300, 1.0),
        "High\nBand": min(features["high_band_energy"],   1.0),
    }
    categories = list(norms.keys())
    values     = list(norms.values()) + [list(norms.values())[0]]  # close polygon
    cats_closed = categories + [categories[0]]

    # Color based on overall health
    rms_norm = norms["RMS"]
    if rms_norm > 0.6 or norms["Kurtosis"] > 0.6:
        line_color = "#ff4466"
    elif rms_norm > 0.35 or norms["Kurtosis"] > 0.35:
        line_color = "#ffd700"
    else:
        line_color = "#00ff88"

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values, theta=cats_closed,
        fill="toself", fillcolor=f"{line_color}18",
        line=dict(color=line_color, width=2),
        name="Features",
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            bgcolor=BG_COLOR,
            radialaxis=dict(
                visible=True, range=[0, 1],
                gridcolor=GRID_COLOR, tickfont=dict(size=8, color=TEXT_COLOR),
                showticklabels=True, tickvals=[0.25, 0.5, 0.75, 1.0],
            ),
            angularaxis=dict(
                gridcolor=GRID_COLOR,
                tickfont=dict(size=9, color=TEXT_COLOR, family=FONT_MONO),
            ),
        ),
        paper_bgcolor=PANEL_COLOR,
        showlegend=False,
        height=220,
        margin=dict(l=30, r=30, t=20, b=20),
        font=dict(family=FONT_MONO, size=9, color=TEXT_COLOR),
    )

    return fig


def plot_probability_gauge(prediction: dict) -> go.Figure:
    """Gauge chart showing health index (normal probability)."""
    health = prediction["probabilities"].get("normal", 0) * 100
    fault_pred = prediction["prediction"]

    if health > 70:
        gauge_color = "#00ff88"
        bar_color   = "#00ff88"
    elif health > 40:
        gauge_color = "#ffaa00"
        bar_color   = "#ffaa00"
    else:
        gauge_color = "#ff2244"
        bar_color   = "#ff2244"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        number=dict(
            suffix="%",
            font=dict(family=FONT_MONO, size=28, color=gauge_color),
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=1, tickcolor=GRID_COLOR,
                tickfont=dict(size=9, color=TEXT_COLOR, family=FONT_MONO),
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
            ),
            bar=dict(color=bar_color, thickness=0.25),
            bgcolor=BG_COLOR,
            borderwidth=1, bordercolor=GRID_COLOR,
            steps=[
                dict(range=[0, 35],  color="#ff224415"),
                dict(range=[35, 65], color="#ffaa0015"),
                dict(range=[65, 100],color="#00ff8815"),
            ],
            threshold=dict(
                line=dict(color="#ffffff", width=2),
                thickness=0.8, value=health,
            ),
        ),
        title=dict(
            text="HEALTH INDEX",
            font=dict(family=FONT_MONO, size=10, color=TEXT_COLOR),
        ),
        domain=dict(x=[0, 1], y=[0, 1]),
    ))

    fig.update_layout(
        paper_bgcolor=PANEL_COLOR,
        height=240,
        margin=dict(l=20, r=20, t=30, b=10),
        font=dict(family=FONT_MONO, color=TEXT_COLOR),
    )

    return fig
