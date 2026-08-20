# 🎨 DESIGN.md — ZZLUXORA v9 (GrandMA3-inspired, dari image_references)

**Versi:** v1.0 · **Tanggal:** 2026-08-10
**Sumber:** `C:\ANDREAS\SCRIPT\image_references\image_01..05.png` (analisis pixel via PIL)

---

## 1. Sumber Referensi Visual

| # | File | Ukuran | Karakter |
|---|------|--------|----------|
| V1 | `image_01.png` | 1170×695 | Main window — deep black, accent biru/teal tipis |
| V2 | `image_02.png` | 1170×695 | Panel dengan highlight biru cerah (buttons/faders aktif) |
| V3 | `image_03.png` | 1170×659 | Grid DMX/fixture — indikator hijau + magenta marker |
| V4 | `image_04.png` | 1170×659 | State output/monitor — merah + teal indikator |
| V5 | `image_05.png` | 1024×696 | Panel neutral keyboard/numpad abu |

---

## 2. Design Tokens (Hasil Analisis Pixel)

### 2.1 Warna Dasar (Dark Theme)

| Token | Nilai | Penggunaan |
|-------|-------|------------|
| `bg-deep` | `#000000` | Background utama (image_01) |
| `bg-base` | `#0F0F0F` | Window base (image_02) |
| `bg-panel` | `#121215` | Panel surface (image_04) |
| `bg-elevated` | `#1C1C1E` | Card/raised panel (image_02) |
| `bg-toolbar` | `#26282A` | Toolbar/header (image_03) |
| `border` | `#333333` | Border panel/divider |
| `border-strong` | `#2A2A2E` | Border fokus/sel |
| `text-primary` | `#FFFFFF` | Teks utama |
| `text-secondary` | `#9A9AA0` | Teks sekunder/deskripsi |
| `text-dim` | `#6E6E76` | Teks disabled/placeholder |

### 2.2 Warna Aksen (Status & Selection)

| Token | Nilai | Penggunaan |
|-------|-------|------------|
| `accent-blue` | `#5C96FD` | **Highlight aktif** — button selected, fader aktif, sidebar item (image_02) |
| `accent-cyan` | `#52CDEA` | Secondary highlight / info (image_02) |
| `ok-green` | `#00B300` | **Connected / active / pass** (image_03) |
| `warn-yellow` | `#F1C40F` | Warning / recording / no-signal (image_03 #7B690A) |
| `danger-red` | `#FF3333` | **Error / stop / emergency** (image_04 #FF0000) |
| `magenta` | `#FF00FF` | **Marker / selection khusus** (image_03/04) |
| `teal` | `#0F9B9B` | Aux info (image_01/04) |

### 2.3 Tipografi (GrandMA3-style)

| Properti | Nilai | Catatan |
|----------|-------|---------|
| Font utama | **Segoe UI / Inter** (sans) | Fallback: `DejaVu Sans` |
| Font numpad | **Consolas / JetBrains Mono** | Untuk nilai DMX, fader, grid |
| Style | **UPPERCASE** untuk label utama | GrandMA3 khas huruf kapital semua |
| Tracking | `letter-spacing: 1-2px` | Label header & tombol |
| Ukuran | Header 13pt bold · Label 10pt · Body 9.5pt · Keterangan 8.5pt | R3: "keterangan diperbesar" → secondary 10pt |
| Weight | Bold (700) untuk tombol & judul | Semi-bold (600) untuk label |

### 2.4 Spacing & Radius

| Token | Nilai | Penggunaan |
|-------|-------|------------|
| `space-xs` | 4px | Gap icon-label |
| `space-sm` | 8px | Padding kecil |
| `space-md` | 12px | Padding standar |
| `space-lg` | 16px | Section gap |
| `radius-sm` | 2px | Button, input (GrandMA3 tajam) |
| `radius-md` | 4px | Panel, card |
| `radius-lg` | 6px | Popup/modal |

> GrandMA3 ciri khas: sudut **tajam/minimal** (2-4px), bukan rounded besar.

---

## 3. Komponen Style (per UI)

### 3.1 Header Bar (R3 §3)
```
[bg-toolbar #26282A, height 48px, border-bottom #333]
[Icon + "ZZLUXORA" uppercase 13pt bold white] 
[project name/path — secondary 10pt] 
                            [ArtNet pill] [Play/Pause toggle] [Blackout]
```
- ArtNet pill: bg `ok-green` text hitam → connected · bg `#333` text `#9A9AA0` → disconnected · bg `warn-yellow` → connecting
- Play/Pause: 1 tombol toggle (accent-blue saat play)
- Blackout: lingkaran hitam border putih

### 3.2 Sidebar (R3 §7)
```
[width 56px collapsed → 200px expanded, bg #121215]
Hamburger (3 strip, konsisten) di kiri atas
Items (5): icon + label uppercase
Active item: bg accent-blue #5C96FD → text hitam  (KONTRAST tinggi)
Hover: bg #1C1C1E
```
- Empty state: sidebar collapsed, logo transparan (opacity 0.3), prompt "Open a Project"

### 3.3 Menu Bar
- File / View / Help — text putih, hover bg #1C1C1E
- View items dengan dot marker (●) di item aktif

### 3.4 Program Tabs (Address/Analyze/Scenes/Chase/Page/Mixer/Preview/Output)
```
Tab strip: uppercase 10pt, active tab bg accent-blue text hitam, border-bottom 2px accent-blue
Panel content: bg-panel #121215
Deskripsi kanan: text-secondary 10pt, wrap, expandable
```

### 3.5 Address Grid (R3 §8) — image_03 style
```
Container: bg #0F0F0F, border #333
Cell: 24 per row (max), 36x36px, bg #1C1C1E, border #333
  - Kosong: angka posisi pojok kanan bawah, text-dim 8pt
  - Terisi: label channel tengah (10pt white), angka tetap pojok
Warna sel per type:
  - Dimmer : #8A6D00 bg-warn + icon lampu ☀
  - Red    : bg #7A0000 + blok merah
  - Green  : bg #007A00
  - Blue   : bg #00007A
  - Strobe : bg #5A007A + icon ⚡
  - Empty  : #1C1C1E
Highlight drag-over: border accent-cyan 2px
Tombol Auto Patch: accent-blue · Clear All: danger-red outline
```

### 3.6 Analyze Tab (R3 §9)
```
Tombol: Load Audio (accent-blue primary) · Analyze (ok-green) · Remove Song (danger-red outline) · Export to Scene (accent-blue outline)
Disabled state: opacity 0.4, text-dim
Song list kiri: bg #0F0F0F, item hover bg #1C1C1E, selected bg accent-blue text hitam
Progress bar: bg #26282A, fill accent-blue (indeterminate → accent-cyan)
Deskripsi ilmiah: text-secondary 10pt italic (berubah tiap 3 detik), monospace frame
```

### 3.7 Scenes / Chase (R3 §10-11) — QLC+ Chaser-inspired
```
Scene card: bg #1C1C1E border #333, thumbnail warna (RGBW preview)
  - Section label: "CHORUS" uppercase 9pt accent-cyan, dll.
  - DRGBW value: monospace 10pt
Chase timeline: horizontal, bg #0F0F0F, step bars warna segmen
  - Fade in/out, hold, direction, loop icon
```

### 3.8 Page Tab (R3 §12) — Virtual Console
```
Button grid 4-6 kolom: bg #1C1C1E, border #333
  - Normal: uppercase white 10pt
  - Active/flash: bg accent-blue text hitam
  - Scene button: border-left 3px warna scene
  - Chase button: border-left 3px magenta
Page selector bawah: tabs "PAGE 1..N"
```

### 3.9 Mixer (R3 §13) — image_02 fader style
```
513 slider horizontal scroll, setiap fader 34px wide
Slider track: bg #26282A, handle bg gradient #5C96FD→#2A5FD8
Value label atas: monospace 10pt white (0-255)
Master Dimmer: handle kuning #F1C40F (GrandMA3 khas master)
Tombol kotak kecil di atas fader: toggle on/off (bg #333 → accent-blue saat on)
Refresh pojok kanan atas (icon ↻)
```

### 3.10 Preview (R3 §14)
```
Canvas bg #0F0F0F, grid halus (#1C1C1E)
Fixture = lingkaran PAR: 
  - Off: ring #333, fill #121215
  - On: fill sesuai warna RGBW aktual + glow (blur, opacity 0.35)
  - Selected: ring accent-cyan 2px dashed + handle drag
Sidebar kanan: posisi X/Y input (monospace), spawn/fixture list
Sudut pandang: tampak depan
```

### 3.11 Output (R3 §15) — scan IP ala QLC+
```
IP list: bg #0F0F0F
  - 127.0.0.1 (localhost) — selalu ada, icon PC
  - 192.168.4.1 (ESP32 AP) — selalu ada, icon chip
  - Local IP hasil scan (QLC+ style auto-scan) — icon network
  - Custom: input field + tombol Add
Item terpilih: bg accent-blue text hitam
Compatibility: universe 0 · port 6454 · ArtDmx (R4) — tanpa setting universe/FPS (R3)
Tombol Save: accent-blue
Status bawah: pill Art-Net state + frame counter monospace
```

### 3.12 Fixture Editor (R3 §17)
```
MDI area: bg #0F0F0F, sub-window draggable: titlebar #26282A, border #333, shadow
Form: Name/Manufacturer/Channel count (spin +/-), tabel channel (Channel/Label/Type)
Type combo: Dimmer, Red, Green, Blue, Color, Strobe, Empty
Save: accent-blue · Close: danger-red outline
```

### 3.13 Toast / Notification
```
Bg #26282A text white, border-left 3px:
  - success: ok-green
  - warning: warn-yellow
  - error: danger-red
Auto-hide 3s, slide-in dari atas
```

---

## 4. Responsivitas (R3 §20)
- Sidebar 56px ↔ 200px dengan animasi 120ms ease-out
- Fixture List expand ke bawah (bukan ke kanan)
- Mixer horizontal scroll penuh 513 fader
- Grid address scroll vertikal
- Minimum window: 1280×720 (skripsi demo ukuran umum)

---

## 5. Checklist Fidelity (untuk QC nanti)
- [ ] Semua elemen memakai token di atas (tidak ada warna hardcode)
- [ ] Zero emoji di chrome UI (R3) — pakai icon geometris (QPainter/SVG)
- [ ] UPPERCASE label utama
- [ ] Highlight aktif selalu accent-blue #5C96FD (bukan hijau/hitam random)
- [ ] Status: hijau=active, merah=error, kuning=warning
- [ ] Sudut tajam 2-4px (khas GrandMA3)
- [ ] ArtNet pill, Play/Pause toggle tunggal, Blackout circle di header
- [ ] Empty state: logo transparan + prompt

---

## 6. Contoh Screenshot (opsional untuk skripsi BAB 4)
Screenshot asli app diambil dengan `QWidget.grab()` (bukan AI) — sesuai revisi skripsi v5.5.
