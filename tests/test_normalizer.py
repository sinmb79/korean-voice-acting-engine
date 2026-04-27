import unittest

from kva_engine.korean.normalizer import normalize_text


class NormalizerTests(unittest.TestCase):
    def test_normalize_creates_speech_script(self):
        script = normalize_text("OpenAI API는 3.5초 안에 응답합니다.")
        self.assertEqual(script.speech_text, "오픈에이아이 에이피아이는 삼 점 오 초 안에 응답합니다.")
        self.assertIn("오픈에이아이", script.phoneme_text)
        self.assertTrue(script.normalization_trace)
        self.assertTrue(script.phrases)

    def test_custom_pronunciation_dictionary(self):
        script = normalize_text(
            "VibeVoice는 좋다.",
            pronunciation_dict={"terms": {"VibeVoice": "바이브보이스"}},
        )
        self.assertEqual(script.speech_text, "바이브보이스는 좋다.")

    def test_ascii_leftover_warning(self):
        script = normalize_text("abc는 아직 모른다.")
        self.assertIn("ascii_leftover_requires_review", script.warnings)

    def test_phoneme_text_uses_pronunciation_overrides(self):
        script = normalize_text("국립 연구소의 값이 크다.")
        self.assertIn("궁닙", script.phoneme_text)
        self.assertIn("갑씨", script.phoneme_text)


if __name__ == "__main__":
    unittest.main()
