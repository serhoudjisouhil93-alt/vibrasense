"""
ML Model Module — VIBRA·SENSE
RandomForest classifier trained on synthetic vibration feature data
Scikit-learn based predictive maintenance fault classifier
"""

import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from utils.signal_gen import generate_signal
from utils.signal_proc import compute_fft, extract_features, get_feature_vector


# ── Training data generation ────────────────────────────────────────────────
def _generate_training_data(n_per_class: int = 300) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic training dataset with realistic variability.
    Simulates sensors on different machines at different operating points.
    """
    fault_types = ["normal", "bearing", "imbalance", "misalignment"]
    X_list, y_list = [], []

    rng = np.random.default_rng(42)

    for fault in fault_types:
        for _ in range(n_per_class):
            noise = rng.uniform(0.05, 0.4)
            sr    = rng.choice([500, 1000, 2000])
            rpm   = rng.integers(600, 3000)

            t, sig     = generate_signal(fault, noise, sr, 1, int(rpm))
            freqs, mags = compute_fft(sig, sr)
            feats       = extract_features(sig, freqs, mags, sr)
            X_list.append(get_feature_vector(feats))
            y_list.append(fault)

    return np.array(X_list), np.array(y_list)


@st.cache_resource(show_spinner="Training ML classifier on synthetic data...")
def load_model():
    """
    Train and cache the RandomForest classifier.
    Returns model, scaler, label_encoder.
    """
    X, y = _generate_training_data(n_per_class=300)

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train_sc, y_train)

    acc = clf.score(X_test_sc, y_test)
    print(f"[VIBRASENSE] Model accuracy: {acc:.3f}")

    return clf, scaler, le


# ── Inference ───────────────────────────────────────────────────────────────
def predict_fault(
    model: RandomForestClassifier,
    scaler: StandardScaler,
    label_encoder: LabelEncoder,
    features: dict,
) -> dict:
    """
    Run fault prediction on extracted features.

    Returns dict with:
        prediction, confidence, probabilities, severity,
        reasoning, recommendation, maintenance_window
    """
    fv = get_feature_vector(features).reshape(1, -1)
    fv_sc = scaler.transform(fv)

    proba = model.predict_proba(fv_sc)[0]
    classes = label_encoder.classes_
    pred_idx = int(np.argmax(proba))
    prediction = classes[pred_idx]
    confidence = float(proba[pred_idx])

    prob_dict = {cls: float(p) for cls, p in zip(classes, proba)}

    # ── Severity rules (expert system overlay) ─────────────────────────────
    severity = _assess_severity(prediction, features, confidence)

    # ── Natural language diagnosis ─────────────────────────────────────────
    reasoning, recommendation, maintenance_window = _generate_diagnosis(
        prediction, features, severity, confidence
    )

    return {
        "prediction":        prediction,
        "confidence":        confidence,
        "probabilities":     prob_dict,
        "severity":          severity,
        "reasoning":         reasoning,
        "recommendation":    recommendation,
        "maintenance_window": maintenance_window,
    }


def _assess_severity(
    prediction: str,
    features: dict,
    confidence: float,
) -> str:
    """Rule-based severity overlay on top of ML prediction."""
    if prediction == "normal":
        return "low"

    rms      = features["rms"]
    kurtosis = features["kurtosis"]
    crest    = features["crest_factor"]

    if prediction == "bearing":
        if kurtosis > 8 or crest > 5:
            return "high"
        elif kurtosis > 5 or crest > 3.5:
            return "medium"
        return "low"

    elif prediction == "imbalance":
        if rms > 4.0:
            return "high"
        elif rms > 2.0:
            return "medium"
        return "low"

    elif prediction == "misalignment":
        hr = features.get("harmonic_ratio", 0)
        if hr > 0.7 or rms > 2.0:
            return "high"
        elif hr > 0.4 or rms > 1.0:
            return "medium"
        return "low"

    return "medium"


def _generate_diagnosis(
    prediction: str,
    features: dict,
    severity: str,
    confidence: float,
) -> tuple[str, str, str]:
    """Generate human-readable diagnosis text."""

    diagnoses = {
        "normal": (
            f"Signal characteristics indicate healthy equipment operation. "
            f"RMS={features['rms']:.3f}g, Kurtosis={features['kurtosis']:.2f} — within ISO 10816 normal limits.",
            "Continue standard monitoring interval. No immediate action required.",
            "Next scheduled PM: as per maintenance plan",
        ),
        "bearing": (
            f"High-frequency impulse signatures detected. Kurtosis={features['kurtosis']:.2f} "
            f"and Crest Factor={features['crest_factor']:.2f} exceed normal thresholds, "
            f"consistent with early-stage bearing race spalling or inadequate lubrication.",
            "Inspect bearing condition immediately. Check lubrication level and quality. "
            "Apply vibration-dampening grease. Schedule bearing replacement if spalling confirmed.",
            "Immediate inspection recommended — schedule within 72 hours",
        ),
        "imbalance": (
            f"Dominant 1x running-speed component with amplitude {features['rms']:.3f}g "
            f"indicates significant rotor mass imbalance. "
            f"Peak-to-peak={features['peak_to_peak']:.3f}g exceeds ISO balance grade tolerance.",
            "Perform dynamic balancing of rotating assembly. Inspect for missing balance weights, "
            "shaft erosion, or uneven material buildup. Balance to ISO 1940 G2.5 or better.",
            "Schedule dynamic balancing within 7 days",
        ),
        "misalignment": (
            f"Strong 2x and 3x harmonic content detected (harmonic ratio={features['harmonic_ratio']:.3f}). "
            f"Multi-frequency pattern at {features['dominant_freq']:.1f}Hz base frequency is characteristic "
            f"of angular or parallel shaft misalignment at the coupling.",
            "Perform precision laser shaft alignment. Check coupling condition and flexible element wear. "
            "Verify baseplate grouting and hold-down bolt torque. Re-align to ≤0.05mm TIR.",
            "Shutdown and realign at next opportunity — within 14 days",
        ),
    }

    return diagnoses.get(prediction, diagnoses["normal"])
