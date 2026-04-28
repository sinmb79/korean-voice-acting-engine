import contextlib
import io
import json
import unittest

from kva_engine.cli import main
from kva_engine.sound_design import build_creature_design_recipe, build_source_library_report


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


if __name__ == "__main__":
    unittest.main()
