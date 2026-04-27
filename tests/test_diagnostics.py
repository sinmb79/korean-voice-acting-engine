import json
import tempfile
import unittest
from pathlib import Path

from kva_engine.cli import main
from kva_engine.diagnostics import run_doctor


class DiagnosticsTests(unittest.TestCase):
    def test_doctor_reports_core_checks(self):
        report = run_doctor(voice_profile_path="public:mms-tts-kor")
        names = {check["name"] for check in report["checks"]}

        self.assertIn(report["status"], {"pass", "warn"})
        self.assertIn("python_version", names)
        self.assertIn("public_voice_catalog", names)
        self.assertIn("voice_profile", names)
        self.assertEqual(report["summary"]["fail"], 0)

    def test_doctor_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out_path = Path(temp_dir) / "doctor.json"
            code = main(
                [
                    "doctor",
                    "--voice-profile",
                    "public:mms-tts-kor",
                    "--out",
                    str(out_path),
                    "--compact",
                ]
            )
            payload = json.loads(out_path.read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertIn(payload["status"], {"pass", "warn"})
        self.assertTrue(payload["checks"])

    def test_doctor_strict_returns_nonzero_on_missing_private_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.wav"
            code = main(["doctor", "--voice-profile", str(missing), "--strict", "--compact"])

        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
