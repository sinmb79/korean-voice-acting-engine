"""Speech synthesis backends owned by KVAE."""

from kva_engine.synthesis.conversion import build_voice_conversion_plan, convert_voice_file
from kva_engine.synthesis.native_character import build_native_character_controls, render_native_character_voice
from kva_engine.synthesis.voice_polish import polish_voice_file
from kva_engine.synthesis.voxcpm import build_voxcpm_synthesis_plan, render_voxcpm_speech

__all__ = [
    "build_voice_conversion_plan",
    "build_native_character_controls",
    "build_voxcpm_synthesis_plan",
    "convert_voice_file",
    "polish_voice_file",
    "render_native_character_voice",
    "render_voxcpm_speech",
]
