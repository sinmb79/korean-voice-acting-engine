import unittest

from kva_engine.acting.planner import plan_voice_acting
from kva_engine.korean.normalizer import normalize_text


class ActingPlannerTests(unittest.TestCase):
    def test_cast_plan_contains_role_parameters(self):
        script = normalize_text("그건 쉬운 일이 아니었지.")
        plan = plan_voice_acting(script, role="old_storyteller")
        self.assertEqual(plan["voice_acting"]["role"], "old_storyteller")
        self.assertLess(plan["voice_acting"]["speed"], 1.0)
        self.assertGreater(plan["voice_acting"]["role_strength"], 0.7)


if __name__ == "__main__":
    unittest.main()

