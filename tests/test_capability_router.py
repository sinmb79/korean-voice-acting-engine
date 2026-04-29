import contextlib
import io
import json
import unittest

from kva_engine.capability_router import build_capability_report, get_capability_route, list_capability_routes
from kva_engine.cli import main


class CapabilityRouterTests(unittest.TestCase):
    def test_production_only_routes_hide_research_experiments(self):
        report = build_capability_report(production_only=True)
        policies = {route["production_policy"] for route in report["routes"]}
        route_ids = {route["id"] for route in report["routes"]}

        self.assertIn("kvae_supported", policies)
        self.assertIn("external_replacement", policies)
        self.assertNotIn("research_only", policies)
        self.assertNotIn("experimental_native_character", route_ids)

    def test_korean_polish_is_kvae_supported(self):
        route = get_capability_route("korean_voice_polish")

        self.assertEqual(route["production_policy"], "kvae_supported")
        self.assertEqual(route["default_handler"], "kva polish")
        self.assertTrue(any("announcer" in command for command in route["kvae_commands"]))
        self.assertFalse(route["external_replacements"])

    def test_child_voice_routes_to_external_replacement(self):
        route = get_capability_route("child_or_age_voice")
        replacements = {replacement["name"] for replacement in route["external_replacements"]}

        self.assertEqual(route["production_policy"], "external_replacement")
        self.assertIn("NAVER Cloud CLOVA Dubbing", replacements)
        self.assertIn("convincing child voice from a private adult voice", route["what_kvae_should_not_claim"])

    def test_persona_dataset_is_text_coverage_not_audio_training(self):
        route = get_capability_route("persona_script_coverage")
        replacement = route["external_replacements"][0]

        self.assertEqual(route["production_policy"], "kvae_supported")
        self.assertEqual(replacement["name"], "NVIDIA Nemotron-Personas-Korea")
        self.assertIn("do not treat it as audio training data", replacement["handoff"])
        self.assertIn("voice data or speaker embeddings are available from the persona dataset", route["what_kvae_should_not_claim"])

    def test_korean_tts_backend_selection_exposes_reviewed_candidates(self):
        route = get_capability_route("korean_tts_backend_selection")
        replacements = {replacement["name"]: replacement for replacement in route["external_replacements"]}

        self.assertEqual(route["production_policy"], "kvae_supported")
        self.assertEqual(route["default_handler"], "kva tts-backends")
        self.assertIn("MOSS-TTS-Nano", replacements)
        self.assertEqual(replacements["MOSS-TTS-Nano"]["license"], "Apache-2.0")
        self.assertIn("VibeVoice-Realtime-0.5B", replacements)
        self.assertIn("VoxCPM2", route["what_kvae_should_do"][0])

    def test_long_form_asr_routes_to_vibevoice_asr(self):
        route = get_capability_route("long_form_asr_and_diarization")
        replacement = route["external_replacements"][0]

        self.assertEqual(route["production_policy"], "external_replacement")
        self.assertEqual(replacement["name"], "VibeVoice-ASR")
        self.assertIn("60-minute", replacement["best_for"])
        self.assertIn("private voice recordings", route["what_kvae_should_not_claim"][-1])

    def test_voice_pro_is_external_due_to_license_boundary(self):
        route = get_capability_route("different_human_speaker")
        voice_pro = [replacement for replacement in route["external_replacements"] if replacement["name"] == "Voice-Pro"]

        self.assertEqual(len(voice_pro), 1)
        self.assertEqual(voice_pro[0]["license"], "GPL-3.0")
        self.assertIn("do not copy", voice_pro[0]["handoff"])

    def test_sound_effect_library_intake_requires_license_gate(self):
        route = get_capability_route("sound_effect_library_intake")
        quark = route["external_replacements"][0]

        self.assertEqual(route["production_policy"], "kvae_supported")
        self.assertEqual(route["default_handler"], "kva source-library")
        self.assertEqual(quark["license"], "unverified")
        self.assertIn("do not import audio", quark["handoff"])
        self.assertIn("permission to redistribute third-party SFX inside KVAE", route["what_kvae_should_not_claim"])

    def test_narrator_ai_is_external_video_narration_route(self):
        route = get_capability_route("external_video_narration_api")
        replacement = route["external_replacements"][0]

        self.assertEqual(route["production_policy"], "external_replacement")
        self.assertEqual(replacement["name"], "Narrator AI CLI Skill")
        self.assertEqual(replacement["license"], "MIT")
        self.assertIn("NARRATOR_APP_KEY", replacement["handoff"])
        self.assertIn("confirm before selecting or submitting resources", replacement["workflow_lessons"])

    def test_open_generative_ai_is_visual_lipsync_external_route(self):
        route = get_capability_route("visual_generation_lipsync")
        replacement = route["external_replacements"][0]

        self.assertEqual(route["production_policy"], "external_replacement")
        self.assertEqual(replacement["name"], "Open Generative AI")
        self.assertIn("README says MIT", replacement["license"])
        self.assertIn("no-filter", replacement["safety_note"])
        self.assertTrue(any("image or video generator" in claim for claim in route["what_kvae_should_not_claim"]))

    def test_capabilities_cli_outputs_requested_task(self):
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = main(["capabilities", "--task", "creature_or_dinosaur", "--compact"])
        payload = json.loads(stdout.getvalue())

        self.assertEqual(code, 0)
        self.assertEqual(payload["routes"][0]["id"], "creature_or_dinosaur")
        self.assertEqual(payload["routes"][0]["production_policy"], "external_replacement")

    def test_list_capability_routes_returns_copies(self):
        routes = list_capability_routes()
        routes[0]["id"] = "mutated"

        self.assertNotEqual(list_capability_routes()[0]["id"], "mutated")


if __name__ == "__main__":
    unittest.main()
