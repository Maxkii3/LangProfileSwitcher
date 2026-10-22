"""Render the README screenshots into docs/images from a fixed demo setup.

Never touches the real machine: the language list, keyboard names, PowerShell calls and the hotkey are
all stubbed, and the config lives in a throwaway folder.  Run: python tools/screenshots.py
"""
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
os.environ["LOCALAPPDATA"] = tempfile.mkdtemp(prefix="lps-shots-")  # before langprofile.core reads it
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QPoint, Qt, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QVBoxLayout, QWidget  # noqa: E402

from langprofile import app as appmod, core, hotkey, theme, winlang  # noqa: E402

DEMO = [
    ("en-US", ["0409:00000409"]),
    ("th", ["041E:0000041E"]),
    ("zh-Hans-CN", ["0804:{81D4E9C9-1D3B-41BC-9E6C-4B40BF79E35E}{FA550B04-5AD7-411F-A5AC-CA038EC515D7}"]),
    ("ko", ["0412:{A028AE76-01B1-46C2-99C4-ACD9858AE02F}{B5FE1F02-D5F2-4445-9C03-C568F23C99A1}"]),
]
KEYBOARDS = {"0409": "US", "041E": "Thai Kedmanee", "0804": "Microsoft Pinyin", "0412": "Microsoft IME"}
live = list(DEMO)


def fake_apply(entries):
    live[:] = entries
    return list(live)


winlang.read_current = lambda: list(live)
winlang.apply_languages = fake_apply
winlang.installed_languages = lambda: []
winlang.keyboard_name = lambda tip: KEYBOARDS.get(tip[:4], tip)
hotkey.GlobalHotkey.set = lambda self, text: None


def pump(seconds=0.4):
    end = time.time() + seconds
    while time.time() < end:
        QApplication.processEvents()


def save(widget_or_pixmap, name):
    pm = widget_or_pixmap if hasattr(widget_or_pixmap, "save") else widget_or_pixmap.grab()
    assert pm.save(str(OUT / name)), name
    print("wrote", OUT / name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    theme.apply(app)
    ctrl = appmod.Controller(app)
    full, mini = ctrl.cfg.profiles
    thai = ctrl.cfg.add_profile("Thai typing", ["th", "en-US"])
    ctrl.changed()

    # 1. settings window, Minimal selected and active
    ctrl.switch(mini.id)
    pump(0.8)
    ctrl.open_settings()
    w = ctrl.window
    w.selected_id = mini.id
    w.reload()
    pump()
    save(w, "settings.png")

    # 2. display-language protection banner
    w.selected_id = thai.id
    w.reload()
    pump()
    save(w, "display-language-warning.png")

    # 3. tray menu + the tray icon states
    ctrl._build_menu()
    ctrl.menu.popup(QPoint(40, 40))
    pump()
    menu_pm = ctrl.menu.grab()
    ctrl.menu.hide()
    canvas = QWidget()
    canvas.setObjectName("Root")
    lay = QVBoxLayout(canvas)
    lay.setContentsMargins(28, 24, 28, 28)
    lay.setSpacing(16)
    title = QLabel("Tray icon shows the active profile")
    title.setProperty("role", "h2")
    lay.addWidget(title)
    grid = QGridLayout()
    grid.setHorizontalSpacing(28)
    for col, (letter, color, caption) in enumerate((("F", theme.RAUSCH, "Full"), ("M", theme.RAUSCH, "Minimal"),
                                                    ("?", theme.MUTED, "Switching / custom"))):
        icon = QLabel()
        icon.setPixmap(theme.badge_icon(letter, color).pixmap(40, 40))
        grid.addWidget(icon, 0, col, Qt.AlignHCenter)
        cap = QLabel(caption)
        cap.setProperty("role", "caption")
        grid.addWidget(cap, 1, col, Qt.AlignHCenter)
    lay.addLayout(grid)
    menu_lbl = QLabel()
    menu_lbl.setPixmap(menu_pm)
    lay.addWidget(menu_lbl, 0, Qt.AlignLeft)
    canvas.adjustSize()
    canvas.show()
    pump()
    save(canvas, "tray-menu.png")
    canvas.hide()

    # 4. safe-exit prompt (we are on Minimal, default is Full)
    def grab_dialog():
        box = app.activeModalWidget()
        save(box, "exit-prompt.png")
        next(b for b in box.buttons() if b.text() == "Cancel").click()
    QTimer.singleShot(500, grab_dialog)
    ctrl.request_exit()

    ctrl.tray.hide()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
