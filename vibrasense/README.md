# ⚡ VIBRA·SENSE — Predictive Maintenance System

**Industrial Vibration Analysis Dashboard for Oil & Gas Equipment**

> Built by [FARES] · Next-Generation Oil Field Solutions

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]((https://vibrasense.streamlit.app/))
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange?logo=scikit-learn)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?logo=streamlit)

---

## 🛢️ Overview

VIBRA·SENSE is a full-stack predictive maintenance application that uses **machine learning** and **signal processing** to detect equipment faults from vibration data — the way it's done in real CBM (Condition-Based Maintenance) programs in the oil & gas industry.

The dashboard simulates vibration sensors on rotating equipment (pumps, compressors, turbines) and classifies their condition in real time.

---

## 🔬 Features

### Signal Generation
| Fault Type | Description | Key Indicator |
|---|---|---|
| ✅ Normal | Clean sine wave at running speed | Low kurtosis, stable RMS |
| ⚙ Bearing Fault | High-freq impulse train (BPFI/BPFO) | High kurtosis (>5), impulsive |
| ⚖ Imbalance | Dominant 1x amplitude | Very high RMS at 1x freq |
| ↗ Misalignment | Rich 1x/2x/3x harmonic content | Harmonic ratio >0.5 |

### Signal Processing
- **FFT** with Hanning window (reduces spectral leakage)
- Time-domain and frequency-domain visualization
- Harmonic marker overlay (1x–5x running speed)

### Feature Extraction (14 features)
- **Time domain**: RMS, Peak, Crest Factor, Kurtosis, Skewness, Std Dev, Shape Factor, Impulse Factor
- **Frequency domain**: Dominant Frequency, Spectral Centroid, Bandwidth, Band Energy Ratios, Harmonic Ratio

### ML Classifier
- **RandomForest** (200 trees) trained on 1200 synthetic samples (300/class)
- StandardScaler normalization
- Returns: class probabilities, confidence, severity (Low/Medium/High)
- Expert-system severity overlay (ISO 10816 thresholds)

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/yourusername/vibrasense.git
cd vibrasense

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push to GitHub (public or private repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set **Main file**: `app.py`
5. Click **Deploy** — done!

No environment variables required. All dependencies are in `requirements.txt`.

---

## 📁 Project Structure

```
vibrasense/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Dark theme config
└── utils/
    ├── __init__.py
    ├── styles.py           # Industrial CSS theme
    ├── signal_gen.py       # Vibration signal synthesis
    ├── signal_proc.py      # FFT + feature extraction
    ├── ml_model.py         # RandomForest classifier
    └── plots.py            # Plotly dark-theme charts
```

---

## 🏭 Real-World Application

This tool demonstrates the core workflow used by industrial CBM software (like Emerson AMS, SKF @ptitude, Bentley Nevada):

1. **Acquire** vibration data from accelerometer sensors
2. **Process** the raw signal (FFT, filtering, demodulation)
3. **Extract** statistical and spectral features
4. **Classify** equipment condition using ML models
5. **Alert** maintenance teams with actionable recommendations

---

## 📊 Technical Standards Referenced

- **ISO 10816** — Mechanical vibration evaluation of machine severity
- **ISO 1940** — Balance quality requirements for rigid rotors
- **API 670** — Machinery protection systems (petroleum industry)

---

## 👤 Author

**SERHOUDJI** · Petroleum Geology & Data Science  
Next-Generation Oil Field Solutions · Algeria  
Fiverr: [souhil_twelve](https://www.fiverr.com/souhil_twelve)

---

## 📄 License

MIT License — free to use and modify for educational and commercial purposes.
