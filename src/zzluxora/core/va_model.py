"""VA model — normalisasi fitur, Valence/Arousal, dan pemetaan V-A → HSV.

INTI SKRIPSI (R2 §2.2.3 + script_math_model.md §2-4). Pure functions, no Qt.

Pipeline:
    raw features → normalize (min-max, clip [0,1])
                 → arousal = 0.40·BPMₙ + 0.35·RMSₙ + 0.25·Onsetₙ
                 → valence = 0.50·ChromaMajorₙ + 0.30·SCₙ + 0.20·(1−|MFCC1ₙ−0.5|·2)
                 → va_to_hsv(v, a) → (H, S, V)
"""
from __future__ import annotations

# Min-max normalization ranges from skripsi (R2 §2.2.3d / math_model §2)
NORMALIZE_RANGES: dict[str, tuple[float, float]] = {
    "bpm": (60.0, 180.0),
    "rms": (0.01, 0.5),
    "spectral_centroid": (500.0, 5000.0),
    "mfcc1": (-300.0, 100.0),
    "onset_rate": (0.5, 8.0),
    "chroma_major_ratio": (0.0, 1.0),
}

# Weight constants (math_model §10 — tunable)
W_AROUSAL = (0.40, 0.35, 0.25)  # BPM, RMS, Onset
W_VALENCE = (0.50, 0.30, 0.20)  # ChromaMajor, SC, MFCC-dist


def normalize_value(x: float, x_min: float, x_max: float) -> float:
    """Min-max normalize to [0,1] with clipping (R2 §2.2.3d)."""
    if x_max <= x_min:
        return 0.0
    norm = (x - x_min) / (x_max - x_min)
    return max(0.0, min(1.0, norm))


def normalize_features(raw: dict[str, float]) -> dict[str, float]:
    """Normalize a raw feature dict using the skripsi tables."""
    out: dict[str, float] = {}
    for key, (lo, hi) in NORMALIZE_RANGES.items():
        out[key] = normalize_value(float(raw.get(key, lo)), lo, hi)
    return out


def compute_arousal(norm: dict[str, float]) -> float:
    """A = 0.40·BPMₙ + 0.35·RMSₙ + 0.25·Onsetₙ (math_model §3)."""
    wa_bpm, wa_rms, wa_onset = W_AROUSAL
    return (
        wa_bpm * float(norm.get("bpm", 0.0))
        + wa_rms * float(norm.get("rms", 0.0))
        + wa_onset * float(norm.get("onset_rate", 0.0))
    )


def compute_valence(norm: dict[str, float]) -> float:
    """V = 0.50·ChromaMajorₙ + 0.30·SCₙ + 0.20·(1 − |MFCC1ₙ − 0.5|·2) (math_model §3)."""
    wv_chroma, wv_sc, wv_mfcc = W_VALENCE
    chroma = float(norm.get("chroma_major_ratio", 0.0))
    sc = float(norm.get("spectral_centroid", 0.0))
    mfcc1 = float(norm.get("mfcc1", 0.5))
    mfcc_dist = 1.0 - abs(mfcc1 - 0.5) * 2.0
    return wv_chroma * chroma + wv_sc * sc + wv_mfcc * mfcc_dist


# ----------------------------------------------------------------------
# V-A → HSV (math_model §4)
# ----------------------------------------------------------------------
def _hue_base(valence: float, arousal: float) -> float:
    """Quadrant-based base hue (math_model §4 / R2 §7.2).

    Q1 V>0.5, A>0.5 → 30 + (V-0.5)·60    (kuning/amber)
    Q2 V≤0.5, A>0.5 → 270 + (0.5-V)·120  (ungu/magenta)
    Q3 V≤0.5, A≤0.5 → 200 + (0.5-V)·120  (biru/indigo)
    Q4 V>0.5, A≤0.5 → 150 + (V-0.5)·100  (hijau/cyan)
    """
    if valence > 0.5 and arousal > 0.5:
        return 30 + (valence - 0.5) * 60
    if valence <= 0.5 and arousal > 0.5:
        return 270 + (0.5 - valence) * 120
    if valence <= 0.5 and arousal <= 0.5:
        return 200 + (0.5 - valence) * 120
    return 150 + (valence - 0.5) * 100


def va_to_hsv(
    valence: float,
    arousal: float,
    rms_n: float | None = None,
    chroma_peak: float = 6.0,
) -> tuple[float, float, float]:
    """Map (Valence, Arousal) → (Hue°, Saturation, Value) per math_model §4.

    H = H_base + (ChromaPeak − 6) × 5°  (koreksi chroma)
    S = 0.6·A + 0.4·|2V − 1|
    V = max(0.5·RMSₙ + 0.5·A, 0.10)      (rms_n fallback ke arousal)
    """
    valence = max(0.0, min(1.0, float(valence)))
    arousal = max(0.0, min(1.0, float(arousal)))

    hue = _hue_base(valence, arousal) + (chroma_peak - 6.0) * 5.0
    hue = hue % 360.0

    sat = 0.6 * arousal + 0.4 * abs(2.0 * valence - 1.0)
    sat = max(0.0, min(1.0, sat))

    rms_n = float(rms_n) if rms_n is not None else arousal
    value = max(0.5 * rms_n + 0.5 * arousal, 0.10)
    value = min(1.0, value)

    return hue, sat, value
