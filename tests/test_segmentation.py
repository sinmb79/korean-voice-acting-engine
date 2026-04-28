import contextlib
import io
import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.training.segmentation import detect_wav_segments, split_wav_on_silence


class RecordingSegmentationTests(unittest.TestCase):
    def test_detect_wav_segments_finds_two_utterances(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "session.wav"
            _write_demo_wav(audio_path)

            segments = detect_wav_segments(audio_path=audio_path)

        self.assertEqual(len(segments), 2)
        self.assertGreaterEqual(segments[0].duration_sec, 0.5)
        self.assertGreaterEqual(segments[1].duration_sec, 0.5)

    def test_split_wav_on_silence_writes_segments_and_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio_path = root / "session.wav"
            transcript_path = root / "transcript.txt"
            output_dir = root / "segments"
            _write_demo_wav(audio_path)
            transcript_path.write_text("첫 문장입니다.\n두 번째 문장입니다.\n", encoding="utf-8")

            manifest = split_wav_on_silence(
                audio_path=audio_path,
                output_dir=output_dir,
                transcript_path=transcript_path,
            )

            manifest_path = Path(manifest["manifest_path"])
            first_segment = Path(manifest["segments"][0]["path"])
            second_segment = Path(manifest["segments"][1]["path"])

            self.assertEqual(manifest["segment_count"], 2)
            self.assertEqual(manifest["segments"][0]["transcript"], "첫 문장입니다.")
            self.assertEqual(manifest["segments"][1]["transcript"], "두 번째 문장입니다.")
            self.assertTrue(first_segment.exists())
            self.assertTrue(second_segment.exists())
            self.assertTrue(manifest_path.exists())

    def test_split_recording_cli_outputs_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            audio_path = root / "session.wav"
            output_dir = root / "segments"
            _write_demo_wav(audio_path)
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "split-recording",
                        "--audio",
                        str(audio_path),
                        "--out-dir",
                        str(output_dir),
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertEqual(payload["segment_count"], 2)
            self.assertTrue((output_dir / "segments_manifest.json").exists())


def _write_demo_wav(path: Path) -> None:
    sample_rate = 16000
    samples: list[int] = []
    samples.extend(_tone(sample_rate=sample_rate, duration_sec=0.6, frequency_hz=440.0))
    samples.extend([0] * int(sample_rate * 0.7))
    samples.extend(_tone(sample_rate=sample_rate, duration_sec=0.6, frequency_hz=660.0))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))


def _tone(*, sample_rate: int, duration_sec: float, frequency_hz: float) -> list[int]:
    frame_count = int(sample_rate * duration_sec)
    amplitude = 0.4 * 32767
    return [
        int(amplitude * math.sin(2 * math.pi * frequency_hz * frame / sample_rate))
        for frame in range(frame_count)
    ]


if __name__ == "__main__":
    unittest.main()
