import unittest

from kva_engine.korean.number_reader import normalize_numbers, read_decimal, read_digits, read_int_sino


class NumberReaderTests(unittest.TestCase):
    def test_sino_integer(self):
        self.assertEqual(read_int_sino(2026), "이천이십육")
        self.assertEqual(read_int_sino(12012), "만이천십이")

    def test_decimal(self):
        self.assertEqual(read_decimal("3.5"), "삼 점 오")

    def test_phone_digits_use_gong_for_zero(self):
        self.assertEqual(read_digits("010", zero="공"), "공일공")

    def test_normalize_mixed_numbers(self):
        text, traces = normalize_numbers("2026년 4월 27일 3.5초 v2.1 010-1234-5678")
        self.assertIn("이천이십육 년", text)
        self.assertIn("사월 이십칠일", text)
        self.assertIn("삼 점 오 초", text)
        self.assertIn("버전 이 점 일", text)
        self.assertIn("공일공 일이삼사 오육칠팔", text)
        self.assertGreaterEqual(len(traces), 5)

    def test_version_with_korean_josa(self):
        text, _ = normalize_numbers("v2.1을 테스트했다")
        self.assertEqual(text, "버전 이 점 일을 테스트했다")

    def test_currency_and_percent(self):
        text, _ = normalize_numbers("$500 30%")
        self.assertEqual(text, "오백 달러 삼십 퍼센트")


if __name__ == "__main__":
    unittest.main()
