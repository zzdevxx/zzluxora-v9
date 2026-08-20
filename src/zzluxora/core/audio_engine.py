"""Audio engine — librosa feature extraction (R2 skripsi §2.2.1, math_model §1).

Pure functions, no Qt. Input: audio file path. Output: dict of features:

    bpm                 tempo (beats per minute)
    rms                 average RMS energy (0..1-ish)
    spectral_centroid   "brightness" in Hz (mean)
    mfcc1               first MFCC coefficient (mean)
    chroma_major_ratio  ratio of major-scale chroma energy
    onset_rate          onsets per second
    beat_times          list of beat frame timestamps (s)
    duration_s          audio duration in seconds
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import librosa
import numpy as np

# Chroma classes belonging to a major scale (root-relative): C D E F G A B
MAJOR_INDICES = [0, 2, 4, 5, 7, 9, 11]

SUPPORTED_EXTENSIONS = (".wav", ".mp3", ".ogg", ".flac")


def load_audio(path: str | Path) -> tuple[np.ndarray, float]:
    """Load mono audio + sample rate. Raises FileNotFoundError if missing."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")
    y, sr = librosa.load(str(path), sr=None, mono=True)
    return y, float(sr)


def extract_features(path: str | Path) -> dict[str, Any]:
    """Extract all MIR features required by the skripsi model."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio file not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported audio format: {path.suffix} (use {SUPPORTED_EXTENSIONS})")

    y, sr = load_audio(path)
    duration_s = float(len(y)) / sr

    # --- Tempo / BPM ---
    # beat_track bisa return 0 pada audio lemah/non-rythmic; fallback ke
    # estimator berbasis onset envelope (math_model §1 — onset strength).
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr
    )
    bpm = float(np.atleast_1d(tempo)[0])
    if not bpm or bpm <= 0:
        bpm = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0])
    if not bpm or bpm <= 0:
        bpm = 60.0  # dan terakhir: default worship tempo (R2: 60-100)

    # --- RMS energy (mean) ---
    rms = float(np.mean(librosa.feature.rms(y=y)[0]))

    # --- Spectral centroid (mean, Hz) ---
    sc = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))

    # --- MFCC (first coefficient, mean) ---
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc1 = float(np.mean(mfcc[0]))

    # --- Chroma major ratio (R2 §2.2.1 / math_model §1) ---
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    total = float(np.sum(chroma_mean))
    major_energy = float(np.sum(chroma_mean[MAJOR_INDICES]))
    chroma_major_ratio = major_energy / total if total > 0 else 0.5

    # --- Onset strength & rate (reuse onset_env dari blok tempo) ---
    onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, units="frames")
    onset_rate = float(len(onset_frames) / duration_s) if duration_s > 0 else 0.0

    # --- Beat times (seconds) — beat_frames dari beat_track di blok tempo ---
    beat_times = librosa.frames_to_time(np.atleast_1d(beat_frames), sr=sr).tolist()

    return {
        "bpm": bpm,
        "rms": rms,
        "spectral_centroid": sc,
        "mfcc1": mfcc1,
        "chroma_major_ratio": chroma_major_ratio,
        "onset_rate": onset_rate,
        "beat_times": beat_times,
        "duration_s": duration_s,
    }
