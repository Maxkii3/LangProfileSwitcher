import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from langprofile import core  # noqa: E402

LIVE = [("en-US", ["0409:00000409"]), ("th", ["041E:0000041E"]), ("ko", ["0412:{A}{B}"]), ("ja", ["0411:{C}{D}"])]


class Rules(unittest.TestCase):
    def setUp(self):
        self.cfg = core.seed(LIVE)
        self.full, self.mini = self.cfg.profiles

    def test_seed(self):
        self.assertEqual(self.full.tags, ["en-US", "th", "ko", "ja"])
        self.assertEqual(self.mini.tags, ["en-US", "th"])
        self.assertEqual(self.cfg.default_id, self.full.id)
        self.assertEqual(self.cfg.languages["ko"], ["0412:{A}{B}"])

    def test_match_is_ordered_and_case_insensitive(self):
        self.assertEqual(core.match_profile(self.cfg, ["EN-us", "TH"]), self.mini.id)
        self.assertIsNone(core.match_profile(self.cfg, ["th", "en-US"]))

    def test_toggle_alternates_last_two(self):
        third = self.cfg.add_profile("Thai only", ["th"])
        self.assertEqual(core.toggle_target(self.cfg, self.full.id), self.mini.id)  # no history -> another profile
        core.record_applied(self.cfg, self.mini.id)
        core.record_applied(self.cfg, third.id)
        self.assertEqual(core.toggle_target(self.cfg, third.id), self.mini.id)
        core.record_applied(self.cfg, self.mini.id)
        self.assertEqual(core.toggle_target(self.cfg, self.mini.id), third.id)

    def test_toggle_single_profile(self):
        cfg = core.seed(LIVE[:2])
        self.assertIsNone(core.toggle_target(cfg, cfg.profiles[0].id))

    def test_remove_guards(self):
        with self.assertRaises(ValueError):
            self.cfg.remove_profile(self.full.id)
        core.record_applied(self.cfg, self.mini.id)
        self.cfg.remove_profile(self.mini.id)
        self.assertIsNone(self.cfg.active_id)

    def test_merge_keeps_tips_and_dedupes_installed(self):
        changed = core.merge_languages(self.cfg, [("th", ["041E:0001041E"])], ["ja-JP", "fr-FR", "und-Thai"],
                                       key=lambda t: t.split("-")[0].casefold())
        self.assertTrue(changed)
        self.assertEqual(self.cfg.languages["th"], ["041E:0001041E"])
        self.assertIn("fr-FR", self.cfg.languages)
        self.assertNotIn("ja-JP", self.cfg.languages)
        self.assertFalse(any(t.startswith("und") for t in self.cfg.languages))
        self.assertFalse(core.merge_languages(self.cfg, [("th", ["041E:0001041E"])]))

    def test_display_tag_from_default(self):
        self.assertEqual(core.display_tag(self.cfg, ["th"]), "en-US")


class Persistence(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "sub" / "config.json"
            cfg = core.seed(LIVE)
            core.record_applied(cfg, cfg.profiles[1].id)
            cfg.hotkey = "Ctrl+Alt+K"
            core.save(cfg, path)
            self.assertEqual(core.load(path), cfg)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["version"], 1)

    def test_corrupt_file_is_moved_aside(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "config.json"
            path.write_text("{not json", encoding="utf-8")
            self.assertIsNone(core.load(path))
            self.assertFalse(path.exists())
            self.assertEqual(len(list(Path(d).glob("config.json.bad-*"))), 1)

    def test_dangling_ids_repaired(self):
        cfg = core.from_dict({"profiles": [{"id": "a", "name": "A", "tags": ["en-US"]},
                                           {"id": "b", "name": "B", "tags": ["en-US", "th"]},
                                           {"id": "c", "name": "Broken", "tags": []}],
                              "default_id": "zzz", "active_id": "gone"})
        self.assertEqual([p.id for p in cfg.profiles], ["a", "b"])
        self.assertEqual(cfg.default_id, "b")  # largest profile becomes the fallback
        self.assertIsNone(cfg.active_id)


@unittest.skipUnless(sys.platform == "win32", "Windows only")
class Windows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtCore import QCoreApplication
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def test_hotkey_parse(self):
        from langprofile.hotkey import to_native
        self.assertEqual(to_native("Ctrl+Alt+L"), (0x2 | 0x1, 0x4C))
        self.assertEqual(to_native("Meta+F12"), (0x8, 0x7B))
        self.assertEqual(to_native("Ctrl+Shift+1"), (0x2 | 0x4, 0x31))
        self.assertIsNone(to_native("Shift+A"))
        self.assertIsNone(to_native("L"))
        self.assertIsNone(to_native("Ctrl+Alt+Left"))

    def test_registry_read_matches_powershell(self):
        from langprofile import winlang
        ps = subprocess.run(
            [winlang.POWERSHELL, "-NoProfile", "-Command",
             "(Get-WinUserLanguageList) | % { $_.LanguageTag + '=' + ($_.InputMethodTips -join ',') }"],
            capture_output=True, text=True, check=True)
        expected = [line.strip() for line in ps.stdout.splitlines() if line.strip()]
        self.assertEqual([f"{t}={','.join(tips)}" for t, tips in winlang.read_current()], expected)

    def test_names(self):
        from langprofile import winlang
        self.assertEqual(winlang.language_name("en-US"), "English (United States)")
        self.assertEqual(winlang.language_name("th"), "Thai")
        self.assertEqual(winlang.locale_key("ja"), winlang.locale_key("ja-JP"))
        self.assertEqual(winlang.keyboard_name("041E:0000041E"), "Thai Kedmanee")


if __name__ == "__main__":
    unittest.main()
