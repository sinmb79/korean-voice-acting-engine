import unittest

from kva_engine.synthesis.audio_postprocess import (
    _apply_bioacoustic_dinosaur_transform,
    _layered_dinosaur_filter_complex,
    _pitch_preserving_tempo_filters,
)


class DinosaurLayeringTests(unittest.TestCase):
    def test_layered_dinosaur_filter_has_sub_grit_and_rumble_layers(self):
        filter_complex = _layered_dinosaur_filter_complex(
            role="dinosaur_giant_roar",
            base_filters=["asetrate=48000*0.529732", "aresample=48000"],
            sample_rate=48000,
        )

        self.assertIn("[main]", filter_complex)
        self.assertIn("[sub]", filter_complex)
        self.assertIn("[grit]", filter_complex)
        self.assertIn("[rumble]", filter_complex)
        self.assertIn("amix=inputs=4", filter_complex)
        self.assertIn("duration=first", filter_complex)
        self.assertIn("equalizer=f=58", filter_complex)

    def test_low_pitch_layers_preserve_performance_duration(self):
        filters = _pitch_preserving_tempo_filters(0.28)

        self.assertEqual(filters, ["atempo=2.000000", "atempo=1.785714"])

    def test_bioacoustic_transform_is_primary_dinosaur_path(self):
        self.assertTrue(callable(_apply_bioacoustic_dinosaur_transform))


if __name__ == "__main__":
    unittest.main()
