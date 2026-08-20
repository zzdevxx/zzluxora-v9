"""MainWindow — aplikasi shell (R3 §3, §4, DESIGN.md §3).

Layout (dari feedback_v2.txt):
  - MenuBar: File / View / Help (R3 §4)
  - Header: [Icon ZZLUXORA] [project name] [ArtNet pill] [Play/Pause] [Blackout]
  - Sidebar: 5 items + hamburger (R3 §3)
  - Stacked pages: Fixture Manager / Function Manager / Program / Virtual Console / Setup

Tanpa splash screen (D7). Geometric icon saja — no emoji (user preference).
"""
from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from zzluxora.app import AppContext
from zzluxora.core.project_io import ProjectData, load_project, save_project
from zzluxora.ui.styles import COLORS


def make_zzluxora_icon() -> QIcon:
    """Icon geometris ZZLUXORA: kotak + chevron (no emoji)."""
    pm = QPixmap(32, 32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    # frame
    p.setPen(QPen(QColor(COLORS["accent_blue"]), 2))
    p.setBrush(Qt.NoBrush)
    p.drawRect(4, 4, 24, 24)
    # chevron kanan
    p.setPen(QPen(QColor(COLORS["accent_cyan"]), 3))
    p.drawLine(12, 12, 18, 16)
    p.drawLine(12, 20, 18, 16)
    p.end()
    return QIcon(pm)


class MainWindow(QMainWindow):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("ZZLUXORA")
        self.setWindowIcon(make_zzluxora_icon())
        self.resize(1280, 800)
        self._build_menubar()
        self._build_header()
        self._build_body()
        self._start_frame_loop()

    # ------------------------------------------------------------------
    # MenuBar: File / View / Help (R3 §4)
    # ------------------------------------------------------------------
    def _build_menubar(self) -> None:
        mb = self.menuBar()
        file_menu = mb.addMenu("File")
        self.act_open = QAction("Open Project", self)
        self.act_save = QAction("Save Project", self)
        self.act_save_as = QAction("Save As...", self)
        self.act_exit = QAction("Exit", self)
        file_menu.addAction(self.act_open)
        file_menu.addAction(self.act_save)
        file_menu.addAction(self.act_save_as)
        file_menu.addSeparator()
        file_menu.addAction(self.act_exit)

        view_menu = mb.addMenu("View")
        self.act_toggle_sidebar = QAction("Toggle Sidebar", self)
        view_menu.addAction(self.act_toggle_sidebar)

        help_menu = mb.addMenu("Help")
        self.act_about = QAction("About", self)
        help_menu.addAction(self.act_about)

    # ------------------------------------------------------------------
    # Header (R3 §3): [icon][project][ArtNet pill][Play/Pause][Blackout]
    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        header = QWidget()
        header.setObjectName("headerBar")
        lay = QHBoxLayout(header)
        lay.setContentsMargins(10, 6, 10, 6)
        lay.setSpacing(8)

        # Hamburger toggle (R3 §99: pojok kiri atas, 3 strip, tetap sama
        # saat buka/tutup)
        self.ui_hamburger = QPushButton("≡")
        self.ui_hamburger.setObjectName("hamburgerBtn")
        self.ui_hamburger.setFixedSize(28, 28)
        self.ui_hamburger.setToolTip("Toggle Sidebar")
        self.ui_hamburger.clicked.connect(self.toggle_sidebar)
        lay.addWidget(self.ui_hamburger)

        self.ui_icon = QLabel()
        self.ui_icon.setPixmap(make_zzluxora_icon().pixmap(24, 24))
        lay.addWidget(self.ui_icon)

        self.ui_project_label = QLabel(self.ctx.project_name)
        self.ui_project_label.setObjectName("projectLabel")
        lay.addWidget(self.ui_project_label)
        lay.addStretch(1)

        # ArtNet pill — klik untuk buka dialog koneksi (R3 §3)
        self.ui_artnet_pill = QPushButton("ART-NET")
        self.ui_artnet_pill.setObjectName("artnetPill")
        self.ui_artnet_pill.setCheckable(True)
        self.ui_artnet_pill.setChecked(False)
        lay.addWidget(self.ui_artnet_pill)

        # Play / Pause toggle
        self.ui_play_pause = QPushButton("PLAY")
        self.ui_play_pause.setObjectName("playPauseBtn")
        self.ui_play_pause.setCheckable(True)
        lay.addWidget(self.ui_play_pause)

        # Blackout toggle (R3 §3)
        self.ui_blackout = QPushButton("BLACKOUT")
        self.ui_blackout.setObjectName("blackoutBtn")
        self.ui_blackout.setCheckable(True)
        lay.addWidget(self.ui_blackout)

        self._header_bar = header

    # ------------------------------------------------------------------
    # Body: sidebar (5 items) + stacked pages
    # ------------------------------------------------------------------
    def _build_body(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._header_bar)

        body = QWidget()
        lay = QHBoxLayout(body)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        root.addWidget(body, 1)

        self.ui_sidebar = QListWidget()
        self.ui_sidebar.setObjectName("sidebar")
        self.ui_sidebar.setFixedWidth(200)
        # Sidebar TERTUTUP secara default (R3 §103)
        self.ui_sidebar.setVisible(False)
        for label in ("Program", "Fixture List", "Fixture Editor",
                      "Settings", "About"):
            item = QListWidgetItem(label)
            item.setSizeHint(item.sizeHint())
            self.ui_sidebar.addItem(item)
        lay.addWidget(self.ui_sidebar)

        self.ui_pages = QStackedWidget()
        self.ui_pages.setObjectName("pages")

        # DQ1/G8: tab utama tengah ala QLC+ (posisi bawah/South, 5 section)
        self.ui_main_tabs = QTabWidget()
        self.ui_main_tabs.setObjectName("mainTabs")
        self.ui_main_tabs.setTabPosition(QTabWidget.South)

        # ── Panel nyata per sidebar (R3 §3) ────────────────────────────
        from zzluxora.ui.panels.address_panel import AddressPanel
        from zzluxora.ui.panels.analyze_panel import AnalyzePanel
        from zzluxora.ui.panels.chase_panel import ChasePanel
        from zzluxora.ui.panels.fixture_list import FixtureListPanel
        from zzluxora.ui.panels.mixer_panel import MixerPanel
        from zzluxora.ui.panels.output_panel import OutputPanel
        from zzluxora.ui.panels.page_panel import PagePanel
        from zzluxora.ui.panels.preview_panel import PreviewPanel
        from zzluxora.ui.panels.fixture_editor import FixtureEditor
        from zzluxora.ui.panels.scenes_panel import ScenesPanel
        from zzluxora.ui.panels.settings_panel import SettingsPanel

        # 1) Fixtures — FixtureListPanel (sidebar 1)
        self.panel_fixture = FixtureListPanel(self.ctx)
        self.ui_pages.addWidget(self.panel_fixture)
        self.ui_main_tabs.addTab(self.panel_fixture, "Fixtures")

        # 2) Functions — ChasePanel (sidebar 2)
        self.panel_function = ChasePanel(self.ctx)
        self.ui_pages.addWidget(self.panel_function)
        self.ui_main_tabs.addTab(self.panel_function, "Functions")

        # 3) Program — 8 sub-tab (M6: Address, Analyze, Scenes, Chase,
        #    Page, Mixer, Preview, Output) — tab bawah ala QLC+ (G8)
        self.program_tabs = QTabWidget()
        self.program_tabs.setObjectName("programTabs")
        self.program_tabs.setTabPosition(QTabWidget.South)
        self.program_tabs.addTab(AddressPanel(self.ctx), "Address")
        self.program_tabs.addTab(AnalyzePanel(self.ctx), "Analyze")
        self.program_tabs.addTab(ScenesPanel(self.ctx), "Scenes")
        self.program_tabs.addTab(ChasePanel(self.ctx), "Chase")
        self.program_tabs.addTab(PagePanel(self.ctx), "Page")
        self.program_tabs.addTab(MixerPanel(self.ctx), "Mixer")
        self.program_tabs.addTab(PreviewPanel(self.ctx), "Preview")
        self.program_tabs.addTab(OutputPanel(self.ctx), "Output")
        self.ui_pages.addWidget(self.program_tabs)
        self.ui_main_tabs.addTab(self.program_tabs, "Program")

        # 4) Virtual Console — PagePanel (sidebar 4)
        self.panel_vc = PagePanel(self.ctx)
        self.ui_pages.addWidget(self.panel_vc)
        self.ui_main_tabs.addTab(self.panel_vc, "Virtual Console")

        # 5) IO — OutputPanel (sidebar 5)
        self.panel_io = SettingsPanel(self.ctx)
        self.ui_pages.addWidget(self.panel_io)
        self.ui_main_tabs.addTab(self.panel_io, "Settings")

        lay.addWidget(self.ui_main_tabs, 1)

        self.ui_sidebar.currentRowChanged.connect(self._show_sidebar_item)
        self.ui_sidebar.currentRowChanged.connect(self._mark_sidebar_active)
        self._mark_sidebar_active(0)

        self._wire_actions()
    def _show_sidebar_item(self, row: int) -> None:
        """Sidebar 5 menu feedback -> tab utama / dialog (DQ2)."""
        mapping = {
            0: ("tab", 2),        # Program -> tab Program
            1: ("tab", 0),        # Fixture List -> tab Fixtures
            2: ("dialog", None),  # Fixture Editor -> dialog
            3: ("tab", 4),        # Settings -> tab Settings
            4: ("dialog", None),  # About -> dialog
        }
        kind, idx = mapping.get(row, ("tab", 0))
        if kind == "tab":
            self._show_main_tab(idx)
        elif row == 2:
            FixtureEditor(self.ctx).exec()
        elif row == 4:
            self._open_about()

    def _show_main_tab(self, idx: int) -> None:
        """Switch main tabs by index."""
        self.ui_main_tabs.setCurrentIndex(idx)
    def _placeholder_page(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lbl = QLabel("Panel under construction")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("placeholderLabel")
        lay.addWidget(lbl)
        return w

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _start_frame_loop(self) -> None:
        """Kirim mixer.get_dmx() → ArtNet setiap ~33ms (30 FPS) saat connected."""
        self._frame_timer = QTimer(self)
        self._frame_timer.setInterval(33)
        self._frame_timer.timeout.connect(self._send_frame)
        self._frame_timer.start()

    def _send_frame(self) -> None:
        self.ctx.artnet.tick(33, dmx=self.ctx.mixer.get_dmx())

    def closeEvent(self, event) -> None:
        self.ctx.artnet.close()
        super().closeEvent(event)

    def toggle_sidebar(self) -> None:
        # Hanya bisa dibuka setelah project di-load (R3 §107)
        if self.ctx.project_filepath is None and not self.ui_sidebar.isVisible():
            return
        self.ui_sidebar.setVisible(not self.ui_sidebar.isVisible())

    def _mark_sidebar_active(self, row: int) -> None:
        """Marker (garis biru) pada item sidebar aktif (R3 §72)."""
        for i in range(self.ui_sidebar.count()):
            item = self.ui_sidebar.item(i)
            font = item.font()
            if i == row:
                item.setBackground(QColor(COLORS["accent_blue"] + "22"))
                font.setBold(True)
            else:
                item.setBackground(QColor("transparent"))
                font.setBold(False)
            item.setFont(font)

    def _wire_actions(self) -> None:
        self.act_toggle_sidebar.triggered.connect(self.toggle_sidebar)
        self.act_exit.triggered.connect(self.close)
        self.act_about.triggered.connect(self._open_about)
        self.act_open.triggered.connect(self._open_project)
        self.act_save.triggered.connect(self._save_project)
        self.act_save_as.triggered.connect(self._save_project_as)
        self.ui_play_pause.toggled.connect(self._on_play_toggle)
        self.ui_blackout.toggled.connect(self._on_blackout_toggle)

    # ── File → Open/Save (.zlx via project_io) ────────────────────────
    def _open_project(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "ZZLUXORA Project (*.zlx);;All Files (*)"
        )
        if not path:
            return
        try:
            data = load_project(path)
            self.ctx.set_project(path)
            self.ctx.fixtures = data.fixtures
            self.ui_project_label.setText(self.ctx.project_name)
            self.ui_sidebar.setVisible(True)  # terbuka setelah load (R3 §107)
            self.ui_main_tabs.widget(0).refresh_from_ctx()
        except Exception as exc:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Open Project", f"Cannot open project:\n{exc}")

    def _save_project(self) -> None:
        if not self.ctx.project_filepath:
            return self._save_project_as()
        data = ProjectData(
            project_name=self.ctx.project_name,
            fixtures=self.ctx.fixtures,
        )
        save_project(data, self.ctx.project_filepath)

    def _save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", self.ctx.project_name,
            "ZZLUXORA Project (*.zlx)"
        )
        if not path:
            return
        if not path.lower().endswith(".zlx"):
            path += ".zlx"
        self.ctx.set_project(path)
        data = ProjectData(
            project_name=self.ctx.project_name,
            fixtures=self.ctx.fixtures,
        )
        save_project(data, path)
        self.ui_project_label.setText(self.ctx.project_name)

    def _open_about(self) -> None:
        from zzluxora.ui.panels.about_panel import AboutDialog
        AboutDialog(self.ctx, self).exec()

    def _on_play_toggle(self, on: bool) -> None:
        self.ui_play_pause.setText("PAUSE" if on else "PLAY")
        # TODO M8: hubungkan ke playback_service (scene execution)

    def _on_blackout_toggle(self, on: bool) -> None:
        if on:
            self.ctx.mixer.blackout()
            self.ctx.artnet.blackout()
            self.ui_blackout.setText("BLACKOUT")
        else:
            self.ctx.mixer.master = 255
            self.ui_blackout.setText("BLACKOUT")
