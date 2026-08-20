"""Fixture Editor — buat/edit fixture (R1 QLC+ Fixture Editor).

  - name field
  - type selector (template kanal: 8ch PAR RGBW / 4ch RGB / ...)
  - SAVE menambahkan fixture ke AppContext.fixtures
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)

from zzluxora.app import AppContext
from zzluxora.core.models import Fixture

# Template kanal (R2: PAR LED RGBW 8-kanal; plus varian umum)
TYPE_TEMPLATES: dict[str, list[str]] = {
    "PAR RGBW 8ch": ["Dimmer", "Red", "Green", "Blue", "Empty", "Program", "Speed", "Empty"],
    "PAR RGB 4ch": ["Dimmer", "Red", "Green", "Blue"],
    "RGB 3ch": ["Red", "Green", "Blue"],
    "Dimmer 1ch": ["Dimmer"],
    "Strobe 2ch": ["Dimmer", "Strobe"],
}


class FixtureEditor(QDialog):
    def __init__(self, ctx: AppContext, parent=None) -> None:
        super().__init__(parent)
        self.ctx = ctx
        self.setWindowTitle("Fixture Editor")
        self.setMinimumWidth(360)

        form = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.name_edit.setObjectName("nameEdit")
        self.name_edit.setPlaceholderText("e.g. PAR1")
        form.addRow("Name:", self.name_edit)

        self.type_combo = QComboBox()
        self.type_combo.setObjectName("typeCombo")
        self.type_combo.addItems(list(TYPE_TEMPLATES.keys()))
        form.addRow("Type:", self.type_combo)

        btns = QHBoxLayout()
        self.btn_cancel = QPushButton("CANCEL")
        self.btn_cancel.clicked.connect(self.reject)
        btns.addWidget(self.btn_cancel)
        self.btn_save = QPushButton("SAVE")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.clicked.connect(self.save)
        btns.addWidget(self.btn_save)
        form.addRow(btns)

    def save(self) -> None:
        name = self.name_edit.text().strip() or "Fixture"
        template = TYPE_TEMPLATES[self.type_combo.currentText()]
        fixture = Fixture(name=name, types=list(template))
        self.ctx.fixtures.append(fixture)
        self.accept()
