import unittest

from kva_engine.korean.telephone_reader import normalize_telephone


class TelephoneReaderTests(unittest.TestCase):
    def test_mobile_phone_number(self):
        text, traces = normalize_telephone("010-1234-5678로 전화")

        self.assertEqual(text, "공일공, 일이삼사, 오육칠팔로 전화")
        self.assertEqual(traces[0].rule, "telephone_digits")

    def test_plus_82_number(self):
        text, _ = normalize_telephone("+82-010-1234-5678")

        self.assertEqual(text, "플러스 팔이, 공일공, 일이삼사, 오육칠팔")


if __name__ == "__main__":
    unittest.main()
