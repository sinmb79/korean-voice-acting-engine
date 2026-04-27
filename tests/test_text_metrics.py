import unittest

from kva_engine.review.text_metrics import character_error_rate, transcript_metrics, word_error_rate


class TextMetricsTests(unittest.TestCase):
    def test_character_error_rate_handles_korean_text(self):
        result = character_error_rate("안녕하세요 보스", "안녕하세오 보스")

        self.assertEqual(result["distance"], 1)
        self.assertGreater(result["reference_length"], 0)
        self.assertGreater(result["rate"], 0)

    def test_word_error_rate_ignores_punctuation_and_case(self):
        result = word_error_rate("KVAE는 한국어 성우 엔진입니다.", "kvae는 한국어 성우 도구입니다")

        self.assertEqual(result["distance"], 1)
        self.assertEqual(result["reference_length"], 4)

    def test_transcript_metrics_returns_cer_and_wer(self):
        result = transcript_metrics("오늘은 차분하게 말합니다", "오늘은 차분하게 말합니다")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
