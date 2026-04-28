import math
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.synthesis.bioacoustic import (
    build_bioacoustic_dinosaur_controls,
    render_bioacoustic_dinosaur,
)
from kva_engine.training.audio_features import analyze_wav


class BioacousticDinosaurTests(unittest.TestCase):
    def test_dinosaur_roar_removes_audible_source_identity(self):
        controls = build_bioacoustic_dinosaur_controls("dinosaur_giant_roar")

        self.assertEqual(controls.source_identity_mix, 0.0)
        self.assertLessEqual(controls.closed_mouth_boom_hz, 35.0)
        self.assertIn("closed_mouth", controls.mode)

    def test_renderer_creates_nonhuman_wav_from_performance_envelope_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            output = root / "dinosaur.wav"
            _write_test_wav(source)

            result = render_bioacoustic_dinosaur(source, output, role="dinosaur_giant_roar")
            analysis = analyze_wav(output)

        self.assertTrue(result["applied"])
        self.assertEqual(result["engine"], "kva-bioacoustic-dinosaur-v3")
        self.assertEqual(result["controls"]["source_identity_mix"], 0.0)
        self.assertIn("only timing and energy", result["layering"]["source_identity"])
        self.assertTrue(analysis["exists"])
        self.assertGreater(analysis["rms"], 0.01)
        self.assertLess(analysis["zero_crossing_rate"], 0.08)


def _write_test_wav(path: Path, *, sample_rate: int = 48000, duration_sec: float = 1.0) -> None:
    frames = []
    for index in range(int(sample_rate * duration_sec)):
        t = index / sample_rate
        syllable_envelope = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 3.0 * t))
        sample = math.sin(2.0 * math.pi * 220.0 * t) * syllable_envelope * 0.45
        frames.append(int(sample * 32767).to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
