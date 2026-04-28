import contextlib
import io
import json
import unittest

from kva_engine.benchmarks.pro_voice_products import (
    build_professional_benchmark_report,
    build_voice_conversion_benchmark_alignment,
)
from kva_engine.cli import main


class ProfessionalBenchmarkTests(unittest.TestCase):
    def test_benchmark_report_contains_actor_theory_and_products(self):
        report = build_professional_benchmark_report()

        self.assertEqual(report["schema_version"], "kva.professional_voice_benchmark.v1")
        self.assertIn("actor-capable", report["summary"]["principle"])
        self.assertGreaterEqual(report["summary"]["product_count"], 6)
        self.assertGreaterEqual(report["summary"]["bioacoustic_reference_count"], 2)
        self.assertGreaterEqual(report["summary"]["voice_acting_reference_count"], 4)
        self.assertGreaterEqual(report["summary"]["voice_acting_technique_count"], 8)
        self.assertGreaterEqual(report["summary"]["studio_sound_design_reference_count"], 6)
        self.assertGreaterEqual(report["summary"]["studio_sound_design_technique_count"], 7)
        self.assertTrue(any(product["id"] == "vocaltractlab" for product in report["products"]))
        self.assertTrue(
            any(reference["id"] == "jurassic_world_bird_calls" for reference in report["studio_sound_design_references"])
        )
        self.assertIn("creator_sound_design_mission", report)
        self.assertIn("voice_acting_techniques", report)
        self.assertIn("studio_sound_design_techniques", report)
        self.assertIn("bioacoustic_references", report)
        self.assertIn("identity anchoring", " ".join(report["actor_theory"]["program_model"]))

    def test_voice_conversion_alignment_tracks_adopted_benchmark_features(self):
        alignment = build_voice_conversion_benchmark_alignment()

        self.assertIn("source_filter_anatomy_controls", alignment["adopted"])
        self.assertIn("voice_acting_technique_catalog", alignment["adopted"])
        self.assertIn("nonhuman_bioacoustic_conversion_without_audible_source_identity", alignment["adopted"])
        self.assertIn("studio_sound_design_technique_catalog", alignment["adopted"])
        self.assertIn("source_library_schema_cli", alignment["adopted"])
        self.assertIn("source_library_scan_validation_cli", alignment["adopted"])
        self.assertIn("creature_design_recipe_cli", alignment["adopted"])
        self.assertIn("creature_design_dinosaur_render_entrypoint", alignment["adopted"])
        self.assertIn("OpenVoice", alignment["inspired_by"])
        self.assertIn("neural speech-to-speech backend", alignment["remaining"])
        self.assertIn("multi-creature sound-design render CLI", alignment["remaining"])

    def test_benchmarks_cli_outputs_report(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["benchmarks", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "kva.professional_voice_benchmark.v1")
        self.assertIn("actor_theory", payload)


if __name__ == "__main__":
    unittest.main()
