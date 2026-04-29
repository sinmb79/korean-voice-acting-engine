import contextlib
import io
import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.synthesis.voice_polish import list_voice_polish_presets, polish_voice_file
from kva_engine.training.audio_features import analyze_wav


class VoicePolishTests(unittest.TestCase):
    def test_polish_voice_file_creates_broadcast_ready_wav(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            output = root / "announcer.wav"
            manifest = root / "announcer.json"
            _write_voice_like_wav(source)

            result = polish_voice_file(
                input_path=source,
                output_path=output,
                preset="announcer",
                manifest_path=manifest,
            )
            audio = analyze_wav(output)
            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))

        self.assertTrue(result["ok"])
        self.assertEqual(result["engine"], "kva-korean-voice-polish-v1")
        self.assertEqual(result["preset"]["name"], "announcer")
        self.assertTrue(audio["exists"])
        self.assertGreater(audio["rms"], 0.03)
        self.assertGreater(audio["peak"], 0.82)
        self.assertTrue(manifest_payload["safety"]["voice_identity_preserved"])
        self.assertTrue(manifest_payload["safety"]["not_a_new_speaker_or_child_voice"])

    def test_polish_cli_lists_presets_and_runs_shorts_preset(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            output = root / "shorts.wav"
            manifest = root / "shorts.json"
            _write_voice_like_wav(source)

            with contextlib.redirect_stdout(io.StringIO()):
                list_code = main(["polish", "--list-presets", "--compact"])
                run_code = main(
                    [
                        "polish",
                        "--input",
                        str(source),
                        "--out",
                        str(output),
                        "--preset",
                        "shorts",
                        "--manifest-out",
                        str(manifest),
                        "--compact",
                    ]
                )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            output_exists = output.exists()

        self.assertEqual(list_code, 0)
        self.assertEqual(run_code, 0)
        self.assertEqual(payload["preset"]["name"], "shorts")
        self.assertTrue(output_exists)

    def test_polish_presets_include_real_use_cases(self):
        names = {preset["name"] for preset in list_voice_polish_presets()}

        self.assertIn("announcer", names)
        self.assertIn("shorts", names)
        self.assertIn("drama", names)
        self.assertIn("documentary", names)


def _write_voice_like_wav(path: Path, *, sample_rate: int = 24000, duration_sec: float = 0.75) -> None:
    frames = []
    for index in range(int(sample_rate * duration_sec)):
        t = index / sample_rate
        envelope = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 4.0 * t))
        sample = (
            math.sin(2.0 * math.pi * 170.0 * t) * 0.35
            + math.sin(2.0 * math.pi * 820.0 * t) * 0.1
            + math.sin(2.0 * math.pi * 2200.0 * t) * 0.045
        )
        sample *= envelope
        frames.append(int(max(min(sample, 0.94), -0.94) * 32767).to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
