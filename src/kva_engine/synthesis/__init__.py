"""Speech synthesis backends owned by KVAE."""

from kva_engine.synthesis.conversion import build_voice_conversion_plan, convert_voice_file
from kva_engine.synthesis.voxcpm import build_voxcpm_synthesis_plan, render_voxcpm_speech

__all__ = [
    "build_voice_conversion_plan",
    "build_voxcpm_synthesis_plan",
    "convert_voice_file",
    "render_voxcpm_speech",
]
