import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.training.family_registry import build_family_registry_training_manifest


class FamilyRegistryTrainingTests(unittest.TestCase):
    def test_build_manifest_without_copying_audio(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            profile_root = root / "profiles" / "father" / "demo"
            (profile_root / "references").mkdir(parents=True)
            _write_test_wav(profile_root / "references" / "voice.wav")
            (profile_root / "voxcpm" / "latest").mkdir(parents=True)
            (profile_root / "voxcpm" / "latest" / "lora_config.json").write_text(
                json.dumps({"rank": 8}),
                encoding="utf-8",
            )
            (profile_root / "voxcpm" / "latest" / "training_state.json").write_text(
                json.dumps({"step": 3}),
                encoding="utf-8",
            )
            (profile_root / "voxcpm" / "latest" / "lora_weights.safetensors").write_bytes(
                b"fake weights"
            )
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
                            "engines": ["voxcpm"],
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
                            "voxcpm_lora_path": "voxcpm/latest",
                        }
                    },
                },
            )

            manifest = build_family_registry_training_manifest(root)

        self.assertTrue(manifest["safety"]["no_audio_copy"])
        self.assertEqual(manifest["summary"]["profile_count"], 1)
        self.assertEqual(manifest["summary"]["audio_clip_count"], 1)
        language = manifest["profiles"][0]["languages"]["ko"]
        self.assertTrue(language["training_ready"])
        self.assertEqual(language["lora"]["status"], "present")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_test_wav(path: Path) -> None:
    sample_rate = 8000
    frames = []
    for index in range(sample_rate // 20):
        sample = int(12000 * math.sin(2 * math.pi * 220 * index / sample_rate))
        frames.append(struct.pack("<h", sample))
    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
