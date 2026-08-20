"""Design tokens + QSS — GrandMA3-inspired dark theme (DESIGN.md §2, R5).

Sumber warna dari analisis pixel image_01..05.png (R5):
  bg-deep #000000, bg-base #0F0F0F, bg-panel #121215, bg-elevated #1C1C1E,
  bg-toolbar #26282A, accent-blue #5C96FD, ok-green #00B300,
  warn-yellow #F1C40F, danger-red #FF3333, magenta #FF00FF.
"""
from __future__ import annotations

# ----------------------------------------------------------------------
# Design tokens (DESIGN.md §2)
# ----------------------------------------------------------------------
COLORS: dict[str, str] = {
    "bg_deep": "#000000",
    "bg_base": "#0F0F0F",
    "bg_panel": "#121215",
    "bg_elevated": "#1C1C1E",
    "bg_toolbar": "#26282A",
    "border": "#333333",
    "border_strong": "#2A2A2E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#9A9AA0",
    "text_dim": "#6E6E76",
    "accent_blue": "#5C96FD",
    "accent_cyan": "#52CDEA",
    "ok_green": "#00B300",
    "warn_yellow": "#F1C40F",
    "danger_red": "#FF3333",
    "magenta": "#FF00FF",
    "teal": "#0F9B9B",
}

# ----------------------------------------------------------------------
# Fonts (DESIGN.md §2.3)
# ----------------------------------------------------------------------
FONT_UI = "Segoe UI"
FONT_MONO = "Consolas"

# ----------------------------------------------------------------------
# QSS
# ----------------------------------------------------------------------
def build_qss() -> str:
    c = COLORS
    return f"""
/* ===== ZZLUXORA v9 — GrandMA3 dark theme ===== */
QMainWindow, QWidget {{
    background-color: {c["bg_base"]};
    color: {c["text_primary"]};
    font-family: "{FONT_UI}";
    font-size: 10pt;
}}

QPushButton {{
    background-color: {c["bg_toolbar"]};
    border: 1px solid {c["border"]};
    border-radius: 2px;
    color: {c["text_primary"]};
    padding: 5px 12px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {c["bg_elevated"]};
    border-color: {c["accent_blue"]};
}}
QPushButton:pressed {{
    background-color: {c["accent_blue"]};
    color: #000000;
}}
QPushButton:disabled {{
    color: {c["text_dim"]};
    background-color: {c["bg_panel"]};
}}

QPushButton#primaryBtn {{
    background-color: {c["accent_blue"]};
    color: #000000;
    border: none;
}}
QPushButton#dangerBtn {{
    background-color: transparent;
    border: 1px solid {c["danger_red"]};
    color: {c["danger_red"]};
}}

QLineEdit, QSpinBox, QComboBox {{
    background-color: {c["bg_deep"]};
    border: 1px solid {c["border"]};
    border-radius: 2px;
    padding: 4px 6px;
    color: {c["text_primary"]};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {c["accent_blue"]};
}}

QListWidget, QTreeWidget, QTableWidget {{
    background-color: {c["bg_deep"]};
    border: 1px solid {c["border"]};
    border-radius: 0px;
    color: {c["text_primary"]};
}}
QListWidget::item:selected, QTableWidget::item:selected {{
    background-color: {c["accent_blue"]};
    color: #000000;
}}
QListWidget::item:hover {{
    background-color: {c["bg_elevated"]};
}}

QSlider::groove:horizontal {{
    background: {c["bg_toolbar"]};
    height: 6px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {c["accent_blue"]};
    width: 10px;
    margin: -4px 0;
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {c["accent_blue"]};
}}

QTabBar::tab {{
    background: {c["bg_panel"]};
    color: {c["text_secondary"]};
    padding: 6px 14px;
    border: 1px solid {c["border"]};
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {c["accent_blue"]};
    color: #000000;
}}
QTabBar::tab:hover {{
    background: {c["bg_elevated"]};
}}

QMenuBar {{
    background-color: {c["bg_toolbar"]};
    color: {c["text_primary"]};
}}
QMenuBar::item:selected {{
    background-color: {c["accent_blue"]};
    color: #000000;
}}
QMenu {{
    background-color: {c["bg_elevated"]};
    border: 1px solid {c["border"]};
    color: {c["text_primary"]};
}}
QMenu::item:selected {{
    background-color: {c["accent_blue"]};
    color: #000000;
}}

QScrollBar:vertical {{
    background: {c["bg_panel"]};
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {c["bg_toolbar"]};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
}}

QStatusBar {{
    background-color: {c["bg_toolbar"]};
    color: {c["text_secondary"]};
}}

QToolTip {{
    background-color: {c["bg_elevated"]};
    color: {c["text_primary"]};
    border: 1px solid {c["accent_blue"]};
}}
"""
