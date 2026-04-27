import unittest

from kva_engine.korean.josa import join_josa, select_josa


class JosaTests(unittest.TestCase):
    def test_select_josa_by_final_consonant(self):
        self.assertEqual(select_josa("코덱스", "은/는"), "는")
        self.assertEqual(select_josa("랩스", "은/는"), "는")
        self.assertEqual(select_josa("값", "은/는"), "은")

    def test_euro_ro_special_case_for_rieul(self):
        self.assertEqual(join_josa("서울", "으로/로"), "서울로")
        self.assertEqual(join_josa("부산", "으로/로"), "부산으로")


if __name__ == "__main__":
    unittest.main()
