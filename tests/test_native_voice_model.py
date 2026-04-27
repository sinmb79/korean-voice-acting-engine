import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.training.native_voice_model import train_native_voice_model


class NativeVoiceModelTests(unittest.TestCase):
    def test_train_native_voice_model_creates_kva_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile_root = root / "profiles" / "father" / "demo"
            (profile_root / "references").mkdir(parents=True)
            _write_wav(profile_root / "references" / "voice.wav")
            _write_json(
                root / "registry.json",
                {
                    "registry_version": 1,
                    "updated_at": "2026-04-27",
                    "privacy": "private-shared-only",
                    "profiles": [
                        {
                            "id": "father-demo",
                            "role": "father",
                            "profile_name": "demo",
                            "path": "profiles/father/demo",
                            "languages": ["ko"],
                            "engines": ["kva-native"],
                        }
                    ],
                },
            )
            _write_json(
                profile_root / "profile.json",
                {
                    "owner": "demo",
                    "profile_version": 1,
                    "languages": {
                        "ko": {
                            "label": "demo-ko",
                            "reference_clip": "references/voice.wav",
                        }
                    },
                },
            )

            model = train_native_voice_model(root)

        self.assertEqual(model["engine"], "kva-native")
        self.assertEqual(model["training_mode"], "statistical_voiceprint_v1")
        self.assertEqual(model["summary"]["actor_count"], 1)
        self.assertEqual(model["summary"]["audio_clip_count"], 1)
        language = model["actors"][0]["languages"]["ko"]
        self.assertIn("normalized_voiceprint", language)
        self.assertIn("calm_narrator", language["acting_role_controls"])
        self.assertIn("father", model["role_averages"])


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_wav(path: Path) -> None:
    sample_rate = 16000
    frames = []
    for index in range(sample_rate // 10):
        sample = int(10000 * math.sin(2 * math.pi * 330 * index / sample_rate))
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
