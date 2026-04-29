import unittest

from kva_engine.korean.english_reader import apply_dotted_spelling, apply_english_terms, apply_unknown_acronyms


class EnglishReaderTests(unittest.TestCase):
    def test_known_terms_are_replaced(self):
        text, traces = apply_english_terms("OpenAI API는 TTS")
        self.assertEqual(text, "오픈에이아이 에이피아이는 티티에스")
        self.assertEqual([trace.source for trace in traces], ["OpenAI", "API", "TTS"])

    def test_custom_terms_override_default_terms(self):
        text, _ = apply_english_terms("VibeVoice", {"VibeVoice": "바이브보이스"})
        self.assertEqual(text, "바이브보이스")

    def test_kvae_terms_are_slow_reading_friendly(self):
        text, _ = apply_english_terms("KVAE VoxCPM2")
        self.assertEqual(text, "케이, 브이, 에이, 이 복스 씨피엠 투")

    def test_dotted_spelling_is_slow_reading_friendly(self):
        text, traces = apply_dotted_spelling("M.A.R.I.A.")
        self.assertEqual(text, "엠, 에이, 아르, 아이, 에이")
        self.assertEqual(traces[0].rule, "dotted_spelling")

    def test_unknown_acronym_is_spelled(self):
        text, traces = apply_unknown_acronyms("ABC 테스트")
        self.assertEqual(text, "에이 비 씨 테스트")
        self.assertEqual(traces[0].kind, "spelling")


if __name__ == "__main__":
    unittest.main()
