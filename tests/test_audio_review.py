import json
import math
import struct
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.review.audio_review import recording_check, review_audio


class AudioReviewTests(unittest.TestCase):
    def test_review_audio_reports_quality_and_transcript_metrics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wav_path = root / "voice.wav"
            _write_test_wav(wav_path, duration_sec=1.2)

            review = review_audio(
                audio_path=wav_path,
                expected_text="보스 오늘은 테스트입니다",
                asr_text="보스 오늘은 테스트입니다",
                role="calm_narrator",
            )

        self.assertTrue(review["ok"])
        self.assertEqual(review["quality"]["status"], "pass")
        self.assertEqual(review["metrics"]["cer"]["rate"], 0.0)
        self.assertEqual(review["manifest"]["role"], "calm_narrator")

    def test_recording_check_warns_when_training_clip_is_short(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wav_path = root / "short.wav"
            _write_test_wav(wav_path, duration_sec=1.2)

            review = recording_check(audio_path=wav_path)

        self.assertFalse(review["ok"])
        self.assertIn("recording_too_short_for_training", review["warnings"])

    def test_review_audio_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            wav_path = root / "voice.wav"
            out_path = root / "review.json"
            _write_test_wav(wav_path, duration_sec=1.2)

            code = main(
                [
                    "review-audio",
                    "--audio",
                    str(wav_path),
                    "--expected-text",
                    "안녕하세요",
                    "--asr-text",
                    "안녕하세요",
                    "--out",
                    str(out_path),
                ]
            )
            payload = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["metrics"]["wer"]["rate"], 0.0)


def _write_test_wav(path: Path, *, duration_sec: float) -> None:
    sample_rate = 16000
    frames = []
    frame_count = int(sample_rate * duration_sec)
    for index in range(frame_count):
        sample = int(9000 * math.sin(2 * math.pi * 440 * index / sample_rate))
        frames.append(struct.pack("<h", sample))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
