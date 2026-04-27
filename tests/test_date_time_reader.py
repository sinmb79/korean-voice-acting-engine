import unittest

from kva_engine.korean.date_time_reader import normalize_datetime


class DateTimeReaderTests(unittest.TestCase):
    def test_full_korean_date_and_time(self):
        text, traces = normalize_datetime("2026년 4월 27일 오후 3시 5분")

        self.assertEqual(text, "이천이십육년 사월 이십칠일 오후 세 시 오 분")
        self.assertEqual([trace.rule for trace in traces], ["full_date", "time"])

    def test_iso_date(self):
        text, _ = normalize_datetime("2026-04-27")

        self.assertEqual(text, "이천이십육년 사월 이십칠일")

    def test_colon_time(self):
        text, _ = normalize_datetime("오후 03:05:09")

        self.assertEqual(text, "오후 세 시 오 분 구 초")


if __name__ == "__main__":
    unittest.main()
