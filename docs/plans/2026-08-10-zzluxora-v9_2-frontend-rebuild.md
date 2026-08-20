# ZZLUXORA v9.2 — Audit & Rombak Front-End (Komposisi QLC+ + GrandMA3)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rombak front-end ZZLUXORA v9 agar komposisinya "enak dilihat" seperti QLC+ (tab tengah bawah), tema GrandMA3, dan 100% sesuai feedback_v1.txt + feedback_v2.txt (tanpa splash screen — D7).

**Architecture:** Gabungan keputusan user: **QTabWidget besar di tengah (tab bawah/South, icon+label ala QLC+) + sidebar kiri hamburger 5 menu (Program, Fixture List, Fixture Editor, Settings, About) ala GrandMA3**. Basis: v9 (SCRIPT3, 226 tests, core zero-Qt). Ambil HelpDialog + SIDEBAR_ITEMS persis dari v8 (SCRIPT2 — sudah sesuai feedback).

**Tech Stack:** Python 3.14, PySide6, pytest (TDD), pytest-cov, venv `C:\ANDREAS\SCRIPT\.venv`.

**Reference (jangan dimodifikasi):**
- `C:\ANDREAS\SCRIPT\notes\feedback_v1.txt` (190 baris — mentah)
- `C:\ANDREAS\SCRIPT\notes\feedback_v2.txt` (324 baris — terstruktur, spec utama)
- `C:\ANDREAS\SCRIPT\qlcplus\ui\src\app.cpp` (L217-296: QTabWidget tengah, tab South, icon+label)
- `C:\ANDREAS\SCRIPT2\zzluxora\widgets\help_modal.py` (HelpDialog lengkap — port)
- `C:\ANDREAS\SCRIPT2\zzluxora\widgets\sidebar.py` (SIDEBAR_ITEMS + PANEL_TITLE — port)
- `C:\ANDREAS\SCRIPT3\src\zzluxora\ui\styles.py` (tokens GrandMA3 — tidak diubah)

---

## Keputusan (dari user)

| ID | Keputusan |
|---|---|
| D7 | **TANPA splash screen** (override feedback §2) |
| DQ1 | **Gabungan**: tab QLC+ tengah + sidebar hamburger kiri 5 menu |
| DQ2 | Label sidebar **persis feedback**: Program, Fixture List, Fixture Editor, Settings, About |

---

## Hasil Audit (gap v9 vs feedback)

| Gap | Spec (v1/v2) | v9 sekarang | Task |
|---|---|---|---|
| G1 | Help → About + **Shortcuts/Keyboard Shortcuts** | ❌ Help cuma About | T3 |
| G2 | View → **5 item** + marker sinkron | ⚠️ View cuma "Toggle Sidebar" | T4 |
| G3 | Sidebar: **Program, Fixture List, Fixture Editor, Settings, About** | ⚠️ "Fixture Manager, Function Manager, Program, Virtual Console, Setup" | T2 |
| G4 | Art-Net pill klik → **buka tab Output** | ⚠️ belum navigasi | T5 |
| G5 | Play/Pause 1 tombol | ✅ sudah | — |
| G6 | Blackout **icon lingkaran hitam** | ⚠️ tombol teks "BLACKOUT" | T6 |
| G7 | Empty state: icon+ZZLUXORA **samar** + prompt | ⚠️ belum ada | T7 |
| G8 | Tab **bawah (South)** ala QLC+ | ❌ program_tabs default (North) | T1+T8 |
| G9 | Header: [icon+ZZLUXORA][nama project/path] | ⚠️ icon samar, label kecil | T9 |
| G10 | Keterangan kanan tiap tab: **tulisan kurang besar** | ⚠️ banyak tab kecil | T10 |
| G11 | Responsif saat buka/tutup sidebar | ⚠️ fixed width, no animasi | T11 |

---

## Task List (TDD — red → green → commit)

### Task 1: Restruktur MainWindow — tab tengah + sidebar ganda

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` (struktur body)
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_main_tab_widget_exists(qapp, ctx):
    w = MainWindow(ctx)
    assert w.ui_main_tabs is not None
    assert w.ui_main_tabs.tabPosition().name == "South"  # ala QLC+
    labels = [w.ui_main_tabs.tabText(i) for i in range(w.ui_main_tabs.count())]
    assert labels == ["Fixtures", "Functions", "Program", "Virtual Console", "IO"]
    w.close()
```

**Step 2: Run → FAIL** (`ui_main_tabs` belum ada)

**Step 3: Implementasi minimal** — di body: `QHBoxLayout[sidebar | QTabWidget(South, 5 tab)]`. Tab 5 = Fixtures(FixtureListPanel), Functions(ChasePanel), Program(program_tabs 8 sub-tab), Virtual Console(PagePanel), IO(OutputPanel). Program_tabs tetap.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): main QTabWidget ala QLC+ (South, 5 tab)`

### Task 2: Sidebar 5 item persis feedback (DQ2/G3)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` L158-162
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_sidebar_items_exact_feedback(qapp, ctx):
    w = MainWindow(ctx)
    items = [w.ui_sidebar.item(i).text() for i in range(w.ui_sidebar.count())]
    assert items == ["Program", "Fixture List", "Fixture Editor", "Settings", "About"]
    w.close()
```

**Step 2: Run → FAIL** (label lama)

**Step 3: Ganti list label** — `("Program", "Fixture List", "Fixture Editor", "Settings", "About")`; map item→pages:
- Program → program_tabs (index 2)
- Fixture List → FixtureListPanel
- Fixture Editor → FixtureEditorPanel (bikin stub jika belum ada — lihat Task 12)
- Settings → SettingsPanel
- About → AboutPanel (dialog)

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): sidebar 5 item persis feedback_v2 §7`

### Task 3: Help → Shortcuts + Keyboard Shortcuts dialog (G1)

**Files:**
- Create: `src/zzluxora/ui/widgets/help_dialog.py` (port dari v8 help_modal.py)
- Modify: `src/zzluxora/ui/main_window.py` (help_menu: About + Shortcuts + Keyboard Shortcuts)
- Test: `tests/test_help_dialog.py` (baru)

**Step 1: Tulis failing test**

```python
def test_help_menu_has_shortcuts_action(qapp, ctx):
    w = MainWindow(ctx)
    assert w.act_shortcuts is not None
    assert w.act_keyboard_shortcuts is not None
    w.close()
```

**Step 2: RUN → FAIL** (act_shortcuts belum ada)

**Step 3: Implementasi** — Port HelpDialog: title "Shortcut", grid key+desc, Close atas (kanan) + bawah (tengah), tanpa emoji, tanpa "v4". SHORTCUTS update sesuai fitur v9 (Ctrl+1..8 program tabs, Space play, B blackout, F1 help, Ctrl+O/S/Shift+S, dll). Help menu: "Shortcuts" (F1) + "Keyboard Shortcuts" (buka dialog sama) + "About".

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): Help menu - Shortcuts + Keyboard Shortcuts dialog (v2 §6)`

### Task 4: View menu 5 item + marker sinkron (G2)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py`
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_view_menu_five_items_sync_marker(qapp, ctx):
    w = MainWindow(ctx)
    menu = None
    for a in w.menuBar().actions():
        if a.text() == "View":
            menu = a.menu()
    actions = [a.text() for a in menu.actions()]
    assert "Program" in actions and "About" in actions
    w.close()
```

**Step 2: Run → FAIL**

**Step 3: Implementasi** — View menu: Program, Fixture List, Fixture Editor, Settings, About (Ctrl+1..5) → `_show_panel(i)` sinkron sidebar currentRow + marker. Tambahkan "Toggle Sidebar" (Ctrl+0).

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): View menu 5 panel + marker sinkron (v2 §5)`

### Task 5: Art-Net pill navigasi → tab Output (G4)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` (header)
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_artnet_pill_opens_output_tab(qapp, ctx):
    w = MainWindow(ctx)
    w.ui_artnet_pill.click()
    assert w.ui_main_tabs.currentIndex() == 4  # IO/Output
    w.close()
```

**Step 2: Run → FAIL**

**Step 3: Implementasi** — `ui_artnet_pill.clicked → w.ui_main_tabs.setCurrentIndex(4)` (tab IO = Output).

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): artnet pill opens Output tab (v2 §6)`

### Task 6: Blackout icon lingkaran hitam (G6)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` (header) + `styles.py` (opsional)
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_blackout_is_circular_icon(qapp, ctx):
    w = MainWindow(ctx)
    btn = w.ui_blackout
    assert not btn.text()  # bukan tombol teks
    assert btn.minimumWidth() == btn.minimumHeight()  # lingkaran (kotak)
    assert "blackoutBtn" == btn.objectName()
    w.close()
```

**Step 2: Run → FAIL** (masih teks "BLACKOUT")

**Step 3: Implementasi** — QPushButton icon lingkaran (QPixmap 20x20: hitam + border putih/merah), fixed 28x28, tooltip "Blackout", checkable, QSS `border-radius: 14px`.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): blackout circular icon button (v2 §3)`

### Task 7: Empty state samar + prompt saat belum load .zlx (G7)

**Files:**
- Create: `src/zzluxora/ui/widgets/empty_state.py` (port konsep v7)
- Modify: `src/zzluxora/ui/main_window.py`
- Test: `tests/test_empty_state.py` (baru)

**Step 1: Tulis failing test**

```python
def test_empty_state_prompt_when_no_project(qapp, ctx):
    w = MainWindow(ctx)
    assert w.ui_empty_state is not None
    assert w.ui_empty_state.isVisible()
    assert "project" in w.ui_empty_state.text().lower()  # prompt
    w.close()
```

**Step 2: Run → FAIL**

**Step 3: Implementasi** — Saat `project_filepath is None`: body menampilkan empty state (icon ZZLUXORA samar opasitas 0.3 + "Open a project to begin" + instruksi). Setelah load .zlx → empty state hilang.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): empty state samar saat belum load project (v2 §7)`

### Task 8: Program tabs → posisi bawah (South) (G8)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` L190-201
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_program_tabs_south(qapp, ctx):
    w = MainWindow(ctx)
    assert w.program_tabs.tabPosition().name == "South"
    assert w.program_tabs.count() == 8
    w.close()
```

**Step 2: Run → FAIL** (posisi North sekarang)

**Step 3: Implementasi** — `self.program_tabs.setTabPosition(QTabWidget.South)`.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): program tabs South ala QLC+ (G8)`

### Task 9: Header — icon+ZZLUXORA jelas + project path (G9)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` (header L106-112)
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_header_brand_and_path(qapp, ctx):
    w = MainWindow(ctx)
    assert w.ui_brand.text().upper() == "ZZLUXORA"
    assert "untitled.zlx" in w.ui_project_label.text().lower()
    w.close()
```

**Step 2: Run → FAIL** (brand terpisah icon saja, label kecil)

**Step 3: Implementasi** — Header: `[hamburger][icon 20px][QLabel "ZZLUXORA" bold 14px][QLabel path project (dim)]`. Hapus label "ZZLIGHT LUXORA" (sudah tidak ada di v9 — ok).

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): header brand ZZLUXORA + project path (v2 §3)`

### Task 10: Keterangan kanan tab — perbesar (G10)

**Files:**
- Modify: tiap panel dengan corner info (address, analyze, dll)
- Test: `tests/test_*_panel.py` (update style assertions bila ada)

**Step 1: Tulis failing test (satu contoh)**

```python
def test_address_corner_info_large(qapp, ctx):
    p = AddressPanel(ctx)
    lbl = p.findChild(QLabel, "cornerInfo")
    assert "font-size" in lbl.styleSheet() or "12px" in lbl.styleSheet()
    p.close()
```

**Step 2: Run → FAIL**

**Step 3: Implementasi** — QSS `#cornerInfo { font-size: 12px; color: #9A9AA0; }` untuk tiap tab yang punya keterangan kanan (Address, Analyze, Scenes, Chase, Mixer, Preview, Output).

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): perbesar keterangan kanan tiap tab (v1 §46, v2 §8-15)`

### Task 11: Responsif buka/tutup sidebar (G11)

**Files:**
- Modify: `src/zzluxora/ui/main_window.py` (toggle_sidebar)
- Test: `tests/test_main_window.py`

**Step 1: Tulis failing test**

```python
def test_sidebar_toggle_keeps_width(qapp, ctx):
    w = MainWindow(ctx)
    ctx.set_project("p.zlx")
    w.toggle_sidebar()
    assert w.ui_sidebar.width() == 200
    assert not w.ui_sidebar.isHidden()
    w.toggle_sidebar()
    assert w.ui_sidebar.isHidden()
    w.close()
```

**Step 2: Run → FAIL** (perlu project dulu; width berubah)

**Step 3: Implementasi** — Sidebar `setFixedWidth(200)` konsisten saat buka/tutup (hidden vs visible), konten stretch otomatis. Opsional QPropertyAnimation (fade/slide 120ms) — skip jika flaky di offscreen.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): responsive sidebar toggle (v1 §175, v2 §20)`

### Task 12: Fixture Editor stub/tab (G3 bagian 3)

**Files:**
- Create: `src/zzluxora/ui/panels/fixture_editor.py` (port minimal dari v8/v9 fixture_editor)
- Modify: `src/zzluxora/ui/main_window.py` (page Fixture Editor)
- Test: `tests/test_fixture_editor.py` (baru)

**Step 1: Tulis failing test**

```python
def test_fixture_editor_sidebar_page(qapp, ctx):
    w = MainWindow(ctx)
    # Fixture Editor page ada (index 2 di sidebar)
    assert w.ui_pages.count() >= 5
    w.close()
```

**Step 2: Run → FAIL/uncertain**

**Step 3: Implementasi** — Pastikan FixtureEditorPanel ada sebagai page ke-3 (sudah ada di v9 M7? cek `ui/panels/fixture_editor.py` — kalau belum, port dari v8). Wire ke sidebar + View menu.

**Step 4: Run → PASS**

**Step 5: Commit** `feat(ui): fixture editor page wired (v2 §17)`

---

## Menjalankan Test (semua task)

```powershell
$env:QT_QPA_PLATFORM="offscreen"
& "C:\ANDREAS\SCRIPT\.venv\Scripts\python.exe" -m pytest tests/ -q
```

**Gate:** semua test hijau (226 + test baru), coverage ≥ 80%.

## Verifikasi Visual (setelah semua task)

1. `tools/screenshot.py` — tangkap UI, verifikasi komposisi baru
2. `build.py` — PyInstaller build OK
3. Buka via Desktop `ZZLUXORA.bat` — cek: tab tengah bawah (5), sidebar 5 menu, help shortcuts, blackout lingkaran, empty state samar, artnet→output

## Catatan

- Splash screen: **TIDAK dibuat** (D7 override feedback §2) — ulangi jangan pernah tambah.
- Emoji: **nol** — semua icon geometris/teks.
- Core (`src/zzluxora/core/`) tetap **zero-Qt** — semua perubahan di `ui/`.
- UI strings: **English**.
