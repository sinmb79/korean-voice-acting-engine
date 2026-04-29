import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.acting.presets import PRESETS
from kva_engine.acting.vocal_tract import VOCAL_TRACT_PRESETS
from kva_engine.cli import main
from kva_engine.platform_delivery import build_platform_delivery_suite_report, write_platform_delivery_suite
from kva_engine.product_quality import USE_CASE_THRESHOLDS
from kva_engine.synthesis.voice_polish import POLISH_PRESETS


class PlatformDeliveryTests(unittest.TestCase):
    def test_platform_delivery_suite_includes_core_platforms(self):
        report = build_platform_delivery_suite_report()
        platforms = {profile["platform"] for profile in report["profiles"]}
        roles = {profile["role"] for profile in report["profiles"]}

        self.assertIn("youtube_shorts", platforms)
        self.assertIn("short_drama", platforms)
        self.assertIn("podcast", platforms)
        self.assertIn("public_announcement", platforms)
        self.assertIn("news_anchor", roles)
        self.assertIn("documentary", roles)
        self.assertIn("calm_narrator", roles)
        self.assertIn("drama_wife_lead", roles)
        self.assertIn("drama_husband_tense", roles)

    def test_every_platform_profile_references_supported_engine_settings(self):
        report = build_platform_delivery_suite_report()

        for profile in report["profiles"]:
            self.assertIn(profile["role"], PRESETS)
            self.assertIn(profile["role"], VOCAL_TRACT_PRESETS)
            self.assertIn(profile["quality_use_case"], USE_CASE_THRESHOLDS)
            self.assertIn(profile["polish_preset"], POLISH_PRESETS)

    def test_write_platform_delivery_suite_creates_prompt_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = write_platform_delivery_suite(temp_dir)
            root = Path(temp_dir)
            report = json.loads((root / "platform_delivery_suite.json").read_text(encoding="utf-8"))
            markdown_exists = (root / "platform_delivery_suite.md").exists()
            prompt_exists = (root / "prompts" / "youtube_shorts_hook.txt").exists()

        self.assertTrue(result["ok"])
        self.assertEqual(result["profile_count"], len(report["profiles"]))
        self.assertTrue(markdown_exists)
        self.assertTrue(prompt_exists)

    def test_platform_suite_cli_writes_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["platform-suite", "--out-dir", temp_dir, "--compact"])
            payload = json.loads((Path(temp_dir) / "platform_delivery_suite.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertGreaterEqual(len(payload["profiles"]), 6)


if __name__ == "__main__":
    unittest.main()
