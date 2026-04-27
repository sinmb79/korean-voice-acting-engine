import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.voice_profile import load_voice_profile


class VoiceProfileTests(unittest.TestCase):
    def test_load_audio_profile_from_extensionless_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample-speaker-20260427.m4a"
            path.write_bytes(b"fake audio")

            profile = load_voice_profile(str(path.with_suffix("")))

        self.assertTrue(profile["exists"])
        self.assertEqual(profile["id"], "sample-speaker-20260427")
        self.assertTrue(profile["reference_audio"].endswith("sample-speaker-20260427.m4a"))

    def test_load_local_json_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio = root / "voice.m4a"
            audio.write_bytes(b"fake audio")
            config = root / "default_voice.local.json"
            config.write_text(
                json.dumps({"id": "sample-speaker-20260427", "reference_audio": str(audio)}),
                encoding="utf-8",
            )

            profile = load_voice_profile(config)

        self.assertEqual(profile["id"], "sample-speaker-20260427")
        self.assertTrue(profile["exists"])
        self.assertEqual(profile["reference_audio"], str(audio))


if __name__ == "__main__":
    unittest.main()
