from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kva_engine.acting.presets import get_preset
from kva_engine.synthesis.audio_postprocess import apply_role_audio_transform, normalize_wav_with_ffmpeg
from kva_engine.training.audio_features import analyze_wav
from kva_engine.voice_profile import load_voice_profile


@dataclass
class VoiceConversionPlan:
    engine: str
    input_path: Path
    output_path: Path
    role: str
    voice_profile: dict[str, Any] | None = None
    normalize: bool = True
    manifest_path: Path | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "input_path": str(self.input_path),
            "output_path": str(self.output_path),
            "role": self.role,
            "role_controls": _role_controls(self.role),
            "voice_profile": self.voice_profile,
            "normalize": self.normalize,
            "manifest_path": str(self.manifest_path) if self.manifest_path else None,
            "warnings": self.warnings,
        }


def build_voice_conversion_plan(
    *,
    input_path: str | Path,
    output_path: str | Path,
    role: str,
    voice_profile_path: str | Path | None = None,
    normalize: bool = True,
    manifest_path: str | Path | None = None,
) -> VoiceConversionPlan:
    source = Path(input_path)
    warnings: list[str] = []
    if not source.exists():
        warnings.append("input_audio_missing")

    role_controls = _role_controls(role)
    if not role_controls:
        warnings.append("unknown_role")

    return VoiceConversionPlan(
        engine="kva-convert-ffmpeg-v1",
        input_path=source,
        output_path=Path(output_path),
        role=role,
        voice_profile=load_voice_profile(voice_profile_path),
        normalize=normalize,
        manifest_path=Path(manifest_path) if manifest_path else Path(output_path).with_suffix(".manifest.json"),
        warnings=warnings,
    )


def convert_voice_file(plan: VoiceConversionPlan) -> dict[str, Any]:
    if not plan.input_path.exists():
        return {
            "ok": False,
            "error": f"Input audio does not exist: {plan.input_path}",
            "plan": plan.to_dict(),
        }

    role_controls = _role_controls(plan.role)
    if not role_controls:
        return {"ok": False, "error": f"Unknown role: {plan.role}", "plan": plan.to_dict()}

    role_output = _role_output_path(plan.output_path)
    role_postprocess = apply_role_audio_transform(plan.input_path, role_output, role_controls)
    if not role_postprocess.get("applied"):
        plan.warnings.append(f"role_audio_transform_{role_postprocess.get('reason', 'failed')}")

    postprocess_input = role_output if role_output.exists() else plan.input_path
    normalize_postprocess: dict[str, Any] = {"applied": False, "reason": "disabled"}
    if plan.normalize:
        normalize_postprocess = normalize_wav_with_ffmpeg(postprocess_input, plan.output_path)
        if not normalize_postprocess.get("applied"):
            plan.warnings.append(f"audio_normalization_{normalize_postprocess.get('reason', 'failed')}")
    else:
        plan.output_path.parent.mkdir(parents=True, exist_ok=True)
        plan.output_path.write_bytes(postprocess_input.read_bytes())

    manifest = {
        "job_id": _job_id(),
        "engine": "kva-engine",
        "task": "voice_conversion",
        "source_audio": _source_audio_info(plan.input_path),
        "role": plan.role,
        "voice_profile": plan.voice_profile,
        "safety": {
            "ai_generated": True,
            "voice_consent_required": True,
            "voice_profile_privacy": (plan.voice_profile or {}).get("privacy"),
            "redistribution_allowed": False,
        },
        "conversion": {
            "engine": plan.engine,
            "created_at": dt.datetime.now(dt.UTC).isoformat(),
            "input_path": str(plan.input_path),
            "output_path": str(plan.output_path),
            "role_controls": role_controls,
            "role_postprocess": role_postprocess,
            "postprocess": normalize_postprocess,
            "warnings": plan.warnings,
            "note": "This is the local deterministic conversion layer. A neural speech-to-speech backend can replace this engine without changing the CLI contract.",
        },
        "review": {
            "asr": "not_run",
            "pronunciation_review": "not_run",
            "warnings": list(plan.warnings),
        },
        "audio": analyze_wav(plan.output_path),
    }
    if not manifest["audio"].get("exists"):
        manifest["review"]["warnings"].append("audio_missing")
    elif manifest["audio"].get("silence_ratio", 0) > 0.8:
        manifest["review"]["warnings"].append("audio_mostly_silent")

    if plan.manifest_path:
        plan.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        plan.manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": manifest["audio"].get("exists", False),
        "plan": plan.to_dict(),
        "audio": manifest["audio"],
        "manifest_path": str(plan.manifest_path) if plan.manifest_path else None,
        "manifest": manifest,
        "warnings": plan.warnings,
    }


def _role_output_path(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.role{output_path.suffix}")


def _role_controls(role: str) -> dict[str, Any]:
    try:
        return get_preset(role).to_dict()
    except ValueError:
        return {}


def _source_audio_info(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(path),
        "file_name": path.name,
        "exists": path.exists(),
        "format": path.suffix.lower().lstrip(".") or "unknown",
    }
    if path.exists():
        info["file_size_bytes"] = path.stat().st_size
        if path.suffix.lower() == ".wav":
            info["wav_analysis"] = analyze_wav(path)
    return info


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
