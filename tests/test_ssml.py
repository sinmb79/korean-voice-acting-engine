import unittest

from kva_engine.korean.normalizer import normalize_text
from kva_engine.ssml import speech_script_to_ssml


class SSMLTests(unittest.TestCase):
    def test_speech_script_to_ssml_adds_breaks(self):
        script = normalize_text("안녕하세요. 테스트입니다.")
        ssml = speech_script_to_ssml(script)

        self.assertTrue(ssml.startswith("<speak>"))
        self.assertIn("<break", ssml)
        self.assertIn("안녕하세요.", ssml)


if __name__ == "__main__":
    unittest.main()
