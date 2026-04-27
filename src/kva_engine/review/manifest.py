from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from kva_engine.training.audio_features import analyze_wav
from kva_engine.voice_profile import load_voice_profile


def build_generation_manifest(
    *,
    script_path: str | Path | None = None,
    audio_path: str | Path | None = None,
    voice_profile_path: str | Path | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    voice_profile = load_voice_profile(voice_profile_path)
    manifest: dict[str, Any] = {
        "job_id": _job_id(),
        "engine": "kva-engine",
        "script_path": str(script_path) if script_path else None,
        "role": role,
        "voice_profile": voice_profile,
        "safety": {
            "ai_generated": True,
            "voice_consent_required": True,
            "voice_profile_privacy": (voice_profile or {}).get("privacy"),
            "redistribution_allowed": False,
        },
        "review": {
            "asr": "not_run",
            "pronunciation_review": "not_run",
            "warnings": [],
        },
    }
    if audio_path:
        manifest["audio"] = analyze_wav(audio_path)
        if not manifest["audio"].get("exists"):
            manifest["review"]["warnings"].append("audio_missing")
        elif manifest["audio"].get("silence_ratio", 0) > 0.8:
            manifest["review"]["warnings"].append("audio_mostly_silent")
    return manifest


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
