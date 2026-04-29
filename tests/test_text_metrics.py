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

    def test_percent_symbol_matches_korean_percent_reading(self):
        result = transcript_metrics("강수 확률은 30퍼센트였습니다.", "강수 확률은 30%였습니다.")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_kvae_spoken_aliases_match_english_product_names(self):
        result = transcript_metrics("KVAE VoxCPM2 ONNX CPU", "케이 브이 에이 이 복스 씨피엠 투 오닉스 씨피유")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_common_asr_product_spellings_match_product_names(self):
        result = transcript_metrics("KVAE VoxCPM2", "KVAV 복스 CPM2")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_counter_digit_matches_native_counter_reading(self):
        result = transcript_metrics("같은 문장을 세 번 생성했습니다.", "같은 문장을 3번 생성했습니다.")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_phone_money_and_address_spacing_variants_match(self):
        result = transcript_metrics(
            "문의 전화는 02-1234-5678이고, 참가비는 3만 5천 원입니다. 장소는 중구 세종대로 110입니다.",
            "문의 전화는 0212345678이고 참가비는 35,000원입니다. 장소는 중구세종대로 110입니다.",
        )

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_korean_spacing_and_phonetic_variants_match(self):
        result = transcript_metrics(
            "처음 세 초가 지나면, 바로 따라 할 수 있는 한 가지 방법이 꽂히는 순간입니다.",
            "처음 세초가 지나면 바로 따라할 수 있는 한가지 방법이 꼬치는 순간입니다.",
        )

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_native_time_words_match_digit_asr(self):
        result = transcript_metrics(
            "오늘 오후 여섯 시부터 약 삼십 분 동안 점검합니다.",
            "오늘 오후 6시부터 약 30분 동안 점검합니다.",
        )

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)

    def test_transcript_metrics_returns_cer_and_wer(self):
        result = transcript_metrics("오늘은 차분하게 말합니다", "오늘은 차분하게 말합니다")

        self.assertEqual(result["cer"]["rate"], 0.0)
        self.assertEqual(result["wer"]["rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
