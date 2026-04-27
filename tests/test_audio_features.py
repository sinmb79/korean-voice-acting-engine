import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.training.audio_features import analyze_wav


class AudioFeaturesTests(unittest.TestCase):
    def test_analyze_wav_extracts_basic_features(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "tone.wav"
            _write_test_wav(path)

            analysis = analyze_wav(path)

        self.assertTrue(analysis["exists"])
        self.assertEqual(analysis["sample_rate_hz"], 16000)
        self.assertEqual(analysis["channels"], 1)
        self.assertAlmostEqual(analysis["duration_sec"], 0.1, places=2)
        self.assertGreater(analysis["rms"], 0.1)
        self.assertGreater(analysis["peak"], 0.4)
        self.assertIn("sha256", analysis)

    def test_missing_wav_returns_error_payload(self):
        analysis = analyze_wav("missing.wav")

        self.assertFalse(analysis["exists"])
        self.assertEqual(analysis["error"], "missing_file")


def _write_test_wav(path: Path) -> None:
    sample_rate = 16000
    frames = []
    for index in range(sample_rate // 10):
        sample = int(16000 * math.sin(2 * math.pi * 440 * index / sample_rate))
        frames.append(struct.pack("<h", sample))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()

