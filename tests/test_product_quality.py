import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.evaluation_suite import build_evaluation_suite_report, write_evaluation_suite
from kva_engine.product_quality import build_product_quality_report


class ProductQualityTests(unittest.TestCase):
    def test_eval_suite_contains_korean_product_prompts(self):
        report = build_evaluation_suite_report()
        prompt_ids = {prompt["id"] for prompt in report["prompts"]}

        self.assertGreaterEqual(len(report["prompts"]), 10)
        self.assertIn("ko_numbers_dates_units", prompt_ids)
        self.assertIn("ko_short_form_one_take", prompt_ids)
        self.assertIn("human_score_scale", report)

    def test_eval_suite_cli_writes_json_markdown_and_prompt_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                code = main(["eval-suite", "--out-dir", temp_dir, "--compact"])
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertEqual(payload["prompt_count"], 10)
            self.assertTrue(Path(payload["json_path"]).exists())
            self.assertTrue(Path(payload["markdown_path"]).exists())
            self.assertTrue((Path(payload["prompt_dir"]) / "ko_drama_low_breath.txt").exists())

    def test_product_quality_without_evidence_needs_evidence(self):
        report = build_product_quality_report(backend_id="voxcpm2", use_case="shorts")
        gate_statuses = {gate["id"]: gate["status"] for gate in report["gates"]}

        self.assertEqual(report["release_state"], "needs_evidence")
        self.assertEqual(gate_statuses["backend_status"], "pass")
        self.assertEqual(gate_statuses["review_report"], "missing")
        self.assertEqual(gate_statuses["human_listening_review"], "missing")

    def test_product_quality_blocks_noncommercial_backend_for_product_release(self):
        report = build_product_quality_report(backend_id="fish_audio_s2", use_case="shorts")
        gate_statuses = {gate["id"]: gate["status"] for gate in report["gates"]}

        self.assertEqual(report["release_state"], "blocked")
        self.assertEqual(gate_statuses["backend_status"], "fail")

    def test_product_quality_passes_with_review_and_human_scores(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            review_path = root / "review.json"
            human_path = root / "human.json"
            review_path.write_text(
                json.dumps(
                    {
                        "ok": True,
                        "warnings": [],
                        "quality": {
                            "status": "pass",
                            "warnings": [],
                            "peak": 0.82,
                            "rms": 0.035,
                            "silence_ratio": 0.08,
                        },
                        "metrics": {
                            "cer": {"rate": 0.01},
                            "wer": {"rate": 0.04},
                        },
                        "manifest": {
                            "safety": {
                                "ai_generated": True,
                                "voice_consent_required": True,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            human_path.write_text(
                json.dumps(
                    {
                        "korean_pronunciation": 4.5,
                        "naturalness": 4.4,
                        "emotion_fit": 4.2,
                        "artifact_control": 4.5,
                        "use_case_fit": 4.3,
                        "overall": 4.4,
                    }
                ),
                encoding="utf-8",
            )

            report = build_product_quality_report(
                backend_id="voxcpm2",
                use_case="shorts",
                review_path=review_path,
                human_scores_path=human_path,
            )

        self.assertEqual(report["release_state"], "ready")
        self.assertTrue(all(gate["status"] == "pass" for gate in report["gates"]))

    def test_product_quality_cli_outputs_backend_review(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main(["product-quality", "--backend", "voxcpm2", "--use-case", "announcer", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["backend_id"], "voxcpm2")
        self.assertEqual(payload["use_case"], "announcer")


if __name__ == "__main__":
    unittest.main()
