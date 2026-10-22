"""Airbnb-inspired tokens (getdesign.md/airbnb): white canvas, ink text, one Rausch accent, soft radii."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from string import Template

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

RAUSCH = "#ff385c"
RAUSCH_ACTIVE = "#e00b41"
RAUSCH_DISABLED = "#ffd1da"
ERROR = "#c13515"
INK = "#222222"
BODY = "#3f3f3f"
MUTED = "#6a6a6a"
MUTED_SOFT = "#929292"
HAIRLINE = "#dddddd"
HAIRLINE_SOFT = "#ebebeb"
BORDER_STRONG = "#c1c1c1"
CANVAS = "#ffffff"
SURFACE_SOFT = "#f7f7f7"
SURFACE_STRONG = "#f2f2f2"
RAUSCH_TINT = "#fff5f7"  # derived, not in the spec: a whisper of Rausch behind the active profile card

# Same relative layout from source and inside the PyInstaller bundle (build.ps1 --add-data).
ASSETS = Path(__file__).resolve().parent / "assets"

# Airbnb Cereal is proprietary; the spec's own fallback chain ends at the system UI font.
FONT = "Segoe UI Variable Text"

QSS = Template("""
* { color: $ink; font-size: 14px; }
QWidget#Root, QDialog, QMessageBox, QInputDialog { background: $canvas; }
QLabel[role="h1"] { font-size: 22px; font-weight: 600; }
QLabel[role="h2"] { font-size: 16px; font-weight: 600; }
QLabel[role="caption"] { font-size: 13px; color: $muted; }
QLabel[role="error"] { font-size: 13px; color: $error; }
QLabel[role="pill"], QLabel[role="status"] {
    font-size: 12px; font-weight: 600; background: $canvas;
    border: 1px solid $hairline; border-radius: 12px; padding: 4px 12px;
}
QFrame#Divider { background: $hairline_soft; border: none; }
QFrame#Banner { background: $surface_soft; border-radius: 14px; }

QPushButton {
    background: $canvas; border: 1px solid $ink; border-radius: 8px;
    padding: 0 18px; min-height: 38px; font-weight: 500;
}
QPushButton:hover { background: $surface_soft; }
QPushButton:pressed { background: $surface_strong; }
QPushButton:focus { border: 2px solid $ink; }
QPushButton:disabled { color: $muted_soft; border-color: $hairline; background: $canvas; }
QPushButton[kind="primary"] {
    background: $rausch; color: $canvas; border: 2px solid $rausch;
    font-size: 16px; min-height: 44px; padding: 0 24px;
}
QPushButton[kind="primary"]:hover, QPushButton[kind="primary"]:pressed { background: $rausch_active; border-color: $rausch_active; }
QPushButton[kind="primary"]:focus { border-color: $ink; }
QPushButton[kind="primary"]:disabled { background: $rausch_disabled; border-color: $rausch_disabled; color: $canvas; }
QPushButton[kind="text"] {
    background: transparent; border: 2px solid transparent; padding: 0 8px; min-height: 32px;
    text-decoration: underline; font-weight: 600;
}
QPushButton[kind="text"]:hover { background: $surface_soft; }
QPushButton[kind="text"]:focus { border-color: $ink; }
QPushButton[kind="text"]:disabled { color: $muted_soft; }

QListView { background: transparent; border: none; outline: 0; }
QLineEdit {
    background: $canvas; border: 1px solid $border_strong; border-radius: 8px;
    padding: 0 12px; min-height: 40px; selection-background-color: $ink;
}
QLineEdit:focus { border: 2px solid $ink; }

QMenu { background: $canvas; border: 1px solid $hairline; border-radius: 12px; padding: 8px 0; }
QMenu::item { padding: 9px 28px 9px 34px; background: transparent; }
QMenu::item:selected { background: $surface_soft; }
QMenu::item:disabled { color: $muted; font-size: 12px; font-weight: 600; }
QMenu::separator { height: 1px; background: $hairline_soft; margin: 6px 0; }
QMenu::indicator { width: 16px; height: 16px; left: 10px; }

QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $border_strong; border-radius: 3px; min-height: 32px; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QToolTip { background: $ink; color: $canvas; border: none; padding: 6px 8px; }
""").substitute(
    ink=INK, canvas=CANVAS, muted=MUTED, muted_soft=MUTED_SOFT, error=ERROR, hairline=HAIRLINE,
    hairline_soft=HAIRLINE_SOFT, border_strong=BORDER_STRONG, surface_soft=SURFACE_SOFT,
    surface_strong=SURFACE_STRONG, rausch=RAUSCH, rausch_active=RAUSCH_ACTIVE, rausch_disabled=RAUSCH_DISABLED,
)


def font(px: int, weight: QFont.Weight = QFont.Normal) -> QFont:
    f = QFont(FONT)
    f.setPixelSize(px)
    f.setWeight(weight)
    return f


def apply(app: QApplication) -> None:
    global FONT
    if FONT not in QFontDatabase.families():
        FONT = "Segoe UI"
    app.setStyle("Fusion")
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)  # the spec has no dark mode; keep dialogs consistent
    app.setFont(font(14))
    app.setStyleSheet(QSS)


@lru_cache(maxsize=32)
def badge_icon(letter: str, color: str) -> QIcon:
    """Filled circle with one white letter: the tray shows the active profile's initial."""
    icon = QIcon()
    for size in (16, 20, 24, 32, 48, 64, 256):
        pm = QPixmap(size, size)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(color))
        p.drawEllipse(0, 0, size, size)
        p.setPen(QColor(CANVAS))
        p.setFont(font(max(9, round(size * 0.6)), QFont.Bold))
        p.drawText(pm.rect(), Qt.AlignCenter, letter)
        p.end()
        icon.addPixmap(pm)
    return icon


@lru_cache(maxsize=8)
def pointer(width: int, dpr: float) -> QPixmap:
    """The pointing hand (assets/niw.png) pre-scaled once per size and screen DPI. Null if the file is missing."""
    pm = QPixmap(str(ASSETS / "niw.png"))
    if pm.isNull():
        return pm
    pm = pm.scaledToWidth(round(width * dpr), Qt.SmoothTransformation)
    pm.setDevicePixelRatio(dpr)
    return pm


def app_icon() -> QIcon:
    return badge_icon("A", RAUSCH)
