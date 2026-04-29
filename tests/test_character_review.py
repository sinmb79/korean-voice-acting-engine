import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.review.character_review import analyze_character_features, review_character_audio


class CharacterReviewTests(unittest.TestCase):
    def test_dinosaur_review_prefers_low_nonhuman_body(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            low_roar = root / "low_roar.wav"
            speech_like = root / "speech_like.wav"
            _write_test_wav(low_roar, frequencies=(42.0, 84.0), noise=0.02)
            _write_test_wav(speech_like, frequencies=(220.0, 900.0, 2300.0), noise=0.0)

            low_review = review_character_audio(audio_path=low_roar, role="dinosaur_giant_roar")
            speech_review = review_character_audio(audio_path=speech_like, role="dinosaur_giant_roar")

        self.assertGreater(low_review["score"], speech_review["score"])
        self.assertIn("human_speech_trace_index_high", speech_review["warnings"])
        self.assertGreater(low_review["features"]["body_index"], speech_review["features"]["body_index"])

    def test_child_review_reads_brightness_and_body_features(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            child = root / "child.wav"
            _write_test_wav(child, frequencies=(420.0, 1800.0, 3600.0), noise=0.015)

            features = analyze_character_features(child)
            review = review_character_audio(audio_path=child, role="child_bright")

        self.assertTrue(features["valid"])
        self.assertGreater(features["brightness_index"], 0.25)
        self.assertIn(review["status"], {"pass", "warn"})

    def test_review_character_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio = root / "monster.wav"
            output = root / "character.json"
            _write_test_wav(audio, frequencies=(58.0, 120.0, 900.0), noise=0.03)

            code = main(
                [
                    "review-character",
                    "--audio",
                    str(audio),
                    "--role",
                    "monster_deep_fx",
                    "--out",
                    str(output),
                ]
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(payload["task"], "character_review")
        self.assertEqual(payload["role_family"], "monster")
        self.assertIn("score", payload)


def _write_test_wav(
    path: Path,
    *,
    frequencies: tuple[float, ...],
    noise: float,
    sample_rate: int = 24000,
    duration_sec: float = 0.8,
) -> None:
    frames = []
    seed = 0.137
    for index in range(int(sample_rate * duration_sec)):
        t = index / sample_rate
        envelope = 0.65 + 0.35 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 4.0 * t))
        sample = 0.0
        for order, frequency in enumerate(frequencies, start=1):
            sample += math.sin(2.0 * math.pi * frequency * t) * (0.36 / order)
        seed = math.fmod(seed * 7.123 + 0.311, 1.0)
        sample += (seed * 2.0 - 1.0) * noise
        sample *= envelope
        frames.append(int(max(min(sample, 0.94), -0.94) * 32767).to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
