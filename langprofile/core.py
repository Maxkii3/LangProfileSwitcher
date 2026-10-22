"""Profile model, JSON persistence and the pure switching rules (no Qt, no Windows calls)."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "LangProfileSwitcher"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_HOTKEY = "Ctrl+Alt+L"


@dataclass
class Profile:
    id: str
    name: str
    tags: list[str]  # ordered BCP-47 tags; tags[0] drives the Windows display language


@dataclass
class Config:
    profiles: list[Profile] = field(default_factory=list)
    default_id: str | None = None
    active_id: str | None = None  # last profile this app applied
    previous_id: str | None = None  # the one before it (left-click / hotkey toggles between the two)
    hotkey: str = DEFAULT_HOTKEY  # "" = no global hotkey
    languages: dict[str, list[str]] = field(default_factory=dict)  # tag -> input-method tips, every language seen
    tray_hint_shown: bool = False

    def profile(self, pid: str | None) -> Profile | None:
        return next((p for p in self.profiles if p.id == pid), None)

    @property
    def default(self) -> Profile | None:
        return self.profile(self.default_id)

    def add_profile(self, name: str, tags: list[str]) -> Profile:
        p = Profile(uuid.uuid4().hex[:8], name, list(tags))
        self.profiles.append(p)
        return p

    def remove_profile(self, pid: str) -> None:
        if pid == self.default_id or len(self.profiles) <= 1:
            raise ValueError("The default profile and the last profile cannot be deleted.")
        self.profiles = [p for p in self.profiles if p.id != pid]
        if self.active_id == pid:
            self.active_id = None
        if self.previous_id == pid:
            self.previous_id = None


def same_tags(a: list[str], b: list[str]) -> bool:
    return [t.casefold() for t in a] == [t.casefold() for t in b]


def match_profile(cfg: Config, current_tags: list[str]) -> str | None:
    """Which profile the live Windows list equals (order included), preferring the last applied one."""
    candidates = sorted(cfg.profiles, key=lambda p: p.id != cfg.active_id)
    return next((p.id for p in candidates if same_tags(p.tags, current_tags)), None)


def toggle_target(cfg: Config, current_id: str | None) -> str | None:
    """Left-click / hotkey target: the previous profile, else the default, else any other profile."""
    current_id = current_id or cfg.active_id
    for pid in (cfg.previous_id, cfg.default_id):
        if pid and pid != current_id and cfg.profile(pid):
            return pid
    return next((p.id for p in cfg.profiles if p.id != current_id), None)


def record_applied(cfg: Config, pid: str) -> None:
    if pid != cfg.active_id:
        cfg.previous_id, cfg.active_id = cfg.active_id, pid


def display_tag(cfg: Config, current_tags: list[str]) -> str | None:
    """The language Windows should keep as display language: first of the default profile."""
    source = cfg.default.tags if cfg.default else current_tags
    return source[0] if source else None


def merge_languages(cfg: Config, current: list[tuple[str, list[str]]], installed: list[str] = (), key=str.casefold) -> bool:
    """Fold the live list (with its keyboards) and installed language packs into the catalog. True if it changed."""
    before = json.dumps(cfg.languages, sort_keys=True)
    for tag, tips in current:
        known = next((t for t in cfg.languages if t.casefold() == tag.casefold()), tag)
        if tips or known not in cfg.languages:
            cfg.languages[known] = list(tips)
    keys = {key(t) for t in cfg.languages}
    for tag in installed:
        if not tag.lower().startswith("und") and key(tag) not in keys:
            cfg.languages[tag] = []  # empty = Windows' default keyboard for that language
            keys.add(key(tag))
    return json.dumps(cfg.languages, sort_keys=True) != before


def seed(current: list[tuple[str, list[str]]]) -> Config:
    """First run: 'Full' = today's list (default), 'Minimal' = its first two languages."""
    cfg = Config()
    merge_languages(cfg, current)
    tags = [t for t, _ in current]
    full = cfg.add_profile("Full", tags)
    cfg.default_id = cfg.active_id = full.id
    if len(tags) >= 3:
        cfg.add_profile("Minimal", tags[:2])
    return cfg


def from_dict(d: dict) -> Config:
    profiles = [
        Profile(str(p["id"]), str(p["name"]), [str(t) for t in p["tags"]])
        for p in d.get("profiles", [])
        if isinstance(p, dict) and p.get("id") and p.get("name") and isinstance(p.get("tags"), list) and p["tags"]
    ]
    langs = d.get("languages") or {}
    cfg = Config(
        profiles=profiles,
        default_id=d.get("default_id"),
        active_id=d.get("active_id"),
        previous_id=d.get("previous_id"),
        hotkey=str(d.get("hotkey", DEFAULT_HOTKEY)),
        languages={str(k): [str(t) for t in v] for k, v in langs.items() if isinstance(v, list)},
        tray_hint_shown=bool(d.get("tray_hint_shown", False)),
    )
    if not cfg.default and cfg.profiles:
        cfg.default_id = max(cfg.profiles, key=lambda p: len(p.tags)).id
    for attr in ("active_id", "previous_id"):
        if not cfg.profile(getattr(cfg, attr)):
            setattr(cfg, attr, None)
    return cfg


def load(path: Path = CONFIG_PATH) -> Config | None:
    """None on first run. A corrupt file is moved aside (never silently overwritten)."""
    if not path.exists():
        return None
    try:
        cfg = from_dict(json.loads(path.read_text(encoding="utf-8")))
        if cfg.profiles:
            return cfg
        raise ValueError("no valid profiles")
    except (ValueError, TypeError, KeyError, AttributeError):
        path.replace(path.with_name(f"{path.name}.bad-{time.strftime('%Y%m%d-%H%M%S')}"))
        return None


def save(cfg: Config, path: Path = CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"version": 1, **asdict(cfg)}, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)  # atomic: a crash mid-write never leaves a half-written config
