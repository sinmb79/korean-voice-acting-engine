import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.public_voices import get_public_voice, list_public_voices, public_voice_profile
from kva_engine.voice_profile import load_voice_profile


class PublicVoicesTests(unittest.TestCase):
    def test_public_catalog_entries_include_required_safety_metadata(self):
        voices = list_public_voices()

        self.assertGreaterEqual(len(voices), 4)
        for voice in voices:
            self.assertIn("source_url", voice)
            self.assertIn("license", voice)
            self.assertIn("ai_voice_disclosure", voice)
            self.assertIn("attribution", voice)
            self.assertFalse(voice["commercial_use_allowed"])

    def test_get_public_voice_profile(self):
        profile = public_voice_profile("mms-tts-kor")

        self.assertEqual(profile["id"], "public:mms-tts-kor")
        self.assertEqual(profile["privacy"], "public-ai-voice")
        self.assertIn("AI-generated", profile["ai_voice_disclosure"])

    def test_load_voice_profile_accepts_public_prefix(self):
        profile = load_voice_profile("public:neurlang-piper-kss-korean")

        self.assertEqual(profile["id"], "public:neurlang-piper-kss-korean")
        self.assertEqual(profile["engine_hint"], "piper_onnx")

    def test_public_voices_cli_writes_catalog(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "public_voices.json"
            code = main(["public-voices", "--out", str(out_path), "--compact"])
            payload = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(payload["catalog_version"], "2026-04-28")
        self.assertTrue(payload["voices"])

    def test_public_voices_cli_can_return_one_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "profile.json"
            code = main(
                [
                    "public-voices",
                    "--id",
                    "mms-tts-kor",
                    "--profile",
                    "--out",
                    str(out_path),
                    "--compact",
                ]
            )
            payload = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(payload["voice_profile"]["id"], "public:mms-tts-kor")

    def test_manual_review_entries_are_hidden_by_default(self):
        default_ids = {voice["id"] for voice in list_public_voices()}
        experimental_ids = {voice["id"] for voice in list_public_voices(include_experimental=True)}

        self.assertNotIn("skytinstone-tacotron-minseok", default_ids)
        self.assertIn("skytinstone-tacotron-minseok", experimental_ids)

    def test_unknown_public_voice_raises_key_error(self):
        with self.assertRaises(KeyError):
            get_public_voice("missing-voice")


if __name__ == "__main__":
    unittest.main()
