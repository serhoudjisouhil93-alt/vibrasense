"""
Signal Generation Module — VIBRA·SENSE
Realistic vibration signal synthesis for oil & gas equipment fault simulation
"""

import numpy as np


def generate_signal(
    fault_type: str,
    noise_level: float = 0.1,
    sample_rate: int = 1000,
    duration: float = 1.0,
    rpm: int = 1500,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic vibration signals mimicking real equipment behavior.

    Parameters
    ----------
    fault_type   : 'normal' | 'bearing' | 'imbalance' | 'misalignment'
    noise_level  : Gaussian noise standard deviation (0 = clean, 1 = very noisy)
    sample_rate  : Samples per second (Hz)
    duration     : Signal length in seconds
    rpm          : Equipment rotational speed (RPM) — used to set base freq

    Returns
    -------
    t      : Time array (seconds)
    signal : Vibration amplitude array
    """
    n = int(sample_rate * duration)
    t = np.linspace(0, duration, n, endpoint=False)

    # Fundamental frequency from RPM
    f0 = rpm / 60.0   # Hz — 1x running speed

    rng = np.random.default_rng(seed=None)
    noise = rng.normal(0, noise_level, n)

    if fault_type == "normal":
        # Clean sinusoidal — balanced rotating machinery
        signal = (
            1.0 * np.sin(2 * np.pi * f0 * t)
            + 0.05 * np.sin(2 * np.pi * 2 * f0 * t)   # Tiny 2x harmonic
            + noise
        )

    elif fault_type == "bearing":
        # Bearing defect → high-freq impulses at BPFI/BPFO
        # Typical BPFI ≈ 3.5–5x running speed
        bpfi = 4.7 * f0   # Ball pass frequency inner race
        bpfo = 3.1 * f0   # Ball pass frequency outer race
        bsf  = 2.0 * f0   # Ball spin frequency

        # Periodic impulse train mimicking bearing defect
        impulse_period = int(sample_rate / bpfi)
        impulses = np.zeros(n)
        for i in range(0, n, max(1, impulse_period)):
            width = max(2, int(sample_rate * 0.002))
            decay = np.exp(-np.arange(width) * 800 / sample_rate)
            end = min(i + width, n)
            impulses[i:end] += decay[:end - i]

        signal = (
            0.6 * np.sin(2 * np.pi * f0 * t)            # 1x running
            + 0.4 * np.sin(2 * np.pi * bpfi * t)        # BPFI
            + 0.3 * np.sin(2 * np.pi * bpfo * t)        # BPFO
            + 0.2 * np.sin(2 * np.pi * bsf  * t)        # BSF
            + 1.5 * impulses                             # Impact train
            + noise * 2.0
        )

    elif fault_type == "imbalance":
        # Mass imbalance → dominant 1x, high amplitude
        signal = (
            3.5 * np.sin(2 * np.pi * f0 * t)             # 1x — dominant
            + 1.2 * np.sin(2 * np.pi * f0 * t + 0.3)    # Phase shift component
            + 0.3 * np.sin(2 * np.pi * 2 * f0 * t)      # 2x harmonic (small)
            + noise
        )

    elif fault_type == "misalignment":
        # Shaft misalignment → rich harmonic content at 1x, 2x, 3x
        signal = (
            1.0 * np.sin(2 * np.pi * f0 * t)             # 1x
            + 0.8 * np.sin(2 * np.pi * 2 * f0 * t)      # 2x — characteristic
            + 0.5 * np.sin(2 * np.pi * 3 * f0 * t)      # 3x — axial component
            + 0.3 * np.sin(2 * np.pi * 4 * f0 * t)      # 4x
            + 0.15 * np.sin(2 * np.pi * 5 * f0 * t)     # 5x
            + noise * 0.8
        )

    else:
        signal = noise

    return t, signal


def get_fault_description(fault_type: str) -> dict:
    """Return metadata about each fault type for display."""
    descriptions = {
        "normal": {
            "cause": "Balanced rotating mass, clean bearings",
            "risk": "Low",
            "color": "#00ff88",
            "icon": "✓",
        },
        "bearing": {
            "cause": "Fatigue spalling on bearing race, inadequate lubrication",
            "risk": "High",
            "color": "#ff6b35",
            "icon": "⚙",
        },
        "imbalance": {
            "cause": "Uneven mass distribution on rotating shaft",
            "risk": "Medium",
            "color": "#ffd700",
            "icon": "⚖",
        },
        "misalignment": {
            "cause": "Angular or parallel shaft misalignment at coupling",
            "risk": "Medium-High",
            "color": "#ff4466",
            "icon": "↗",
        },
    }
    return descriptions.get(fault_type, descriptions["normal"])
