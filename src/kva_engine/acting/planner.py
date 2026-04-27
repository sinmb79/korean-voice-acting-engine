from __future__ import annotations

from typing import Any

from kva_engine.acting.presets import get_preset
from kva_engine.schemas import SpeechScript


def plan_voice_acting(
    script: SpeechScript,
    *,
    role: str = "calm_narrator",
    voice_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    preset = get_preset(role)
    plan = {
        "display_text": script.display_text,
        "speech_text": script.speech_text,
        "phoneme_text": script.phoneme_text,
        "voice_acting": preset.to_dict(),
        "phrases": [phrase.to_dict() for phrase in script.phrases],
        "warnings": script.warnings,
    }
    if voice_profile:
        plan["voice_profile"] = voice_profile
    return plan
