# Changelog

## 1.0.0 (2026-10-23)

First public release.

- Tray app that swaps the Windows input-language list between named profiles, with no reboot or sign-out.
- Left-click the tray icon, or press **Ctrl+Alt+L** (configurable), to toggle between your last two profiles.
- Each language keeps its own keyboards and IMEs (Microsoft Pinyin, Microsoft IME, Thai Kedmanee and others).
- Active profile at a glance: raised Rausch-bordered card, *Active* badge and a pointing-hand marker.
- Display-language protection: a warning and a one-click fix when a profile would change the Windows UI language.
- Safe exit: offers to revert to the default profile before quitting.
- First launch builds a **Full** profile from that PC's own languages; nothing is bundled.
- Per-user installer (no admin) with Desktop, Start Menu and optional startup shortcuts.
