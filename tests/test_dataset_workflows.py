import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.training.dataset import (
    apply_transcript_review_sheet,
    build_dataset_split,
    export_transcript_review_sheet,
    generate_recording_session_plan,
)


class DatasetWorkflowTests(unittest.TestCase):
    def test_generate_recording_session_plan_writes_json_and_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = generate_recording_session_plan(
                output_dir=temp_dir,
                speaker_id="demo-speaker",
                prompt_count=12,
            )

            plan_path = Path(plan["plan_path"])
            script_path = Path(plan["script_path"])

            self.assertEqual(plan["schema_version"], "kva.recording_session_plan.v1")
            self.assertEqual(plan["speaker_id"], "demo-speaker")
            self.assertEqual(plan["prompt_count"], 12)
            self.assertTrue(plan_path.exists())
            self.assertTrue(script_path.exists())
            self.assertIn("KVAE Recording Script", script_path.read_text(encoding="utf-8"))

    def test_recording_plan_cli_outputs_plan(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "recording-plan",
                        "--out-dir",
                        temp_dir,
                        "--prompt-count",
                        "5",
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertEqual(payload["prompt_count"], 5)
            self.assertTrue((Path(temp_dir) / "recording_session_plan.json").exists())

    def test_build_dataset_split_skips_missing_transcripts_when_required(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "segments_manifest.json"
            split_path = root / "split.json"
            manifest_path.write_text(
                json.dumps({"segments": _fake_segments(10, missing_transcripts={2, 5})}),
                encoding="utf-8",
            )

            split = build_dataset_split(
                manifest_path=manifest_path,
                output_path=split_path,
                require_transcript=True,
            )

            self.assertEqual(split["schema_version"], "kva.dataset_split.v1")
            self.assertEqual(split["summary"]["source_segment_count"], 10)
            self.assertEqual(split["summary"]["eligible_segment_count"], 8)
            self.assertEqual(split["summary"]["skipped_segment_count"], 2)
            self.assertTrue(split_path.exists())
            self.assertGreater(split["summary"]["train_count"], split["summary"]["validation_count"])
            self.assertEqual(len(split["splits"]["test"]), split["summary"]["test_count"])

    def test_dataset_split_cli_outputs_split(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "segments_manifest.json"
            split_path = root / "split.json"
            manifest_path.write_text(json.dumps({"segments": _fake_segments(6)}), encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "dataset-split",
                        "--manifest",
                        str(manifest_path),
                        "--out",
                        str(split_path),
                        "--compact",
                    ]
                )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(code, 0)
            self.assertEqual(payload["summary"]["source_segment_count"], 6)
            self.assertTrue(split_path.exists())

    def test_transcript_review_export_and_apply_updates_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            manifest_path = root / "segments_manifest.json"
            review_path = root / "review.tsv"
            reviewed_manifest_path = root / "reviewed_manifest.json"
            manifest_path.write_text(json.dumps({"segments": _fake_segments(3)}), encoding="utf-8")

            export = export_transcript_review_sheet(
                manifest_path=manifest_path,
                output_path=review_path,
            )
            rows = _read_tsv(review_path)
            rows[1]["corrected_transcript"] = "고친 문장입니다."
            rows[2]["status"] = "drop"
            rows[2]["notes"] = "잡음이 큼"
            _write_tsv(review_path, rows)

            result = apply_transcript_review_sheet(
                manifest_path=manifest_path,
                review_path=review_path,
                output_path=reviewed_manifest_path,
            )
            reviewed = json.loads(reviewed_manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(export["row_count"], 3)
            self.assertEqual(result["corrected_count"], 1)
            self.assertEqual(result["dropped_count"], 1)
            self.assertEqual(reviewed["segments"][1]["transcript"], "고친 문장입니다.")
            self.assertFalse(reviewed["segments"][2]["include_in_training"])


def _fake_segments(count: int, *, missing_transcripts: set[int] | None = None) -> list[dict]:
    missing_transcripts = missing_transcripts or set()
    return [
        {
            "index": index,
            "path": f"segment_{index:04d}.wav",
            "file_name": f"segment_{index:04d}.wav",
            "transcript": None if index in missing_transcripts else f"테스트 문장 {index}입니다.",
            "audio": {
                "sha256": f"{index:064x}",
                "duration_sec": 1.0,
            },
        }
        for index in range(1, count + 1)
    ]


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return [dict(row) for row in csv.DictReader(file, delimiter="\t")]


def _write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
