import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.synthesis.conversion import build_voice_conversion_plan


class VoiceConversionTests(unittest.TestCase):
    def test_build_voice_conversion_plan_records_role_controls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")

            plan = build_voice_conversion_plan(
                input_path=source,
                output_path=root / "wolf.wav",
                role="wolf_growl",
            )

        self.assertEqual(plan.engine, "kva-convert-ffmpeg-v1")
        self.assertEqual(plan.role, "wolf_growl")
        self.assertTrue(plan.to_dict()["role_controls"]["pitch_shift"] < 0)
        self.assertLess(plan.to_dict()["vocal_tract_design"]["filter"]["formant_shift_ratio"], 1.0)
        self.assertEqual(plan.warnings, [])

    def test_convert_dry_run_cli_outputs_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")
            json_out = root / "plan.json"

            code = main(
                [
                    "convert",
                    "--input",
                    str(source),
                    "--role",
                    "monster_deep",
                    "--out",
                    str(root / "monster.wav"),
                    "--json-out",
                    str(json_out),
                    "--dry-run",
                ]
            )
            result = json.loads(json_out.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["conversion_plan"]["role"], "monster_deep")
        self.assertEqual(result["conversion_plan"]["input_path"], str(source))

    def test_convert_dry_run_supports_clear_and_fx_creature_roles(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "input.wav"
            source.write_bytes(b"fake wav")
            json_out = root / "plan.json"

            code = main(
                [
                    "convert",
                    "--input",
                    str(source),
                    "--role",
                    "dinosaur_giant_clear",
                    "--out",
                    str(root / "dinosaur.wav"),
                    "--json-out",
                    str(json_out),
                    "--dry-run",
                ]
            )
            result = json.loads(json_out.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(result["conversion_plan"]["role"], "dinosaur_giant_clear")
        self.assertGreater(result["conversion_plan"]["role_controls"]["articulation_strength"], 0.5)


if __name__ == "__main__":
    unittest.main()
