# 📋 PRD — ZZLUXORA v9 (Recreate-from-Scratch)

**Versi PRD:** v2.0 (diupdate dari v1.0 berdasarkan 4 sumber referensi)
**Tanggal:** 2026-08-10
**Project:** `C:\ANDREAS\SCRIPT3`
**Author:** Andreas Restuawanta Christwara (UNNES) — dibantu agen Antigravity

---

## 0. Sumber Referensi (Base)

| # | Sumber | Peran | Path |
|---|--------|-------|------|
| R1 | **QLC+ source** | **Base reference arsitektur & konsep UI** (Fixture Manager, Function Manager, Virtual Console, Monitor, Simple Desk, Grand Master, Input/Output Manager + plugin Art-Net) | `C:\ANDREAS\SCRIPT\qlcplus` |
| R2 | **Skripsi v3 (docx)** | **Base core & method** — rule-based mapping, model V-A → HSV → RGB → RGBW (BAB 2-3), batasan fixture 8-kanal, 4 PAR LED | `C:\ANDREAS\SCRIPT\script_projects\script_andreas_v3.docx` |
| R3 | **feedback_v2.txt** | **Base frontend & backend behavior** — spesifikasi UI per-panel, alur tombol, mixer 513 slider, output scan-IP (tanpa universe/FPS setting) | `C:\ANDREAS\SCRIPT\notes\feedback_v2.txt` |
| R4 | **artnet_dmx_v4.txt** | **Base Art-Net connection** — universe 0, port 6454, ArtDmx opcode 0x50, single universe, IP target (localhost / 192.168.4.1 / custom) | `C:\ANDREAS\SCRIPT\artnet_projects\artnet_dmx_v4.txt` |
| R5 | **image_references (5 PNG)** | **Base frontend style — GrandMA3** — dark theme, accent biru elektrik, indikator hijau/merah, grid DMX, fader, typography uppercase | `C:\ANDREAS\SCRIPT\image_references\image_01..05.png` |

> **Keputusan user:** TANPA splash screen · UI bahasa **Inggris** · **Mixer 512 fader termasuk MVP** · Installer Inno Setup **ya** · Real-time mic → roadmap.
>
> **Design system lengkap di [docs/DESIGN.md](file:///C:/ANDREAS/SCRIPT3/docs/DESIGN.md)** (token warna, tipografi, komponen per-panel — diturunkan dari analisis pixel image_01..05, style GrandMA3).

---

## 1. Executive Summary

### Masalah
Gereja kecil-menengah mengelola pencahayaan secara manual (1–2 operator non-profesional), menyusun scene per lagu secara manual, tanpa sistem terstandarisasi. Lagu rohani (*praise* & *worship*) punya dinamika berbeda yang sulit disinkronkan secara manual.

### Solusi
**ZZLUXORA v9** — desktop app *audio-reactive lighting design* yang:
1. Menganalisis lagu rohani (WAV/MP3) → fitur audio (BPM, RMS, spectral centroid, MFCC, chroma, onset, beat) via librosa
2. Memetakan fitur → **Valence-Arousal** (rule-based, skripsi §3) → **HSV → RGB → RGBW** (DRGBW 0-255)
3. Generate **scene & chase** otomatis + kontrol manual (mixer 513 fader, page button pad)
4. Kirim via **Art-Net** (UDP 6454, universe 0, ArtDmx) ke QLC+ virtual adapter atau **modul ESP32** (artnet_dmx_v4 final)

### Posisi vs Versi Lama
| Versi | Kelemahan | v9 fix |
|-------|-----------|--------|
| v7 (SCRIPT) | Monolitik, complexity 67, global state | Layering keras `core/services/ui` |
| v8 (SCRIPT2) | Panel monolitik, test minim | DI via AppContext, dataclass models, worker threads |
| **v9** | — | **Fidelity ke feedback_v2** + arsitektur QLC+-inspired + skripsi-faithful |

---

## 2. Target Audience

| Segmen | Kebutuhan |
|--------|-----------|
| **Operator lighting gereja** (non-profesional) | 1 tombol: load lagu → output sinkron; Page button pad untuk trigger cepat |
| **Mahasiswa/peneliti (skripsi)** | Validasi model matematis, black-box test, kuesioner (SUS + kesesuaian) |
| **Teknisi event kecil** | Kontrol manual (mixer 513 fader) + chase custom |

---

## 3. MVP Scope (v1.0)

> Berbasis **feedback_v2.txt** (R3) sebagai spesifikasi UI/UX yang harus dipenuhi 100% (tanpa splash per keputusan user).

### A. Aplikasi & Branding (R3 §1, §2, §3)
- [ ] Nama: **ZZLUXORA** (title bar, taskbar)
- [ ] Icon: logo lampu putih background hitam (taskbar + title bar)
- [ ] **TANPA splash screen** (override R3 §2 — keputusan user)
- [ ] Empty state saat belum load project: logo transparan, prompt "open a project", sidebar closed

### B. Header / Menubar (R3 §3)
- [ ] Header: `[Icon + ZZLUXORA] [project name/path]` + status bar kanan: `[Art-Net pill] [Play/Pause toggle] [Blackout]`
- [ ] Art-Net pill: hijau = connected, merah = disconnected
- [ ] Play/Pause: 1 tombol toggle (bukan 2)
- [ ] Blackout: set semua slider (master + ch 1-512) ke 0
- [ ] Menu bar: **File** (Open Ctrl+O, Save Ctrl+S, Save As Ctrl+Shift+S, Exit) · **View** (Program Ctrl+1, Fixture List Ctrl+2, Fixture Editor Ctrl+3, Settings Ctrl+4, About Ctrl+5 + marker aktif) · **Help** (Keyboard Shortcuts, About)
- [ ] Default filename: `untitled.zlx`

### C. Sidebar (R3 §7)
- [ ] Hamburger icon (3 strip) kiri atas, TETAP sama saat buka/tutup
- [ ] Sidebar closed by default (sebelum load project); baru bisa dibuka setelah project loaded
- [ ] Items (5): Program, Fixture List, Fixture Editor, Settings, About

### D. Program → Tab Address (R3 §8)
- [ ] Grid DMX: **max 24 kotak per baris**, scroll vertikal
- [ ] Kotak kosong: angka posisi di pojok kanan; kotak terisi: label channel di tengah + angka tetap
- [ ] Warna kotak sesuai type: Dimmer (icon lampu), Red (blok merah), Strobe (icon khusus), dst
- [ ] Tombol: **Auto Patch** (popup), **Clear All Patch** (konfirmasi), + tombol tambahan (developer nanti)
- [ ] Keterangan kanan: teks BESAR (R3: "kurang besar, perbesar")

### E. Program → Tab Analyze (CORE SKRIPSI) (R3 §9)
- [ ] Tombol: **Load Audio** (4 ekstensi: mp3/wav/ogg/flac) · **Analyze** · **Remove Song** · **Export to Scene**
- [ ] Aturan: Load selalu aktif; Analyze/Remove/Export disabled sampai song dipilih; Analyze bisa diulang; Export aktif hanya jika hasil analyze ada
- [ ] Song list di kotak kiri
- [ ] **Progress bar + deskripsi berubah tiap 3 detik** (penjelasan proses ilmiah)
- [ ] Perhitungan persis skripsi v3 (R2) + script_math_model.md: normalisasi min-max → Arousal/Valence → V-A→HSV → HSV→RGB → RGBW → DRGBW (lihat §5)

### F. Program → Tab Scenes (R3 §10)
- [ ] Kotak kiri: song list; kotak kanan: hasil mapping scene per segmen lagu
- [ ] Desain section: chorus, pre-chorus, verse, bridge
- [ ] Scene bisa dikumpulkan → Chase

### G. Program → Tab Chase (R3 §11)
- [ ] Kotak kiri: song list; kotak kanan: kontrol chase (kumpulan scene + fade timing)
- [ ] Timeline visual (referensi QLC+ Chaser Editor: step, fade in/out, hold, direction, loop)

### H. Program → Tab Page (R3 §12) — Virtual Console (R1)
- [ ] Custom button pad untuk trigger scene & chase yang sudah dibuat
- [ ] Konsep: **QLC+ Virtual Console** (button grid, page system)

### I. Program → Tab Mixer (R3 §13) — Simple Desk (R1)
- [ ] Layout: `[Master Dimmer] [Ch1] [Ch2] ... [Ch512]` = **513 slider**, full-width, horizontal scroll
- [ ] Bentuk slider: referensi Grandma console (slider + tombol kotak), value 0-255
- [ ] Tombol **Refresh** pojok kanan atas

### J. Program → Tab Preview (R3 §14) — Monitor (R1)
- [ ] Visual fixture (lingkaran PAR LED), bisa select + drag
- [ ] Sidebar kanan: panel posisi X,Y
- [ ] Sudut pandang: tampak depan

### K. Program → Tab Output (R3 §15) + Art-Net (R4)
- [ ] **Scan IP seperti QLC+** (R1 Input/Output Manager + Art-Net plugin)
- [ ] IP wajib: **localhost 127.0.0.1** · **192.168.4.1** (ESP32 AP) · **Custom**
- [ ] **TANPA setting universe dan FPS** (R3 eksplisit; firmware R4 = universe 0, port 6454)
- [ ] Tombol: **Save only** (connect/disconnect/blackout di header)
- [ ] Art-Net sender: UDP 6454, **universe 0**, ArtDmx opcode 0x50, buffer 512 ch, frame counter
- [ ] Art-Net status: connected/disconnected/connecting

### L. Fixture List (R3 §16) — Fixture Manager (R1)
- [ ] Buka ke BAWAH (bukan ke kanan), tombol segitiga expand
- [ ] Daftar fixture dari folder `fixtures/`
- [ ] Drag & drop ke tab Address

### M. Fixture Editor (R3 §17)
- [ ] Embedded window (window-in-window, bisa digeser & ditumpuk)
- [ ] Tombol Open (.json) & New
- [ ] Form: Name, Manufacturer, Channel count (tombol <>), tabel channel (Channel/Label/Type), Type options: Dimmer/RGB/Color/Strobe/Empty, tombol Save
- [ ] Default 8-kanal PAR LED RGBW (R2): ch1 Dimmer, ch2 Red, ch3 Green, ch4 Blue, ch5 Empty, ch6 Program, ch7 Speed, ch8 Empty

### N. Settings (R3 §18)
- [ ] Sesuai kebutuhan (config.ini di AppData)

### O. About (R3 §19)
- [ ] Urutan detail: Application → Description → Author → NIM → Prodi → Jurusan → Fakultas → Universitas → Judul Skripsi

### P. Fix/Improvement lain (R3 §20 + R5)
- [ ] Style **GrandMA3 + QLC+** (lihat [DESIGN.md](file:///C:/ANDREAS/SCRIPT3/docs/DESIGN.md)): dark theme, accent biru #5C96FD, indikator status, uppercase, sudut tajam
- [ ] Responsif buka/tutup sidebar & fixture list
- [ ] Kurangi emoji/icon berlebihan — icon geometris QPainter/SVG

### Q. Installer (R3 §21 + user)
- [ ] Inno Setup: install ke Program Files, data di AppData, clean install (hapus folder lama dulu), opsi keep/delete AppData
- [ ] Uninstaller: hapus folder bersih, opsi keep/delete data

### R. Core Engine (R2 — skripsi v3) 
- [ ] Normalisasi min-max (BPM 60-180, RMS 0.01-0.5, SC 500-5000, MFCC1 -300..100, onset 0.5-8.0, chroma 0-1) → clip [0,1]
- [ ] Arousal = 0.40·BPMₙ + 0.35·RMSₙ + 0.25·Onsetₙ
- [ ] Valence = 0.50·ChromaMajorₙ + 0.30·SCₙ + 0.20·(1 − |MFCC1ₙ−0.5|·2)
- [ ] Kuadran V-A → Hue base (Q1 30°, Q2 270°, Q3 200°, Q4 150° + formula) + koreksi chroma ±5°
- [ ] S = 0.6·A + 0.4·|2V−1|; V = max(0.5·RMSₙ + 0.5·A, 0.10)
- [ ] HSV→RGB (Foley & van Dam) → RGBW (W = min(R,G,B)) → **DRGBW 0–255 per kanal**
- [ ] Scene per segmen (onset/beat → pergantian scene); Chase timing rules (BPM → 500/700/1500 ms; onset strength → snap/crossfade)
- [ ] Pola multi-fixture: All-On, Running, Gradient, Center-Out
- [ ] **18+ test regresi math model** (RELEASE BLOCKER)

### S. Kualitas & Infra
- [ ] Layering keras: `core/` (0 Qt) → `services/` → `ui/` (PySide6) — QLC+-inspired (R1)
- [ ] Dataclass models: Fixture, Scene, Chase, Song, Cue (respon atas R1 `engine/`)
- [ ] Worker threads (analyze & artnet tidak block UI)
- [ ] Logging terstruktur
- [ ] pytest: math model ≥ 18 tests + engine coverage ≥ 80%
- [ ] Build: PyInstaller + Inno Setup

### 🔵 Future Roadmap (BUKAN MVP)
- Real-time audio reactive (mic) — porting `realtime.py` v8
- Multi-universe Art-Net
- MIDI/OSC input
- Web remote control
- Undo/Redo

---

## 4. Core User Flows

### Flow 1 — Penggunaan Utama (Worship)
```
1. Jalankan ZZLUXORA (tanpa splash, langsung main window + empty state)
2. File → Open Project (.zlx) atau buat baru → sidebar terbuka
3. (Opsional) Fixture Editor → buat/load fixture 8-kanal → drag ke Address tab
4. Program → Analyze: Load Audio → Analyze (progress bar + deskripsi ilmiah tiap 3 detik)
5. Review Scenes per segmen → (opsional) Export to Scene / bangun Chase
6. Output tab → Scan IP → pilih 127.0.0.1 / 192.168.4.1 / Custom → Save
7. Header → Connect → Play/Pause → lampu sinkron lagu
8. Space = play/stop, B = blackout, Esc = emergency stop
```

### Flow 2 — Konfigurasi Awal
```
1. Fixture Editor → New (Name, Manufacturer, Channel count, table channel) → Save
2. Address tab → Auto Patch atau drag-drop fixture ke grid DMX
3. File → Save As → untitled.zlx
```

### Flow 3 — Pengujian Skripsi (BAB 4)
```
1. Setup: laptop + app + ESP32 (artnet_dmx_v4) + 4× PAR LED RGBW
2. Black-box testing per fitur (checklist → pass/fail)
3. Ukur latency & packet loss (Wireshark / timestamp logging)
4. Demo 25 responden → SUS (10 item) + kesesuaian (6 item Likert)
```

---

## 5. Technical Requirements (Tech Stack & Architecture)

### Stack
| Layer | Teknologi | Alasan |
|-------|-----------|--------|
| UI | PySide6 6.11+ | Native Qt, stabil, installer-friendly |
| Audio | librosa 0.11+, numpy 2.x, scipy, soundfile | Proven di v2.1+ |
| Art-Net | UDP socket internal (stupidArtnet opsional) | R4: universe 0, port 6454 — cukup pakai socket langsung |
| Config | configparser → dataclass (AppData) | Ringan, user-editable |
| Build | PyInstaller 6+ + Inno Setup | R3 §21 |
| Test | pytest + pytest-cov | Math model block release |
| Python | 3.13 | Environment existing |

### Arsitektur (QLC+-inspired — R1)

```
zzluxora_v9/
├── src/zzluxora/
│   ├── app.py                    ← entry (TANPA splash) + AppContext (DI)
│   ├── config.py                 ← AppConfig dataclass + configparser
│   ├── logging_conf.py
│   ├── core/                     ← PURE (0 Qt) — mirror QLC+ engine/
│   │   ├── models.py             ← dataclasses (Fixture, Scene, Chase, Cue, Song)
│   │   ├── audio_engine.py       ← librosa features (pure)
│   │   ├── va_model.py           ← V-A + kuadran (skripsi §3)
│   │   ├── color_mapping.py      ← HSV→RGB→RGBW (Foley & van Dam)
│   │   ├── scene_generator.py    ← segmen → Scene
│   │   ├── chase.py              ← sequencer (fade/direction/loop)
│   │   ├── fixture_types.py      ← 10 template + 8-kanal PAR default
│   │   ├── mixer.py              ← 513-channel state + master
│   │   ├── artnet_sender.py      ← UDP 6454, universe 0, ArtDmx (R4)
│   │   └── project_io.py         ← .zlx save/load
│   ├── services/                 ← orchestration
│   │   ├── analyze_service.py    ← worker thread + progress events
│   │   ├── playback_service.py   ← chase/scene timing
│   │   └── artnet_service.py     ← connect/disconnect lifecycle
│   ├── ui/                       ← PySide6 ONLY — mirror QLC+ ui/src/
│   │   ├── main_window.py        ← menubar + header + sidebar
│   │   ├── widgets/              ← header_bar, artnet_pill, toast, dsb
│   │   └── panels/               ← address, analyze, scenes, chase, page,
│   │                             ←   mixer, preview, output, fixture_list,
│   │                             ←   fixture_editor, settings, about
│   └── tests/                    ← pytest per modul core
├── docs/                         ← PRD, DESIGN, API, BUILD, DEV
├── tools/                        ← make_ico, screenshot, audit
├── build.py · zzluxora.spec · requirements.txt
└── installer/                    ← Inno Setup (R3 §21)
```

**Prinsip arsitektur:**
1. **core/ 100% pure** — mudah dites, mirror `engine/` QLC+
2. **AppContext DI** — service registry
3. **Dataclass models** — tipe eksplisit
4. **Signals/Slots** — UI ↔ service
5. **Worker threads** — analyze & Art-Net off main thread
6. **Fidelity R3** — setiap panel sesuai feedback_v2 literal (tanpa splash, 513 slider, output scan-IP tanpa universe/FPS, dsb.)

---

## 6. Success Metrics

| # | Metrik | Target |
|---|--------|--------|
| 1 | Test math model (RELEASE BLOCKER) | **18/18 pass** (turunan v7 + skripsi §3) |
| 2 | Test coverage core | **≥ 80%** |
| 3 | Startup → window | ≤ 3 detik (tanpa splash — langsung usable) |
| 4 | Art-Net frame | Stabil 30–40 FPS, frame counter (universe 0, port 6454 — R4) |
| 5 | Fidelity feedback_v2 | **100% item terimplementasi** (checklist R3) |
| 6 | Installer | Clean install/uninstall + keep/delete AppData |
| 7 | Qt dependency on core | **0** (import-checker lint) |
| 8 | Skripsi readiness | Black-box test case siap untuk BAB 4 |

---

## 7. Keputusan Terkonfirmasi User

| # | Keputusan | Hasil |
|---|-----------|-------|
| D1 | Real-time mic di MVP | **Tidak** → roadmap |
| D2 | Mixer 512 fader | **Ya, MVP** (513 slider total) |
| D3 | Bahasa UI | **Inggris** |
| D4 | Test framework | **pytest** |
| D5 | Firmware ESP32 recreate | **Tidak** — `artnet_dmx_v4.txt` = base connection (R4) |
| D6 | Installer Inno Setup | **Ya** |
| D7 | Splash screen | **TANPA splash** |
| D8 | Sumber referensi | R1 QLC+ · R2 skripsi v3 · R3 feedback_v2 · R4 artnet_v4 · **R5 image refs (GrandMA3)** |

---

*Dokumen ini dibuat mengikuti skill prd-architect. Belum ada kode yang ditulis.*
