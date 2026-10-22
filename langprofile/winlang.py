"""Windows input-language list: read from the registry (instant), write via Set-WinUserLanguageList (supported path)."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import winreg

from PySide6.QtCore import QLocale

PROFILE_KEY = r"Control Panel\International\User Profile"
POWERSHELL = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), r"System32\WindowsPowerShell\v1.0\powershell.exe")

# Payload arrives through an env var, so no user data is ever spliced into script text.
APPLY_SCRIPT = r"""
$ErrorActionPreference = 'Stop'; $ProgressPreference = 'SilentlyContinue'
try {
    $entries = @($env:LPS_PAYLOAD | ConvertFrom-Json | ForEach-Object { $_ })
    $list = New-WinUserLanguageList $entries[0].tag
    for ($i = 1; $i -lt $entries.Count; $i++) { $list.Add($entries[$i].tag) }
    for ($i = 0; $i -lt $entries.Count; $i++) {
        $tips = @($entries[$i].tips)
        if ($tips.Count) { $list[$i].InputMethodTips.Clear(); foreach ($t in $tips) { $list[$i].InputMethodTips.Add($t) } }
    }
    Set-WinUserLanguageList $list -Force -WarningAction SilentlyContinue
} catch { [Console]::Out.Write($_.Exception.Message); exit 1 }
"""

INSTALLED_SCRIPT = r"""
$ProgressPreference = 'SilentlyContinue'
try { (Get-InstalledLanguage).LanguageId -join "`n" } catch { }
"""


class ApplyError(RuntimeError):
    pass


def read_current() -> list[tuple[str, list[str]]]:
    """[(tag, [input-method tips in order])] exactly as Get-WinUserLanguageList would report."""
    out = []
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PROFILE_KEY) as root:
        tags, _ = winreg.QueryValueEx(root, "Languages")
        for tag in tags:
            tips = []
            try:
                with winreg.OpenKey(root, tag) as sub:
                    for i in range(winreg.QueryInfoKey(sub)[1]):
                        name, value, _ = winreg.EnumValue(sub, i)
                        if ":" in name and isinstance(value, int):
                            tips.append((value, name))
            except OSError:
                pass
            out.append((tag, [name for _, name in sorted(tips)]))
    return out


def _powershell(script: str, **env: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-EncodedCommand", base64.b64encode(script.encode("utf-16-le")).decode()],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90,
        stdin=subprocess.DEVNULL, env={**os.environ, **env},
        creationflags=subprocess.CREATE_NO_WINDOW,  # no console flash
    )


def apply_languages(entries: list[tuple[str, list[str]]]) -> list[tuple[str, list[str]]]:
    """Replace the user language list and verify Windows kept it. Blocking: call from a worker thread."""
    if not entries:
        raise ApplyError("A profile needs at least one language.")
    payload = json.dumps([{"tag": t, "tips": list(tips)} for t, tips in entries])
    try:
        r = _powershell(APPLY_SCRIPT, LPS_PAYLOAD=payload)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise ApplyError(f"Could not run PowerShell: {e}") from e
    if r.returncode != 0:
        raise ApplyError((r.stdout or r.stderr).strip() or f"PowerShell exited with code {r.returncode}")
    now = read_current()
    wanted, got = [t.casefold() for t, _ in entries], [t.casefold() for t, _ in now]
    if wanted != got:
        raise ApplyError(f"Windows kept {', '.join(t for t, _ in now)} instead of {', '.join(t for t, _ in entries)}.")
    return now


def installed_languages() -> list[str]:
    """Language packs installed on this PC (slow, ~2 s). Empty when the cmdlet is unavailable."""
    try:
        r = _powershell(INSTALLED_SCRIPT)
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in r.stdout.splitlines() if line.strip()]


def locale_key(tag: str) -> str:
    """'ja' and 'ja-JP' are the same language for de-duplication."""
    loc = QLocale(tag)
    return loc.name() if loc.language() != QLocale.Language.C else tag.casefold()


def language_name(tag: str) -> str:
    loc = QLocale(tag)
    if loc.language() == QLocale.Language.C:
        return tag
    name = QLocale.languageToString(loc.language())
    parts = tag.split("-")
    if len(parts) > 1 and (parts[-1].isupper() or parts[-1].isdigit()):  # explicit region, e.g. en-US
        name += f" ({QLocale.territoryToString(loc.territory())})"
    return name


def native_name(tag: str) -> str:
    loc = QLocale(tag)
    return loc.nativeLanguageName() if loc.language() != QLocale.Language.C else ""


def keyboard_name(tip: str) -> str:
    """'041E:0000041E' -> 'Thai Kedmanee'; '0412:{clsid}{profile}' -> 'Microsoft IME'."""
    lang, _, rest = tip.partition(":")
    if rest.startswith("{"):
        path, value = rf"SOFTWARE\Microsoft\CTF\TIP\{rest[:38]}\LanguageProfile\0x0000{lang}\{rest[38:]}", "Description"
    else:
        path, value = rf"SYSTEM\CurrentControlSet\Control\Keyboard Layouts\{rest}", "Layout Text"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as k:
            return str(winreg.QueryValueEx(k, value)[0]) or tip
    except OSError:
        return tip
