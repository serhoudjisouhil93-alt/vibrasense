"""
Signal Processing Module — VIBRA·SENSE
FFT computation and statistical feature extraction for vibration analysis
"""

import numpy as np
from scipy import stats, signal as sp_signal
from scipy.fft import rfft, rfftfreq


def compute_fft(sig: np.ndarray, sample_rate: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute Real FFT of the vibration signal.

    Returns
    -------
    freqs : Frequency bins (Hz)
    mags  : Magnitude spectrum (normalized)
    """
    n = len(sig)
    # Apply Hanning window to reduce spectral leakage
    window = np.hanning(n)
    windowed = sig * window

    fft_vals = rfft(windowed)
    freqs = rfftfreq(n, d=1.0 / sample_rate)
    mags  = np.abs(fft_vals) * (2.0 / n)   # Two-sided → one-sided correction

    return freqs, mags


def extract_features(
    sig: np.ndarray,
    freqs: np.ndarray,
    mags: np.ndarray,
    sample_rate: int,
) -> dict:
    """
    Extract time-domain and frequency-domain features from vibration signal.

    Features used by ISO 10816 / ISO 20816 vibration standards and
    common CBM (Condition-Based Maintenance) practices.
    """
    n = len(sig)
    mean = np.mean(sig)
    sig_centered = sig - mean

    # ── Time-domain features ───────────────────────────────────────────────
    rms          = float(np.sqrt(np.mean(sig ** 2)))
    peak         = float(np.max(np.abs(sig)))
    crest_factor = float(peak / rms) if rms > 0 else 0.0
    std_dev      = float(np.std(sig))
    kurtosis     = float(stats.kurtosis(sig, fisher=False))   # Excess kurtosis + 3
    skewness     = float(stats.skew(sig))
    peak_to_peak = float(np.max(sig) - np.min(sig))
    shape_factor = float(rms / (np.mean(np.abs(sig)) + 1e-10))
    impulse_factor = float(peak / (np.mean(np.abs(sig)) + 1e-10))

    # ── Frequency-domain features ──────────────────────────────────────────
    dom_idx      = int(np.argmax(mags))
    dominant_freq = float(freqs[dom_idx])

    # Spectral centroid (center of mass of spectrum)
    total_mag = np.sum(mags) + 1e-10
    spectral_centroid = float(np.sum(freqs * mags) / total_mag)

    # Spectral bandwidth (RMS spread around centroid)
    spectral_bandwidth = float(
        np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * mags) / total_mag)
    )

    # Energy in frequency bands (low, mid, high)
    low_band  = float(np.sum(mags[freqs <  100] ** 2))
    mid_band  = float(np.sum(mags[(freqs >= 100) & (freqs < 300)] ** 2))
    high_band = float(np.sum(mags[freqs >= 300] ** 2))
    total_energy = low_band + mid_band + high_band + 1e-10

    # Harmonic ratio (2nd harmonic vs fundamental)
    if dom_idx > 0:
        harmonic_idx = min(2 * dom_idx, len(mags) - 1)
        harmonic_ratio = float(mags[harmonic_idx] / (mags[dom_idx] + 1e-10))
    else:
        harmonic_ratio = 0.0

    return {
        # Time domain
        "rms":             rms,
        "peak":            peak,
        "crest_factor":    crest_factor,
        "std_dev":         std_dev,
        "kurtosis":        kurtosis,
        "skewness":        skewness,
        "peak_to_peak":    peak_to_peak,
        "shape_factor":    shape_factor,
        "impulse_factor":  impulse_factor,
        # Frequency domain
        "dominant_freq":       dominant_freq,
        "spectral_centroid":   spectral_centroid,
        "spectral_bandwidth":  spectral_bandwidth,
        "low_band_energy":     low_band / total_energy,
        "mid_band_energy":     mid_band / total_energy,
        "high_band_energy":    high_band / total_energy,
        "harmonic_ratio":      harmonic_ratio,
    }


def get_feature_vector(features: dict) -> np.ndarray:
    """Convert features dict to ordered numpy array for ML model input."""
    keys = [
        "rms", "peak", "crest_factor", "std_dev", "kurtosis", "skewness",
        "dominant_freq", "spectral_centroid", "spectral_bandwidth",
        "low_band_energy", "mid_band_energy", "high_band_energy",
        "harmonic_ratio", "impulse_factor",
    ]
    return np.array([features[k] for k in keys])
