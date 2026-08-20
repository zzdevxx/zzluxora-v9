import io, re, ast, sys

f = r"C:\ANDREAS\SCRIPT3\src\zzluxora\ui\main_window.py"
with io.open(f, encoding="utf-8") as fh:
    c = fh.read()

# 1) tambah import FixtureEditor + SettingsPanel
c = c.replace(
    "from zzluxora.ui.panels.scenes_panel import ScenesPanel",
    "from zzluxora.ui.panels.fixture_editor import FixtureEditor\n"
    "        from zzluxora.ui.panels.scenes_panel import ScenesPanel\n"
    "        from zzluxora.ui.panels.settings_panel import SettingsPanel",
)

# 2) connect sidebar ke handler baru
c = c.replace(
    "        self.ui_sidebar.currentRowChanged.connect(self._show_main_tab)",
    "        self.ui_sidebar.currentRowChanged.connect(self._show_sidebar_item)",
)

# 3) ganti _show_main_tab dengan _show_sidebar_item routing
old = (
    "    def _show_main_tab(self, row: int) -> None:\n"
    '        """Sidebar row -> main tab (QLC+). Holder ui_pages tetap utk mapping."""\n'
    "        if 0 <= row < self.ui_main_tabs.count():\n"
    "            self.ui_main_tabs.setCurrentIndex(row)"
)
new = (
    "    def _show_sidebar_item(self, row: int) -> None:\n"
    '        """Sidebar 5 menu feedback -> tab utama / dialog (DQ2)."""\n'
    "        mapping = {\n"
    "            0: (\"tab\", 2),        # Program -> tab Program\n"
    "            1: (\"tab\", 0),        # Fixture List -> tab Fixtures\n"
    "            2: (\"dialog\", None),  # Fixture Editor -> dialog\n"
    "            3: (\"tab\", 4),        # Settings -> tab Settings\n"
    "            4: (\"dialog\", None),  # About -> dialog\n"
    "        }\n"
    "        kind, idx = mapping.get(row, (\"tab\", 0))\n"
    "        if kind == \"tab\":\n"
    "            self.ui_main_tabs.setCurrentIndex(idx)\n"
    "        elif row == 2:\n"
    "            FixtureEditor(self.ctx).exec()\n"
    "        elif row == 4:\n"
    "            self._open_about()"
)
if old in c:
    c = c.replace(old, new)
else:
    print("OLD _show_main_tab tidak ketemu!")
    for i, l in enumerate(c.splitlines()):
        if "_show_main_tab" in l:
            print(i, l)

with io.open(f, "w", encoding="utf-8", newline="") as fh:
    fh.write(c)

ast.parse(open(f, encoding="utf-8").read())
print("AST OK")
