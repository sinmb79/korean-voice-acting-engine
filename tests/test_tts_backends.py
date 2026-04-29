import contextlib
import io
import json
import unittest

from kva_engine.cli import main
from kva_engine.tts_backends import build_tts_backend_report, get_tts_backend


class TtsBackendsTests(unittest.TestCase):
    def test_voxcpm2_is_integrated_default(self):
        backend = get_tts_backend("voxcpm2")

        self.assertEqual(backend["kvae_status"], "integrated_default")
        self.assertEqual(backend["license"], "Apache-2.0")
        self.assertIn("Korean", backend["korean_support"])
        self.assertTrue(any("kva render" in use for use in backend["kvae_use"]))

    def test_moss_tts_nano_is_cpu_fallback_candidate(self):
        backend = get_tts_backend("moss_tts_nano")

        self.assertEqual(backend["kvae_status"], "research_candidate")
        self.assertEqual(backend["runtime"], "CPU-friendly; ONNX Runtime CPU path available")
        self.assertIn("20 supported languages", backend["korean_support"])
        self.assertIn("not yet wired into KVAE render", backend["limitations"])

    def test_vibevoice_realtime_is_research_only_for_korean(self):
        backend = get_tts_backend("vibevoice_realtime_tts")

        self.assertEqual(backend["license"], "MIT")
        self.assertIn("experimental", backend["korean_support"])
        self.assertIn("non-English output may be unpredictable", backend["limitations"])

    def test_vibevoice_asr_is_long_form_review_candidate(self):
        backend = get_tts_backend("vibevoice_asr")

        self.assertEqual(backend["backend_role"], "long_form_asr_and_diarization_candidate")
        self.assertIn("60-minute single-pass transcription", backend["strengths"])
        self.assertIn("private voices", backend["kvae_use"][-1])

    def test_production_only_report_keeps_only_integrated_backend(self):
        report = build_tts_backend_report(production_only=True)
        ids = {backend["id"] for backend in report["backends"]}

        self.assertEqual(ids, {"voxcpm2"})
        self.assertEqual(report["counts"], {"integrated_default": 1})

    def test_tts_backends_cli_outputs_requested_backend(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main(["tts-backends", "--id", "moss_tts_nano", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["backends"][0]["id"], "moss_tts_nano")
        self.assertIn("MOSS-TTS-Nano", payload["decision"])


if __name__ == "__main__":
    unittest.main()
