import contextlib
import io
import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.sound_design import (
    build_creature_design_recipe,
    build_source_library_report,
    render_creature_design_audio,
    scan_source_library_directory,
    validate_source_library_file,
)


class SoundDesignWorkflowTests(unittest.TestCase):
    def test_source_library_report_defines_provenance_and_privacy(self):
        report = build_source_library_report()

        self.assertEqual(report["schema_version"], "kva.source_library.v1")
        self.assertIn("source_id", report["source_library_schema"]["required_fields"])
        self.assertIn("ai_or_synthetic_disclosure", report["source_library_schema"]["required_fields"])
        self.assertIn("local_private", report["source_library_schema"]["privacy_levels"])
        self.assertTrue(any(category["id"] == "foley_body" for category in report["source_categories"]))
        self.assertIn("jurassic_world_bird_calls", report["studio_reference_ids"])

    def test_dinosaur_recipe_removes_human_speech_identity(self):
        recipe = build_creature_design_recipe("dinosaur_giant_roar", intensity=1.4)

        self.assertEqual(recipe["schema_version"], "kva.creator_sound_design.recipe.v1")
        self.assertFalse(recipe["source_voice_identity_retained"])
        self.assertFalse(recipe["source_speech_audible"])
        self.assertEqual(recipe["performance_policy"]["recommended_engine"], "kva-bioacoustic-dinosaur-v3")
        self.assertTrue(any(layer["slot"] == "body_rumble" for layer in recipe["layer_chain"]))
        self.assertTrue(any(layer["slot"] == "closed_mouth_boom" for layer in recipe["layer_chain"]))
        self.assertIn("source_provenance_complete=true", recipe["review_targets"])
        self.assertIn("source_speech_audible=false", recipe["review_targets"])
        self.assertIn("studio_sound_design", recipe["technique_catalog"])

    def test_creature_design_cli_outputs_recipe(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["creature-design", "--role", "dinosaur_giant_roar", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["role"], "dinosaur_giant_roar")
        self.assertFalse(payload["source_speech_audible"])

    def test_source_library_cli_outputs_schema(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["source-library", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "kva.source_library.v1")

    def test_source_library_scan_and_validate_local_audio(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            _write_test_wav(root / "foley_step.wav")
            scan = scan_source_library_directory(root)
            registry = root / "registry.json"
            registry.write_text(json.dumps({"entries": scan["entries"]}), encoding="utf-8")
            validation = validate_source_library_file(registry)

        self.assertEqual(scan["schema_version"], "kva.source_library.scan.v1")
        self.assertEqual(scan["entry_count"], 1)
        self.assertTrue(scan["validation"]["ok"])
        self.assertTrue(validation["ok"])
        self.assertEqual(scan["entries"][0]["source_type"], "foley_body")

    def test_creature_design_render_uses_bioacoustic_dinosaur_engine(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "controller.wav"
            output = root / "dinosaur.wav"
            _write_test_wav(source)
            result = render_creature_design_audio(source, output, role="dinosaur_giant_roar")

        self.assertTrue(result["ok"])
        self.assertEqual(result["render"]["engine"], "kva-bioacoustic-dinosaur-v3")
        self.assertFalse(result["recipe"]["source_speech_audible"])

    def test_creature_design_cli_render_outputs_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "controller.wav"
            output = root / "dinosaur.wav"
            _write_test_wav(source)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "creature-design",
                        "--role",
                        "dinosaur_giant_roar",
                        "--input",
                        str(source),
                        "--render-out",
                        str(output),
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())
            self.assertEqual(code, 0)
            self.assertTrue(payload["ok"])
            self.assertTrue(output.exists())


def _write_test_wav(path: Path, *, sample_rate: int = 48000, duration_sec: float = 0.2) -> None:
    frames = []
    for index in range(int(sample_rate * duration_sec)):
        t = index / sample_rate
        envelope = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 3.0 * t))
        sample = math.sin(2.0 * math.pi * 220.0 * t) * envelope * 0.45
        frames.append(int(sample * 32767).to_bytes(2, "little", signed=True))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
