"""System-wide hotkey via RegisterHotKey; WM_HOTKEY arrives on the GUI thread's message queue."""
from __future__ import annotations

import ctypes
from ctypes import wintypes

from PySide6.QtCore import QAbstractNativeEventFilter, QTimer, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication

WM_HOTKEY = 0x0312
MOD_ALT, MOD_CONTROL, MOD_SHIFT, MOD_WIN, MOD_NOREPEAT = 0x1, 0x2, 0x4, 0x8, 0x4000
HOTKEY_ID = 0x4C50
_MODS = {Qt.ControlModifier: MOD_CONTROL, Qt.AltModifier: MOD_ALT, Qt.ShiftModifier: MOD_SHIFT, Qt.MetaModifier: MOD_WIN}
_user32 = ctypes.WinDLL("user32", use_last_error=True)


def to_native(text: str) -> tuple[int, int] | None:
    """'Ctrl+Alt+L' -> (modifiers, virtual key). Only letters, digits and F-keys with Ctrl/Alt/Win."""
    seq = QKeySequence(text, QKeySequence.PortableText)
    if seq.count() != 1:
        return None
    combo = seq[0]
    mods = sum(v for m, v in _MODS.items() if combo.keyboardModifiers() & m)
    if not mods & (MOD_CONTROL | MOD_ALT | MOD_WIN):  # Shift+X alone would swallow normal typing
        return None
    key = combo.key().value
    if Qt.Key_A.value <= key <= Qt.Key_Z.value or Qt.Key_0.value <= key <= Qt.Key_9.value:
        vk = key  # Qt and Windows share ASCII codes here
    elif Qt.Key_F1.value <= key <= Qt.Key_F24.value:
        vk = 0x70 + key - Qt.Key_F1.value
    else:
        return None
    return mods, vk


class GlobalHotkey(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback
        self._registered = False
        QApplication.instance().installNativeEventFilter(self)

    def set(self, text: str) -> str | None:
        """Register (or clear with ""). Returns an error message, or None on success."""
        self.clear()
        if not text:
            return None
        native = to_native(text)
        if not native:
            return "Use Ctrl, Alt or Win plus a letter, digit or F-key."
        if not _user32.RegisterHotKey(None, HOTKEY_ID, native[0] | MOD_NOREPEAT, native[1]):
            return f"{text} is already used by another app."
        self._registered = True
        return None

    def clear(self) -> None:
        if self._registered:
            _user32.UnregisterHotKey(None, HOTKEY_ID)
            self._registered = False

    def nativeEventFilter(self, event_type, message):
        if bytes(event_type) == b"windows_generic_MSG":
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                QTimer.singleShot(0, self._callback)  # leave the native dispatch before doing real work
                return True, 0
        return False, 0
