import json
import math
import tempfile
import unittest
import wave
from pathlib import Path

from kva_engine.cli import main
from kva_engine.synthesis.native_character import (
    build_native_character_controls,
    render_native_character_voice,
)
from kva_engine.training.audio_features import analyze_wav


class NativeCharacterRendererTests(unittest.TestCase):
    def test_original_drama_leads_render_as_distinct_native_voices(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            prince = root / "prince.wav"
            lady = root / "lady.wav"
            _write_test_wav(source)

            prince_result = render_native_character_voice(source, prince, role="twentyfirst_prince_lead")
            lady_result = render_native_character_voice(source, lady, role="twentyfirst_grand_lady_lead")
            prince_audio = analyze_wav(prince)
            lady_audio = analyze_wav(lady)
            prince_bytes = prince.read_bytes()
            lady_bytes = lady.read_bytes()

        self.assertEqual(prince_result["engine"], "kva-native-character-v1")
        self.assertEqual(lady_result["engine"], "kva-native-character-v1")
        self.assertTrue(prince_audio["exists"])
        self.assertTrue(lady_audio["exists"])
        self.assertGreater(prince_audio["rms"], 0.01)
        self.assertGreater(lady_audio["rms"], 0.01)
        self.assertLess(
            lady_result["controls"]["source_identity_mix"],
            prince_result["controls"]["source_identity_mix"],
        )
        self.assertGreater(lady_result["controls"]["pitch_ratio"], prince_result["controls"]["pitch_ratio"])
        self.assertNotEqual(prince_bytes, lady_bytes)

    def test_dinosaur_native_path_removes_audible_source_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            output = root / "dinosaur.wav"
            _write_test_wav(source)

            result = render_native_character_voice(source, output, role="dinosaur_giant_roar")
            analysis = analyze_wav(output)

        self.assertEqual(result["engine"], "kva-native-character-v1")
        self.assertEqual(result["sub_engine"], "kva-bioacoustic-dinosaur-v3")
        self.assertEqual(result["controls"]["source_identity_mix"], 0.0)
        self.assertEqual(result["layering"]["external_audio_tool"], "not_used")
        self.assertTrue(analysis["exists"])
        self.assertLess(analysis["zero_crossing_rate"], 0.08)

    def test_convert_cli_can_render_with_native_engine_without_ffmpeg(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.wav"
            output = root / "monster.wav"
            result_json = root / "monster.result.json"
            manifest = root / "monster.manifest.json"
            _write_test_wav(source)

            code = main(
                [
                    "convert",
                    "--input",
                    str(source),
                    "--role",
                    "monster_deep_fx",
                    "--engine",
                    "native",
                    "--out",
                    str(output),
                    "--json-out",
                    str(result_json),
                    "--manifest-out",
                    str(manifest),
                ]
            )
            result = json.loads(result_json.read_text(encoding="utf-8"))
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
            output_exists = output.exists()

        self.assertEqual(code, 0)
        self.assertTrue(result["ok"])
        self.assertTrue(output_exists)
        self.assertEqual(manifest_data["conversion"]["engine"], "kva-native-character-v1")
        self.assertEqual(manifest_data["conversion"]["role_postprocess"]["layering"]["external_audio_tool"], "not_used")

    def test_controls_reduce_identity_as_character_distance_rises(self):
        calm = build_native_character_controls("calm_narrator")
        monster = build_native_character_controls("monster_deep_fx")

        self.assertGreater(calm.source_identity_mix, monster.source_identity_mix)
        self.assertGreater(monster.character_mix, calm.character_mix)


def _write_test_wav(path: Path, *, sample_rate: int = 24000, duration_sec: float = 0.65) -> None:
    frames = []
    for index in range(int(sample_rate * duration_sec)):
        t = index / sample_rate
        syllable = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2.0 * math.pi * 4.0 * t))
        carrier = math.sin(2.0 * math.pi * 180.0 * t) + 0.32 * math.sin(2.0 * math.pi * 360.0 * t)
        sample = carrier * syllable * 0.32
        frames.append(int(sample * 32767).to_bytes(2, "little", signed=True))

    with wave.open(str(path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(b"".join(frames))


if __name__ == "__main__":
    unittest.main()
