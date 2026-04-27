import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.workflows.voice_lab import (
    DEFAULT_VOICE_LAB_ROLES,
    parse_role_list,
    resolve_voice_lab_roles,
    roles_for_group,
    run_voice_lab_conversion,
)


class VoiceLabWorkflowTests(unittest.TestCase):
    def test_parse_role_list_uses_defaults(self):
        self.assertEqual(parse_role_list(None), list(DEFAULT_VOICE_LAB_ROLES))
        self.assertEqual(parse_role_list("wolf_growl_clear, child_bright"), ["wolf_growl_clear", "child_bright"])

    def test_role_groups_are_available(self):
        self.assertIn("monster_deep_fx", roles_for_group("creature"))
        self.assertIn("news_anchor", roles_for_group("narration"))
        self.assertEqual(resolve_voice_lab_roles(roles="child_bright", group="creature"), ["child_bright"])

    def test_voice_lab_dry_run_writes_summary_playlist_and_plans(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")
            out_dir = root / "voice-lab"

            summary = run_voice_lab_conversion(
                input_path=source,
                output_dir=out_dir,
                roles=["wolf_growl_clear", "child_bright"],
                dry_run=True,
            )

            summary_path = Path(summary["summary_path"])
            playlist_path = Path(summary["playlist_path"])
            readme_path = Path(summary["readme_path"])
            first_result = out_dir / "wolf_growl_clear.result.json"
            payload = json.loads(first_result.read_text(encoding="utf-8"))

            self.assertTrue(summary["ok"])
            self.assertTrue(summary_path.exists())
            self.assertTrue(playlist_path.exists())
            self.assertTrue(readme_path.exists())
            self.assertTrue(payload["dry_run"])
            self.assertEqual(len(summary["samples"]), 2)

    def test_voice_lab_cli_dry_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")
            out_dir = root / "voice-lab"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "voice-lab",
                        "--input",
                        str(source),
                        "--out-dir",
                        str(out_dir),
                        "--roles",
                        "monster_deep_clear",
                        "--dry-run",
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertTrue(payload["dry_run"])
            self.assertEqual(payload["roles"], ["monster_deep_clear"])
            self.assertTrue((out_dir / "monster_deep_clear.result.json").exists())

    def test_voice_lab_cli_group_dry_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")
            out_dir = root / "voice-lab"
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "voice-lab",
                        "--input",
                        str(source),
                        "--out-dir",
                        str(out_dir),
                        "--group",
                        "creature",
                        "--dry-run",
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertIn("dinosaur_giant_roar", payload["roles"])
            self.assertTrue((out_dir / "dinosaur_giant_roar.result.json").exists())


if __name__ == "__main__":
    unittest.main()
