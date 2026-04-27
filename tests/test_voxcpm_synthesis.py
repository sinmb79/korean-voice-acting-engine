import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.synthesis.voxcpm import build_voxcpm_synthesis_plan


class VoxCpmSynthesisTests(unittest.TestCase):
    def test_plan_resolves_relative_profile_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reference = root / "reference.wav"
            prompt = root / "prompt.txt"
            lora = root / "lora"
            reference.write_bytes(b"fake wav")
            prompt.write_text("테스트 기준 문장입니다.", encoding="utf-8")
            lora.mkdir()
            profile = root / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "id": "test-voice",
                        "reference_audio": "reference.wav",
                        "voxcpm_prompt_text_file": "prompt.txt",
                        "voxcpm_lora_path": "lora",
                        "voxcpm_python": "python-with-voxcpm",
                        "voxcpm_model_path": "local-model",
                        "cfg_weight": 2.5,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            plan = build_voxcpm_synthesis_plan(
                text="테스트입니다.",
                output_path=root / "out.wav",
                voice_profile_path=profile,
            )

        self.assertEqual(plan.reference_audio, reference)
        self.assertEqual(plan.prompt_audio, reference)
        self.assertEqual(plan.prompt_text_file, prompt)
        self.assertEqual(plan.lora_path, lora)
        self.assertEqual(plan.python_executable, "python-with-voxcpm")
        self.assertEqual(plan.model_path, "local-model")
        self.assertEqual(plan.cfg_value, 2.5)

    def test_render_dry_run_cli_outputs_resolved_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reference = root / "reference.wav"
            reference.write_bytes(b"fake wav")
            profile = root / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "id": "test-voice",
                        "reference_audio": str(reference),
                        "voxcpm_python": "python-with-voxcpm",
                        "voxcpm_model_path": "local-model",
                    }
                ),
                encoding="utf-8",
            )
            json_out = root / "dry-run.json"

            code = main(
                [
                    "render",
                    "테스트 문장입니다.",
                    "--voice-profile",
                    str(profile),
                    "--out",
                    str(root / "out.wav"),
                    "--json-out",
                    str(json_out),
                    "--dry-run",
                ]
            )
            result = json.loads(json_out.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["render_plan"]["python_executable"], "python-with-voxcpm")
        self.assertEqual(result["render_plan"]["model_path"], "local-model")
        self.assertEqual(result["render_plan"]["reference_audio"], str(reference))

    def test_creature_role_is_available_in_render_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            reference = root / "reference.wav"
            reference.write_bytes(b"fake wav")
            profile = root / "profile.json"
            profile.write_text(
                json.dumps(
                    {
                        "id": "test-voice",
                        "reference_audio": str(reference),
                        "voxcpm_python": "python-with-voxcpm",
                        "voxcpm_model_path": "local-model",
                    }
                ),
                encoding="utf-8",
            )
            json_out = root / "dry-run.json"

            code = main(
                [
                    "render",
                    "creature voice test",
                    "--role",
                    "dinosaur_giant",
                    "--voice-profile",
                    str(profile),
                    "--out",
                    str(root / "out.wav"),
                    "--json-out",
                    str(json_out),
                    "--dry-run",
                ]
            )
            result = json.loads(json_out.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(result["render_plan"]["role"], "dinosaur_giant")
        self.assertEqual(result["render_plan"]["role_controls"]["pitch_shift"], -8.0)
        self.assertLess(result["render_plan"]["role_controls"]["speed"], 0.75)


if __name__ == "__main__":
    unittest.main()
