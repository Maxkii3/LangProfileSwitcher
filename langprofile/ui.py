"""Settings window: profiles on the left, the selected profile's languages on the right."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QPointF, QRect, QRectF, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QFontMetrics, QKeySequence, QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QInputDialog, QKeySequenceEdit, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMessageBox, QPushButton, QStyle, QStyledItemDelegate, QVBoxLayout, QWidget,
)

from . import theme, winlang

if TYPE_CHECKING:
    from .app import Controller

ROLE_ID, ROLE_CAPTION, ROLE_DEFAULT, ROLE_ACTIVE = (Qt.UserRole + i for i in range(4))


def _label(text: str, role: str, wrap: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setProperty("role", role)
    lbl.setWordWrap(wrap)
    return lbl


def _button(text: str, kind: str, slot) -> QPushButton:
    b = QPushButton(text)
    b.setProperty("kind", kind)
    b.setCursor(Qt.PointingHandCursor)
    b.clicked.connect(lambda _=False: slot())
    return b


def repolish(widget: QWidget, name: str, value: str) -> None:
    """Change a QSS-selector property after the widget was already styled."""
    widget.setProperty(name, value)
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def _checked(index) -> bool:
    v = index.data(Qt.CheckStateRole)
    return v == Qt.Checked or v == Qt.Checked.value


class _RowDelegate(QStyledItemDelegate):
    HEIGHT = 64

    def sizeHint(self, option, index):
        return QSize(0, self.HEIGHT)  # width 0: rows fill the viewport, never a horizontal scrollbar

    @staticmethod
    def _background(p: QPainter, option) -> QRectF:
        r = QRectF(option.rect).adjusted(2, 2, -2, -2)
        fill = (theme.SURFACE_STRONG if option.state & QStyle.State_Selected
                else theme.SURFACE_SOFT if option.state & QStyle.State_MouseOver else None)
        if fill:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(fill))
            p.drawRoundedRect(r, 12, 12)
        if option.state & QStyle.State_HasFocus:  # visible keyboard focus ring
            p.setPen(QPen(QColor(theme.INK), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(r.adjusted(1, 1, -1, -1), 12, 12)
        return r

    @staticmethod
    def _pill(p: QPainter, right: float, cy: float, text: str, filled: bool = False) -> float:
        f = theme.font(11, QFont.DemiBold)
        w, h = QFontMetrics(f).horizontalAdvance(text) + 20, 22
        r = QRectF(right - w, cy - h / 2, w, h)
        p.setPen(Qt.NoPen if filled else QPen(QColor(theme.HAIRLINE), 1))
        p.setBrush(QColor(theme.RAUSCH if filled else theme.CANVAS))
        p.drawRoundedRect(r, h / 2, h / 2)
        p.setFont(f)
        p.setPen(QColor(theme.CANVAS if filled else theme.INK))
        p.drawText(r, Qt.AlignCenter, text)
        return r.left()

    @staticmethod
    def _texts(p: QPainter, left: float, right: float, top: float, title: str, caption: str, ink: str,
               title_font: QFont | None = None, caption_color: str = theme.MUTED) -> None:
        width = int(right - left)
        for text, f, color, y in ((title, title_font or theme.font(16, QFont.DemiBold), ink, top + 12),
                                  (caption, theme.font(13), caption_color, top + 35)):
            p.setFont(f)
            p.setPen(QColor(color))
            p.drawText(QRectF(left, y, width, 20), Qt.AlignLeft | Qt.AlignVCenter,
                       QFontMetrics(f).elidedText(text, Qt.ElideRight, width))


class ProfileDelegate(_RowDelegate):
    """Active profile = elevated card with a Rausch border, plus the pointing hand in a gutter on its right."""
    HEIGHT = 76
    POINTER = 28  # hand width in px
    GUTTER = POINTER + 6  # reserved on every row so the hand never covers text and rows stay aligned

    def paint(self, p, option, index):
        p.save()
        p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        active = bool(index.data(ROLE_ACTIVE))
        card = QRectF(option.rect).adjusted(4, 5, -self.GUTTER, -7)
        if active:
            self._shadow(p, card)
            p.setPen(QPen(QColor(theme.RAUSCH), 2))
            p.setBrush(QColor(theme.RAUSCH_TINT))
            p.drawRoundedRect(card.adjusted(1, 1, -1, -1), 14, 14)
            self._pointer(p, card)
        elif option.state & (QStyle.State_Selected | QStyle.State_MouseOver):
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(theme.SURFACE_STRONG if option.state & QStyle.State_Selected else theme.SURFACE_SOFT))
            p.drawRoundedRect(card, 14, 14)
        if option.state & QStyle.State_HasFocus:  # keyboard focus ring, inside the Rausch border when active
            p.setPen(QPen(QColor(theme.INK), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(card.adjusted(4, 4, -4, -4) if active else card.adjusted(1, 1, -1, -1), 11, 11)

        right, cy = card.right() - 14, card.center().y()
        if active:
            right = self._pill(p, right, cy, "Active", filled=True) - 6
        if index.data(ROLE_DEFAULT):
            right = self._pill(p, right, cy, "Default") - 6
        # inactive rows stay legible (body/muted pass 4.5:1) but recede next to the bold active card
        self._texts(p, card.left() + 16, right - 8, card.top() + 1, index.data(Qt.DisplayRole), index.data(ROLE_CAPTION),
                    theme.INK if active else theme.BODY,
                    title_font=theme.font(17, QFont.Bold) if active else theme.font(16, QFont.Medium),
                    caption_color=theme.BODY if active else theme.MUTED)
        p.restore()

    @staticmethod
    def _shadow(p: QPainter, card: QRectF) -> None:
        # stacked translucent layers approximate the spec's single elevation tier (0 2px 6px / 0 4px 8px)
        p.setPen(Qt.NoPen)
        for spread, alpha in ((6, 6), (4, 10), (2, 16)):
            p.setBrush(QColor(0, 0, 0, alpha))
            p.drawRoundedRect(card.translated(0, 2).adjusted(-spread / 2, -spread / 4, spread / 2, spread / 2),
                              14 + spread / 2, 14 + spread / 2)

    def _pointer(self, p: QPainter, card: QRectF) -> None:
        pm = theme.pointer(self.POINTER, p.device().devicePixelRatioF())
        if pm.isNull():  # asset missing: fall back to a Rausch dot
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(theme.RAUSCH))
            p.drawEllipse(QPointF(card.right() + self.GUTTER / 2, card.center().y()), 5, 5)
            return
        h = pm.height() / pm.devicePixelRatio()
        p.drawPixmap(QPointF(card.right() + 3, card.center().y() - h / 2), pm)  # fingertip touches the card edge


class LanguageDelegate(_RowDelegate):
    @staticmethod
    def _box(rect: QRect) -> QRectF:
        return QRectF(rect.left() + 18, rect.center().y() - 10, 20, 20)

    def paint(self, p, option, index):
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        r = self._background(p, option)
        on = _checked(index)
        box = self._box(option.rect)
        if on:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(theme.INK))
            p.drawRoundedRect(box, 5, 5)
            p.setPen(QPen(QColor(theme.CANVAS), 2.2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            x, y = box.left(), box.top()
            p.drawPolyline([QPointF(x + 5, y + 10.5), QPointF(x + 8.5, y + 14), QPointF(x + 15, y + 6.5)])
        else:
            p.setPen(QPen(QColor(theme.MUTED), 1.5))
            p.setBrush(QColor(theme.CANVAS))
            p.drawRoundedRect(box.adjusted(0.75, 0.75, -0.75, -0.75), 5, 5)

        # drag grip, far right
        right, cy = r.right() - 16, r.center().y()
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(theme.MUTED_SOFT))
        for dx in (0, 6):
            for dy in (-6, 0, 6):
                p.drawEllipse(QPointF(right - dx, cy + dy), 1.6, 1.6)
        right -= 22
        if on and self._first_checked(index):
            right = self._pill(p, right, cy, "Display language") - 8
        self._texts(p, box.right() + 16, right, r.top(), index.data(Qt.DisplayRole), index.data(ROLE_CAPTION),
                    theme.INK if on else theme.MUTED)
        p.restore()

    @staticmethod
    def _first_checked(index) -> bool:
        m = index.model()
        return not any(_checked(m.index(row, 0)) for row in range(index.row()))

    def editorEvent(self, event, model, option, index):
        hit = (event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton
               and self._box(option.rect).adjusted(-10, -10, 10, 10).contains(event.position()))
        key = event.type() == QEvent.KeyPress and event.key() in (Qt.Key_Space, Qt.Key_Select)
        if hit or key:
            model.setData(index, Qt.Unchecked if _checked(index) else Qt.Checked, Qt.CheckStateRole)
            return True
        return False


class SettingsWindow(QWidget):
    def __init__(self, ctrl: Controller):
        super().__init__()
        self.ctrl = ctrl
        self.selected_id: str | None = None
        self._filled_for: str | None = None
        self._loading = False
        self.setObjectName("Root")
        self.setWindowTitle("Language Profiles")
        self.setWindowIcon(theme.app_icon())
        self.resize(1000, 720)
        self.setMinimumSize(840, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(24)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(4)
        titles.addWidget(_label("Language profiles", "h1"))
        self.subtitle = _label("", "caption", wrap=True)
        titles.addWidget(self.subtitle)
        header.addLayout(titles, 1)
        self.status = _label("", "status")
        self.status.setTextFormat(Qt.RichText)
        header.addWidget(self.status, 0, Qt.AlignTop)
        root.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(28)
        root.addLayout(body, 1)

        # left column: profiles + hotkey
        left = QVBoxLayout()
        left.setSpacing(12)
        left.addWidget(_label("Profiles", "h2"))
        self.profile_list = QListWidget()
        self.profile_list.setItemDelegate(ProfileDelegate(self.profile_list))
        self.profile_list.setMouseTracking(True)
        self.profile_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.profile_list.setAccessibleName("Profiles")
        self.profile_list.currentItemChanged.connect(self._profile_selected)
        left.addWidget(self.profile_list, 1)
        left.addWidget(_button("New profile", "secondary", self._new_profile))
        left.addSpacing(16)
        left.addWidget(_label("Toggle hotkey", "h2"))
        self.hotkey_edit = QKeySequenceEdit()
        self.hotkey_edit.setMaximumSequenceLength(1)
        self.hotkey_edit.setClearButtonEnabled(True)
        self.hotkey_edit.setAccessibleName("Toggle hotkey")
        self.hotkey_edit.editingFinished.connect(self._hotkey_edited)
        self.hotkey_edit.keySequenceChanged.connect(lambda s: s.isEmpty() and self._hotkey_edited())
        # the registered hotkey would swallow the keystroke while the user records a new one
        self.hotkey_edit.findChild(QLineEdit).installEventFilter(self)
        left.addWidget(self.hotkey_edit)
        self.hotkey_note = _label("", "caption", wrap=True)
        left.addWidget(self.hotkey_note)
        left_w = QWidget()
        left_w.setLayout(left)
        left_w.setFixedWidth(330)
        left.setContentsMargins(0, 0, 0, 0)
        body.addWidget(left_w)

        divider = QFrame()
        divider.setObjectName("Divider")
        divider.setFixedWidth(1)
        body.addWidget(divider)

        # right column: selected profile
        right = QVBoxLayout()
        right.setSpacing(12)
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        self.title = _label("", "h1")
        self.default_pill = _label("Default", "pill")
        title_row.addWidget(self.title)
        title_row.addWidget(self.default_pill, 0, Qt.AlignVCenter)
        title_row.addStretch()
        self.make_default_btn = _button("Make default", "text", self._make_default)
        self.rename_btn = _button("Rename", "text", self._rename)
        self.delete_btn = _button("Delete", "text", self._delete)
        for b in (self.make_default_btn, self.rename_btn, self.delete_btn):
            title_row.addWidget(b)
        right.addLayout(title_row)

        lang_head = QHBoxLayout()
        lang_head.setSpacing(8)
        col = QVBoxLayout()
        col.setSpacing(4)
        col.addWidget(_label("Languages", "h2"))
        col.addWidget(_label("Tick the languages this profile cycles through. Drag to reorder: the first one is "
                             "the Windows display language.", "caption", wrap=True))
        lang_head.addLayout(col, 1)
        lang_head.addWidget(_button("Add language", "secondary", self._add_language), 0, Qt.AlignBottom)
        lang_head.addWidget(_button("Rescan", "secondary", self.ctrl.rescan), 0, Qt.AlignBottom)
        right.addLayout(lang_head)

        self.lang_list = QListWidget()
        self.lang_list.setItemDelegate(LanguageDelegate(self.lang_list))
        self.lang_list.setMouseTracking(True)
        self.lang_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lang_list.setAccessibleName("Languages in this profile")
        self.lang_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.lang_list.setDefaultDropAction(Qt.MoveAction)
        self.lang_list.itemChanged.connect(self._languages_edited)
        self.lang_list.model().rowsMoved.connect(self._languages_edited)
        right.addWidget(self.lang_list, 1)

        move_row = QHBoxLayout()
        move_row.setSpacing(4)
        for text, delta in (("Move up", -1), ("Move down", 1), ("Move to top", None)):
            move_row.addWidget(_button(text, "text", lambda d=delta: self._move(d)))
        move_row.addStretch()
        self.note = _label("", "caption")
        move_row.addWidget(self.note)
        right.addLayout(move_row)

        self.banner = QFrame()
        self.banner.setObjectName("Banner")
        bl = QHBoxLayout(self.banner)
        bl.setContentsMargins(20, 14, 16, 14)
        bl.setSpacing(16)
        self.banner_text = _label("", "banner", wrap=True)
        self.banner_text.setTextFormat(Qt.RichText)
        bl.addWidget(self.banner_text, 1)
        self.banner_fix = _button("", "secondary", self._fix_display_language)
        bl.addWidget(self.banner_fix)
        right.addWidget(self.banner)

        footer = QHBoxLayout()
        footer.addStretch()
        self.apply_btn = _button("Switch to this profile", "primary", self._apply)
        footer.addWidget(self.apply_btn)
        right.addLayout(footer)
        body.addLayout(right, 1)

    # ---- state -> widgets -------------------------------------------------------------
    def _profile(self):
        return self.ctrl.cfg.profile(self.selected_id)

    def reload(self) -> None:
        cfg, ctrl = self.ctrl.cfg, self.ctrl
        if not cfg.profile(self.selected_id):
            self.selected_id = ctrl.matched or cfg.default_id or cfg.profiles[0].id
        self._loading = True
        self.profile_list.clear()
        for p in cfg.profiles:
            it = QListWidgetItem(p.name)
            n = len(p.tags)
            it.setData(ROLE_ID, p.id)
            it.setData(ROLE_CAPTION, f"{n} language{'s' * (n != 1)} · " + ", ".join(t.split('-')[0].upper() for t in p.tags))
            it.setData(ROLE_DEFAULT, p.id == cfg.default_id)
            it.setData(ROLE_ACTIVE, p.id == ctrl.matched)
            it.setData(Qt.AccessibleTextRole, f"{p.name}, {n} languages"
                       + (", default" if p.id == cfg.default_id else "") + (", active" if p.id == ctrl.matched else ""))
            self.profile_list.addItem(it)
            if p.id == self.selected_id:
                self.profile_list.setCurrentItem(it)
        self._fill_languages()
        self._loading = False
        self._update_details()

    def _fill_languages(self) -> None:
        p, cfg = self._profile(), self.ctrl.cfg
        keep = self._filled_for == self.selected_id
        row, scroll = self.lang_list.currentRow(), self.lang_list.verticalScrollBar().value()
        self.lang_list.clear()
        others = sorted((t for t in cfg.languages if t not in p.tags), key=winlang.language_name)
        for tag in p.tags + others:
            it = QListWidgetItem(winlang.language_name(tag))
            it.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            it.setCheckState(Qt.Checked if tag in p.tags else Qt.Unchecked)
            keyboards = ", ".join(winlang.keyboard_name(t) for t in cfg.languages.get(tag, [])) or "Windows default keyboard"
            it.setData(ROLE_ID, tag)
            it.setData(ROLE_CAPTION, " · ".join(x for x in (winlang.native_name(tag), tag, keyboards) if x))
            self.lang_list.addItem(it)
        if keep:
            self.lang_list.setCurrentRow(row)
            self.lang_list.verticalScrollBar().setValue(scroll)
        self._filled_for = self.selected_id

    def _update_details(self) -> None:
        p, cfg, ctrl = self._profile(), self.ctrl.cfg, self.ctrl
        is_default = p.id == cfg.default_id
        self.title.setText(p.name)
        self.default_pill.setVisible(is_default)
        self.make_default_btn.setVisible(not is_default)
        can_delete = not is_default and len(cfg.profiles) > 1
        self.delete_btn.setEnabled(can_delete)
        self.delete_btn.setToolTip("" if can_delete else "The default profile can't be deleted.")

        disp = ctrl.display_tag
        warn = bool(disp) and p.tags[0].casefold() != disp.casefold()
        self.banner.setVisible(warn)
        if warn:
            first, want = winlang.language_name(p.tags[0]), winlang.language_name(disp)
            self.banner_text.setText(
                f"<b>Windows display language may change.</b><br>This profile starts with {first}, but your default "
                f"starts with {want}. Windows shows menus in the first language after you next sign in.")
            self.banner_fix.setText(f"Put {want} first")

        if ctrl.busy:
            text, enabled = "Switching…", False
        elif ctrl.matched == p.id:
            text, enabled = "Active now", False
        else:
            text, enabled = "Switch to this profile", True
        self.apply_btn.setText(text)
        self.apply_btn.setEnabled(enabled)

        active = cfg.profile(ctrl.matched)
        dot = f'<span style="color:{theme.RAUSCH}">●</span>'
        self.status.setText("Switching…" if ctrl.busy else f"{dot} Active: {active.name}" if active
                            else "Custom list (not a saved profile)")
        how = f"{cfg.hotkey} or a left click on the tray icon" if cfg.hotkey else "A left click on the tray icon"
        self.subtitle.setText(f"Choose which input languages Windows cycles through. No sign-out needed. "
                              f"{how} toggles your last two profiles.")
        if self.hotkey_note.property("role") != "error":
            self.hotkey_note.setText("Toggles your last two profiles from any app.")
        if not self.hotkey_edit.hasFocus():
            self.hotkey_edit.setKeySequence(QKeySequence(cfg.hotkey, QKeySequence.PortableText))

    def _set_note(self, label: QLabel, text: str, error: bool = False) -> None:
        repolish(label, "role", "error" if error else "caption")
        label.setText(text)

    # ---- user actions -----------------------------------------------------------------
    def _profile_selected(self, current, _previous) -> None:
        if self._loading or not current:
            return
        self.selected_id = current.data(ROLE_ID)
        self._set_note(self.note, "")
        self._loading = True
        self._fill_languages()
        self._loading = False
        self._update_details()

    def _languages_edited(self, *_) -> None:
        if self._loading:
            return
        p = self._profile()
        tags = [self.lang_list.item(i).data(ROLE_ID) for i in range(self.lang_list.count())
                if _checked(self.lang_list.model().index(i, 0))]
        if not tags:
            self._set_note(self.note, "A profile needs at least one language.", error=True)
        else:
            self._set_note(self.note, "")
            if tags != p.tags:
                p.tags = tags
                self.ctrl.changed()
        QTimer.singleShot(0, self.reload)  # never rebuild a list from inside its own signal

    def _move(self, delta: int | None) -> None:
        row = self.lang_list.currentRow()
        if row < 0:
            self._set_note(self.note, "Select a language first.")
            return
        new = 0 if delta is None else max(0, min(self.lang_list.count() - 1, row + delta))
        if new == row:
            return
        self._loading = True
        self.lang_list.insertItem(new, self.lang_list.takeItem(row))
        self.lang_list.setCurrentRow(new)
        self._loading = False
        self._languages_edited()

    def _fix_display_language(self) -> None:
        p, disp = self._profile(), self.ctrl.display_tag
        p.tags = [disp] + [t for t in p.tags if t.casefold() != disp.casefold()]
        self.ctrl.changed()
        self.reload()

    def _ask_name(self, title: str, current: str = "") -> str | None:
        name, ok = QInputDialog.getText(self, title, "Profile name", QLineEdit.Normal, current)
        name = name.strip()
        if not ok or not name or name == current:
            return None
        if any(q.name.casefold() == name.casefold() for q in self.ctrl.cfg.profiles):
            QMessageBox.information(self, title, f"A profile named “{name}” already exists.")
            return None
        return name

    def _new_profile(self) -> None:
        name = self._ask_name("New profile")
        if name:
            cfg = self.ctrl.cfg
            base = cfg.default.tags if cfg.default else [t for t, _ in self.ctrl.current]
            self.selected_id = cfg.add_profile(name, base).id
            self.ctrl.changed()
            self.reload()

    def _rename(self) -> None:
        p = self._profile()
        name = self._ask_name("Rename profile", p.name)
        if name:
            p.name = name
            self.ctrl.changed()
            self.reload()

    def _delete(self) -> None:
        p = self._profile()
        if QMessageBox.question(self, "Delete profile",
                                f"Delete “{p.name}”? The languages stay installed in Windows.") != QMessageBox.Yes:
            return
        self.ctrl.cfg.remove_profile(p.id)
        self.selected_id = None
        self.ctrl.changed()
        self.reload()

    def _make_default(self) -> None:
        self.ctrl.cfg.default_id = self.selected_id
        self.ctrl.changed()
        self.reload()

    def _add_language(self) -> None:
        QDesktopServices.openUrl(QUrl("ms-settings:regionlanguage"))
        self._set_note(self.note, "Add the language in Windows Settings; it appears here when you come back.")

    def _apply(self) -> None:
        self.ctrl.switch(self.selected_id)

    def _hotkey_edited(self) -> None:
        text = self.hotkey_edit.keySequence().toString(QKeySequence.PortableText)
        if text == self.ctrl.cfg.hotkey:
            return
        err = self.ctrl.set_hotkey(text)
        if err:
            self._set_note(self.hotkey_note, err, error=True)
            self.hotkey_edit.setKeySequence(QKeySequence(self.ctrl.cfg.hotkey, QKeySequence.PortableText))
        else:
            self._set_note(self.hotkey_note, "Saved." if text else "Hotkey off. The tray icon still toggles.")
            self._update_details()

    # ---- Qt events --------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.ctrl.hotkey.clear()
        elif event.type() == QEvent.FocusOut:
            self.ctrl.hotkey.set(self.ctrl.cfg.hotkey)
        return False

    def changeEvent(self, event):
        # pick up languages added in Windows Settings when the user comes back
        if event.type() == QEvent.ActivationChange and self.isActiveWindow() and self.ctrl.refresh():
            self.reload()
        super().changeEvent(event)

    def closeEvent(self, event):
        event.ignore()  # closing the window keeps the tray app running; Exit lives in the tray menu
        self.hide()
        self.ctrl.window_hidden()
