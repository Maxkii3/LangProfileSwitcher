"""Tray controller: owns the config, the hotkey, background switching and the exit/revert flow."""
from __future__ import annotations

import getpass
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QActionGroup
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from . import core, theme, winlang
from .hotkey import GlobalHotkey
from .ui import SettingsWindow, repolish

APP_NAME = "LangProfileSwitcher"
LOG_PATH = core.CONFIG_DIR / "error.log"


def log(text: str) -> None:
    core.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {text}\n")


class Controller(QObject):
    _applied = Signal(str, object, object)  # profile id, exception | None, follow-up callable | None
    _scanned = Signal(list)

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.pool = ThreadPoolExecutor(max_workers=1)  # one writer: switches never overlap
        self.busy = False
        self.window: SettingsWindow | None = None
        self.current = winlang.read_current()
        loaded = core.load()
        self.first_run = loaded is None
        self.cfg = loaded or core.seed(self.current)
        core.merge_languages(self.cfg, self.current)
        self.matched = core.match_profile(self.cfg, self.tags)
        core.save(self.cfg)

        self._applied.connect(self._on_applied)
        self._scanned.connect(self._on_scanned)

        self.menu = QMenu()
        self.menu.setWindowFlags(self.menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.menu.setAttribute(Qt.WA_TranslucentBackground)  # lets the QSS radius show
        self.menu.aboutToShow.connect(self._build_menu)
        self.tray = QSystemTrayIcon(self)
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self._tray_clicked)
        self.update_tray()
        self.tray.show()

        self.hotkey = GlobalHotkey(self.toggle)
        if err := self.hotkey.set(self.cfg.hotkey):
            self.tray.showMessage("Hotkey not registered", err, QSystemTrayIcon.Warning)
        self.rescan()

    # ---- state ------------------------------------------------------------------------
    @property
    def tags(self) -> list[str]:
        return [t for t, _ in self.current]

    @property
    def display_tag(self) -> str | None:
        return core.display_tag(self.cfg, self.tags)

    def refresh(self) -> bool:
        """Re-read the live list (registry, instant). True if anything visible changed."""
        before = (self.current, self.matched)
        try:
            self.current = winlang.read_current()
        except OSError as e:
            log(f"read_current failed: {e}")
            return False
        grew = core.merge_languages(self.cfg, self.current)
        self.matched = core.match_profile(self.cfg, self.tags)
        if grew:
            core.save(self.cfg)
        self.update_tray()
        return grew or before != (self.current, self.matched)

    def changed(self) -> None:
        """The settings window edited the config."""
        self.matched = core.match_profile(self.cfg, self.tags)
        core.save(self.cfg)
        self.update_tray()

    def rescan(self) -> None:
        def done(f):
            self._scanned.emit(f.result() if not f.exception() else [])
        self.pool.submit(winlang.installed_languages).add_done_callback(done)

    def _on_scanned(self, installed: list) -> None:
        self.refresh()
        if core.merge_languages(self.cfg, self.current, installed, key=winlang.locale_key):
            core.save(self.cfg)
        self._reload_window()

    # ---- switching --------------------------------------------------------------------
    def switch(self, pid: str, then=None) -> None:
        p = self.cfg.profile(pid)
        if self.busy or not p:
            return
        self.refresh()
        if pid == self.matched:
            if then:
                then()
            return
        entries = [(t, self.cfg.languages.get(t, [])) for t in p.tags]
        self.busy = True
        self.update_tray()
        self._reload_window()
        self.pool.submit(winlang.apply_languages, entries).add_done_callback(
            lambda f: self._applied.emit(pid, f.exception(), then))

    def _on_applied(self, pid: str, err, then) -> None:
        self.busy = False
        if err is None:
            core.record_applied(self.cfg, pid)
            core.save(self.cfg)
        self.refresh()
        self._reload_window()
        if err is not None:
            name = self.cfg.profile(pid).name if self.cfg.profile(pid) else "profile"
            log(f"switch to {name} failed: {err!r}")
            self._error(f"Could not switch to {name}", str(err))
        elif then:
            then()

    def toggle(self) -> None:
        if self.busy:
            return
        self.refresh()
        target = core.toggle_target(self.cfg, self.matched)
        if target:
            self.switch(target)
        else:
            self.open_settings()

    def set_hotkey(self, text: str) -> str | None:
        if err := self.hotkey.set(text):
            self.hotkey.set(self.cfg.hotkey)
            return err
        self.cfg.hotkey = text
        core.save(self.cfg)
        self.update_tray()
        return None

    # ---- tray -------------------------------------------------------------------------
    def update_tray(self) -> None:
        p = self.cfg.profile(self.matched)
        color = theme.MUTED if self.busy or not p else theme.RAUSCH
        self.tray.setIcon(theme.badge_icon(p.name[:1].upper() if p else "?", color))
        state = "Switching…" if self.busy else f"{p.name}: {', '.join(p.tags)}" if p else "Custom language list"
        self.tray.setToolTip(f"Language profiles\n{state}")

    def _build_menu(self) -> None:
        self.refresh()
        m = self.menu
        m.clear()
        m.addAction("Switching…" if self.busy else "Input language profile").setEnabled(False)
        group = QActionGroup(m)
        for p in self.cfg.profiles:
            a = m.addAction(p.name + ("  (default)" if p.id == self.cfg.default_id else ""))
            a.setCheckable(True)
            a.setChecked(p.id == self.matched)
            a.setEnabled(not self.busy)
            a.triggered.connect(lambda _=False, pid=p.id: self.switch(pid))
            group.addAction(a)
        m.addSeparator()
        m.addAction("Settings / Manage Profiles", self.open_settings)
        m.addAction("Exit", self.request_exit)

    def _tray_clicked(self, reason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self.toggle()

    def _error(self, title: str, text: str) -> None:
        if self.window and self.window.isVisible():
            QMessageBox.warning(self.window, title, text)
        else:
            self.tray.showMessage(title, text, QSystemTrayIcon.Warning)

    # ---- window -----------------------------------------------------------------------
    def open_settings(self) -> None:
        if not self.window:
            self.window = SettingsWindow(self)
        self.refresh()
        self.window.reload()
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    def _reload_window(self) -> None:
        if self.window and self.window.isVisible():
            self.window.reload()

    def window_hidden(self) -> None:
        if not self.cfg.tray_hint_shown:
            self.tray.showMessage("Still running", "Language Profiles lives in the tray. Use Exit in its menu to quit.")
            self.cfg.tray_hint_shown = True
            core.save(self.cfg)

    # ---- exit -------------------------------------------------------------------------
    def request_exit(self) -> None:
        if self.busy:
            self.tray.showMessage("Please wait", "A language switch is still running.")
            return
        self.refresh()
        default = self.cfg.default
        if default and self.matched != default.id:
            box = QMessageBox(self.window if self.window and self.window.isVisible() else None)
            box.setWindowTitle("Exit Language Profiles")
            box.setWindowIcon(theme.app_icon())
            box.setText("You are currently on a restricted profile. Do you want to revert to the default "
                        f"profile ({default.name}) before exiting?")
            revert = box.addButton("Revert and Exit", QMessageBox.AcceptRole)
            repolish(revert, "kind", "primary")
            leave = box.addButton("Exit without Reverting", QMessageBox.DestructiveRole)
            box.addButton("Cancel", QMessageBox.RejectRole)
            box.setDefaultButton(revert)
            box.exec()
            if box.clickedButton() is revert:
                self.switch(default.id, then=self.quit)
                return
            if box.clickedButton() is not leave:
                return
        self.quit()

    def quit(self) -> None:
        self.hotkey.clear()
        core.save(self.cfg)
        self.tray.hide()
        self.pool.shutdown(wait=False, cancel_futures=True)
        self.app.quit()


def _excepthook(kind, value, tb) -> None:
    # a windowed .exe has no console: keep a trace instead of dying silently
    log("".join(traceback.format_exception(kind, value, tb)))


def main() -> int:
    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)
    theme.apply(app)
    app.setWindowIcon(theme.app_icon())

    # single instance per Windows user: a second launch just opens the first one's settings
    name = f"{APP_NAME}-{getpass.getuser()}"
    sock = QLocalSocket()
    sock.connectToServer(name)
    if sock.waitForConnected(500):
        sock.write(b"show")
        sock.waitForBytesWritten(500)
        return 0
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, APP_NAME, "No system tray is available.")
        return 1

    ctrl = Controller(app)
    server = QLocalServer()
    QLocalServer.removeServer(name)  # clear a stale socket left by a crash
    server.listen(name)

    def on_connection():
        server.nextPendingConnection().disconnectFromServer()
        ctrl.open_settings()
    server.newConnection.connect(on_connection)

    if ctrl.first_run or "--settings" in sys.argv:
        ctrl.open_settings()
    return app.exec()
