import tempfile
import unittest
from pathlib import Path

from kva_engine.review.manifest import build_generation_manifest


class ManifestTests(unittest.TestCase):
    def test_manifest_records_safety_and_missing_audio_warning(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio = Path(temp_dir) / "missing.wav"
            manifest = build_generation_manifest(audio_path=audio, role="calm_narrator")

        self.assertTrue(manifest["safety"]["ai_generated"])
        self.assertEqual(manifest["role"], "calm_narrator")
        self.assertIn("audio_missing", manifest["review"]["warnings"])


if __name__ == "__main__":
    unittest.main()
