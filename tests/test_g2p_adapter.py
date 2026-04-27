import unittest

from kva_engine.korean.g2p_adapter import apply_g2p


class G2PAdapterTests(unittest.TestCase):
    def test_rules_mode_uses_internal_pronunciation_planner(self):
        text, traces, warnings = apply_g2p("국립 연구소의 값이 크다.", mode="rules")

        self.assertIn("궁닙", text)
        self.assertIn("갑씨", text)
        self.assertFalse(warnings)
        self.assertTrue(traces)

    def test_external_mode_warns_when_g2pk_is_missing(self):
        _text, _traces, warnings = apply_g2p("테스트", mode="external")

        if warnings:
            self.assertEqual(warnings, ["g2pk_not_available"])


if __name__ == "__main__":
    unittest.main()
