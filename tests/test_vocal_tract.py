import contextlib
import io
import json
import unittest

from kva_engine.acting.vocal_tract import build_vocal_tract_design, build_vocal_tract_filter_chain
from kva_engine.cli import main


class VocalTractDesignTests(unittest.TestCase):
    def test_child_voice_uses_shorter_tract_and_higher_formants(self):
        design = build_vocal_tract_design("child_bright")

        self.assertLess(design.filter.vocal_tract_length_scale, 1.0)
        self.assertGreater(design.filter.formant_shift_ratio, 1.0)
        self.assertGreater(design.source.pitch_ratio, 1.0)
        self.assertIn("equalizer", ",".join(design.filter_chain))

    def test_creature_voice_uses_longer_tract_and_rough_source(self):
        design = build_vocal_tract_design("dinosaur_giant_roar")

        self.assertGreater(design.filter.vocal_tract_length_scale, 1.0)
        self.assertLess(design.filter.formant_shift_ratio, 1.0)
        self.assertGreater(design.source.roughness, 0.5)
        self.assertIn("low_identity_anchor", design.warnings[0])

    def test_filter_chain_is_available_for_conversion_layer(self):
        filters = build_vocal_tract_filter_chain("monster_deep_clear")

        self.assertTrue(filters)
        self.assertTrue(any(item.startswith("highpass") for item in filters))
        self.assertTrue(any(item.startswith("lowpass") for item in filters))

    def test_vocal_tract_cli_outputs_design(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            code = main(["vocal-tract", "--role", "wolf_growl_clear", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["schema_version"], "kva.vocal_tract_voice_design.v1")
        self.assertEqual(payload["role"], "wolf_growl_clear")
        self.assertIn("source", payload)
        self.assertIn("filter_chain", payload)


if __name__ == "__main__":
    unittest.main()
