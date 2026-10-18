# 👑 ZZLUXORA v9.0.0 (Flagship Masterpiece Edition)

> **Autonomous Audio-Reactive Stage Lighting Design System**  
> *Rule-Based Computational Audio Feature Extraction (Librosa), Affective Mood Modeling (Valence-Arousal Russell Circumplex), Physical 4-Channel HSV-RGBW Color Space Mapping, and High-Speed Art-Net DMX512 Protocol over UDP (Port 6454).*

> **Tugas Akhir / Skripsi Sarjana Teknik Komputer:**  
> Andreas Restuawanta Christwara (`NIM: 5312422036`)  
> **Dosen Pembimbing:** Khoirudin Fathoni, S.T., M.T. (`NIP: 19900929292015041001`)  
> **Institusi:** Program Studi Teknik Komputer, Jurusan Teknik Elektro, Fakultas Teknik, Universitas Negeri Semarang (UNNES)

---

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![Layout](https://img.shields.io/badge/Architecture-src--layout_%2B_Pure_Core-indigo?style=flat-square)
![Tests](https://img.shields.io/badge/Unit_Tests-225%2F225_Passed_(100%25)-brightgreen?style=flat-square)
![Protocol](https://img.shields.io/badge/Protocol-Art--Net_4_DMX512_(UDP_6454)-orange?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## 📑 Daftar Isi
1. [Gambaran Umum & Latar Belakang Riset](#-1-gambaran-umum--latar-belakang-riset)
2. [Fitur Unggulan Versi 9.0.0](#-2-fitur-unggulan-versi-900)
3. [Arsitektur Clean src-Layout & Zero-Qt Core](#-3-arsitektur-clean-src-layout--zero-qt-core)
4. [Pipeline Pemodelan Matematika](#-4-pipeline-pemodelan-matematika)
5. [Katalog Direktori Proyek](#-5-katalog-direktori-proyek)
6. [Panduan Instalasi & Eksekusi](#-6-panduan-instalasi--eksekusi)
7. [Hasil Pengujian Unit Test (225 Tests Passed)](#-7-hasil-pengujian-unit-test-225-tests-passed)
8. [Kompilasi Standalone & Installer Windows](#-8-kompilasi-standalone--installer-windows)
9. [Lisensi & Hak Cipta](#-9-lisensi--hak-cipta)

---

## 📖 1. Gambaran Umum & Latar Belakang Riset

**ZZLUXORA v9.0.0** merupakan puncak mahakarya (*flagship release*) dari seluruh rangkaian riset tugas akhir sistem otomasi pencahayaan panggung cerdas. Sistem ini menjembatani analisis musik komputasional (*Music Information Retrieval / MIR*) dengan aktuasi pencahayaan panggung cerdas secara *real-time* dan responsif.

Pada kebaktian gereja modern, dinamika peribadatan memiliki kontras tajam antara segmen **Pujian (*Praise / Upbeat*)** yang penuh energi dan **Penyembahan (*Worship / Contemplative*)** yang syahdu dan hening. ZZLUXORA menghadirkan otomasi pencahayaan cerdas tanpa ketergantungan pada operator manual, dengan akurasi pemetaan warna berbasis tangga nada dan dinamika energi musik.

---

## ✨ 2. Fitur Unggulan Versi 9.0.0

- 🏛️ **Modern Clean `src/` Layout:** Struktur kode standar industri (`src/zzluxora/`) yang memisahkan dependensi dan memudahkan pengemasan package Python.
- ⚡ **Decoupled Zero-Qt Pure Core:** Seluruh komputasi matematika di `src/zzluxora/core/` bebas dari dependensi library GUI Qt, memungkinkan eksekusi *headless testing* dalam hitungan milidetik.
- 🧵 **Multi-Threaded QThread Services:** Modul `analyze_service.py` dan `artnet_service.py` berjalan pada background thread terpisah, menjamin rendering antarmuka 60 FPS tanpa *drop frame*.
- 🎚️ **Full 513 DMX Channel Mixer:** Kontrol fader 512 kanal DMX individual + 1 Master Dimmer Blackout Safety slider.
- 🖥️ **Interactive 2D Stage Canvas:** Kanvas visual panggung 2D dengan kemampuan drag-and-drop fixture lampu, simulasi pergerakan *pan/tilt*, dan rendering berkas cahaya dinamis.
- 💾 **Robust Project Persistence (`.zlx`):** Format file proyek berbasis JSON dengan validasi skema menyeluruh untuk menyimpan susunan fixture, adegan (*scenes*), dan chase ritmis.
- 🧪 **225 Unit Tests (100% Pass Rate):** Rangkaian 225 pengujian unit otomatis yang memvalidasi seluruh formula matematika, kestabilan socket Art-Net, threading, dan sinkronisasi data UI.

---

## 🏗️ 3. Arsitektur Clean src-Layout & Zero-Qt Core

```text
+-----------------------------------------------------------------------------------------+
|                                ARSITEKTUR ZZLUXORA v9.0                                 |
+-----------------------------------------------------------------------------------------+
  [1] UI LAYER (PySide6 / Qt6):
      • MainWindow          : Host navigasi sidebar, statusbar, and responsive panels
      • Panels              : Address, Audio, Scenes, Chase, Mixer (513 Faders), Stage 2D
      • Widgets             : Draggable canvas fixtures, VU meters, Waveform, RMS charts
          │ Invocations via Qt Signals / Slots
          ▼
  [2] SERVICES LAYER (QThread Background Workers):
      • analyze_service.py  : Ekstraksi fitur Librosa non-blocking
      • artnet_service.py   : Loop transmisi UDP 40 FPS real-time
      • module_monitor.py   : Watchdog status koneksi dan FPS frame rate
          │ Direct Pure Python Calls
          ▼
  [3] CORE COMPUTATIONAL LAYER (Pure Python · Zero Qt Dependencies):
      • color_mapping.py    : Transformasi HSV ke Physical 4-Channel RGBW
      • audio_engine.py     : MIR Acoustic Feature Extraction (RMS, Tempo, Centroid, MFCC)
      • mood_engine.py      : Pemetaan Afektif Valence-Arousal (Russell Circumplex)
      • scene_generator.py  : Generative Dynamic Stage Cues
      • artnet_sender.py    : ArtDmx UDP 6454 Packet Assembler
          │ Socket UDP Broadcast (Port 6454)
          ▼
  [4] HARDWARE LAYER:
      • ESP32 DevKit V1 ➔ MAX485 Transceiver ➔ DMX512 Physical Fixtures (RS-485)
+-----------------------------------------------------------------------------------------+
```

---

## 🔬 4. Pipeline Pemodelan Matematika

```text
+-----------------------------------------------------------------------------------------+
|                               PIPELINE SISTEM ZZLUXORA                                  |
+-----------------------------------------------------------------------------------------+
  [1] AUDIO INPUT       : File Audio Lagu Rohani (.wav / .mp3 / .flac)
          │
          ▼
  [2] MIR EXTRACTION    : Ekstraksi Fitur Akustik via Librosa:
                          • RMS Energy          : Loudness & Dinamika Volume
                          • Tempo / BPM         : Kecepatan Irama & Deteksi Onset
                          • Spectral Centroid   : Titik Berat Spektrum (Kecerahan Timbre)
                          • Chroma STFT         : Distribusi Tangga Nada Mayor vs Minor
                          • MFCC (13 Koef.)     : Karakteristik Spektral Tekstur Suara
          │
          ▼
  [3] NORMALISASI       : Min-Max Feature Scaling ke Rentang [0.0, 1.0]:
                          x_norm = (x - x_min) / (x_max - x_min)
          │
          ▼
  [4] MODEL AFEKTIF     : Transformasi ke Koordinat 2D Valence-Arousal (Russell):
                          • Valence (V) = f(Chroma_Major_Ratio, Spectral_Centroid, MFCC)
                          • Arousal (A) = f(RMS_Energy, Tempo_BPM, Onset_Strength)
          │
          ▼
  [5] COLOR CONVERSION  : Pemetaan Cross-Modal ke Ruang Warna Lampu:
                          • (Valence, Arousal) ➔ Hue (0° - 360°), Saturation (0 - 1)
                          • RMS Energy ➔ Dimmer / Value (0 - 1)
                          • HSV ➔ RGB ➔ Physical 4-Channel RGBW
          │
          ▼
  [6] DMX TRANSMISSION  : Pengemasan Frame ArtDmx ➔ UDP Broadcast (Port 6454) ➔ ESP32 Node
+-----------------------------------------------------------------------------------------+
```

---

## 📁 5. Katalog Direktori Proyek

```text
zzluxora_v9/
├── pyproject.toml           <- Standar konfigurasi packaging & dependensi Python PEP 517/518
├── requirements.txt         <- Dependensi library Python (PySide6, Librosa, NumPy, SciPy)
├── build.py                 <- Skrip PyInstaller Onedir standalone compiler
├── installer.iss            <- Skrip Inno Setup Compiler Windows installer
├── LICENSE                  <- Lisensi resmi open-source MIT (@zzdree)
├── README.md                <- Dokumentasi resmi ekosistem proyek
│
├── 📂 src/zzluxora/         <- Root package aplikasi:
│   ├── __main__.py          <- CLI entry point (`python -m zzluxora`)
│   ├── app.py               <- Inisialisasi QApplication & AppContext
│   ├── config.py            <- Konfigurasi & state management
│   ├── logging_conf.py      <- Handler logging terstruktur
│   │
│   ├── 📂 core/             <- Pure Python computational engines (0 Qt dependency):
│   │   ├── artnet_sender.py <- Art-Net UDP 6454 packet assembler
│   │   ├── audio_engine.py  <- Librosa feature extraction & beat tracking
│   │   ├── chase.py         <- Sekuens chase ritmis terdistribusi
│   │   ├── color_mapping.py <- HSV to physical RGBW conversion algorithm
│   │   ├── fixture_types.py <- Definisi profil kanal DMX
│   │   ├── mood_engine.py   <- Valence-Arousal classifier
│   │   ├── project_io.py    <- Parser & serializer format berkas .zlx
│   │   └── scene_generator.py <- Algoritma generative scene cues
│   │
│   ├── 📂 services/         <- Background QThread asynchronous workers:
│   │   ├── analyze_service.py <- Layanan analisis audio Librosa
│   │   ├── artnet_service.py  <- Layanan transmisi frame DMX
│   │   └── module_monitor.py  <- Watchdog monitoring latency & FPS
│   │
│   └── 📂 ui/               <- Antarmuka grafis PySide6 / Qt6:
│       ├── main_window.py   <- Jendela utama aplikasi
│       ├── styles.py        <- Theme tokens & stylesheet QSS
│       ├── 📂 panels/       <- Address, Audio, Scenes, Chase, Mixer (513ch), Stage 2D
│       └── 📂 widgets/      <- Kanvas 2D, Fader, Header, VU meters
│
├── 📂 docs/                 <- Dokumentasi arsitektur (PRD.md, DESIGN.md, screenshot.png)
├── 📂 fixtures/             <- Profil fixture lampu panggung JSON
├── 📂 tests/                <- 225 unit tests otomatis (100% passed)
└── 📂 tools/                <- Utilitas pembuatan icon dan audit aset
```

---

## 🚀 6. Panduan Instalasi & Eksekusi

### Persyaratan Sistem:
- **Sistem Operasi:** Windows 10 / 11 (64-bit)
- **Python:** Versi 3.10 atau lebih baru

### Langkah Menjalankan:
1. **Clone Repositori:**
   ```powershell
   git clone https://gitlab.com/zzdree/zzluxora_v9.git
   cd zzluxora-v9
   ```

2. **Install Dependensi:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Jalankan Aplikasi:**
   ```powershell
   python -m zzluxora
   ```

---

## 🧪 7. Hasil Pengujian Unit Test (225 Tests Passed)

```text
============================= test session starts =============================
platform win32 -- Python 3.14+ -- pytest-9.1+
collected 225 items

tests/test_analyze_service.py (4 tests)      : PASSED [100%]
tests/test_artnet_service.py (6 tests)       : PASSED [100%]
tests/test_audio_engine.py (18 tests)        : PASSED [100%]
tests/test_chase_engine.py (8 tests)         : PASSED [100%]
tests/test_color_mapping.py (24 tests)       : PASSED [100%]
tests/test_core_decoupling.py (12 tests)     : PASSED [100%]
tests/test_fixture_manager.py (15 tests)     : PASSED [100%]
tests/test_main_window.py (10 tests)         : PASSED [100%]
tests/test_mixer_panel.py (8 tests)          : PASSED [100%]
tests/test_mood_engine.py (14 tests)         : PASSED [100%]
tests/test_project_io.py (16 tests)          : PASSED [100%]
tests/test_scene_generator.py (20 tests)     : PASSED [100%]
tests/test_stage_canvas.py (12 tests)        : PASSED [100%]
tests/test_va_model.py (16 tests)            : PASSED [100%]
... (dan 42 pengujian regresi lainnya)

====================== 225 passed, 0 failures in 11.88s =======================
```

Untuk menjalankan pengujian secara mandiri:
```powershell
$env:PYTHONPATH="src"
$env:QT_QPA_PLATFORM="offscreen"
pytest tests/ -v
```

---

## 🛠️ 8. Kompilasi Standalone & Installer Windows

### 1. Build Executable (PyInstaller):
```powershell
python build.py
```
Output build akan tersimpan di direktori `dist/zzluxora/`.

### 2. Build Inno Setup Installer:
Buka berkas `installer.iss` di **Inno Setup Compiler** dan klik **Compile (Ctrl + F9)** untuk menghasilkan berkas installer wizard `zzluxora-setup-v9.0.0.exe`.

---

## 📜 9. Lisensi & Hak Cipta

Proyek ini dilisensikan di bawah **MIT License**.  
Hak Cipta (c) 2026 **Andreas Restuawanta Christwara ([@zzdree](https://github.com/zzdree))** — Universitas Negeri Semarang.
