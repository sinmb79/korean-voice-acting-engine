from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from kva_engine.acting.presets import get_preset
from kva_engine.review.manifest import build_generation_manifest
from kva_engine.synthesis.audio_postprocess import apply_role_audio_transform, normalize_wav_with_ffmpeg
from kva_engine.training.audio_features import analyze_wav
from kva_engine.voice_profile import load_voice_profile


KVA_RESULT_PREFIX = "KVA_RESULT_JSON="
VOXCPM_PYTHON_ENV = "KVA_VOXCPM_PYTHON"
VOXCPM_MODEL_ENV = "KVA_VOXCPM_MODEL"


class VoxCpmRenderError(RuntimeError):
    def __init__(self, message: str, *, stdout: str = "", stderr: str = "") -> None:
        super().__init__(message)
        self.stdout = stdout
        self.stderr = stderr


@dataclass
class VoxCpmSynthesisPlan:
    engine: str
    text: str
    output_path: Path
    voice_profile: dict[str, Any] | None
    role: str | None = None
    python_executable: str = sys.executable
    model_path: str = "openbmb/VoxCPM2"
    reference_audio: Path | None = None
    prompt_audio: Path | None = None
    prompt_text_file: Path | None = None
    lora_path: Path | None = None
    cfg_value: float = 2.0
    inference_timesteps: int = 20
    role_audio_transform: bool = True
    normalize: bool = True
    manifest_path: Path | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "engine": self.engine,
            "text": self.text,
            "output_path": str(self.output_path),
            "role": self.role,
            "python_executable": self.python_executable,
            "model_path": self.model_path,
            "reference_audio": _path_or_none(self.reference_audio),
            "prompt_audio": _path_or_none(self.prompt_audio),
            "prompt_text_file": _path_or_none(self.prompt_text_file),
            "lora_path": _path_or_none(self.lora_path),
            "cfg_value": self.cfg_value,
            "inference_timesteps": self.inference_timesteps,
            "role_audio_transform": self.role_audio_transform,
            "role_controls": _role_controls(self.role),
            "normalize": self.normalize,
            "manifest_path": _path_or_none(self.manifest_path),
            "voice_profile": self.voice_profile,
            "warnings": self.warnings,
        }


def build_voxcpm_synthesis_plan(
    *,
    text: str,
    output_path: str | Path,
    voice_profile_path: str | Path | None = None,
    role: str | None = None,
    python_executable: str | None = None,
    model_path: str | None = None,
    reference_audio: str | Path | None = None,
    prompt_audio: str | Path | None = None,
    prompt_text_file: str | Path | None = None,
    lora_path: str | Path | None = None,
    cfg_value: float | None = None,
    inference_timesteps: int = 20,
    role_audio_transform: bool = True,
    normalize: bool = True,
    manifest_path: str | Path | None = None,
) -> VoxCpmSynthesisPlan:
    profile = load_voice_profile(voice_profile_path)
    language = _language_settings(profile)
    warnings: list[str] = []

    resolved_reference = _resolve_setting_path(
        explicit=reference_audio,
        profile=profile,
        keys=("reference_audio", "voxcpm_reference_clip", "reference_clip"),
        language=language,
    )
    resolved_prompt_audio = _resolve_setting_path(
        explicit=prompt_audio,
        profile=profile,
        keys=("voxcpm_prompt_audio", "prompt_audio", "reference_audio", "voxcpm_reference_clip"),
        language=language,
    )
    resolved_prompt_text = _resolve_setting_path(
        explicit=prompt_text_file,
        profile=profile,
        keys=("voxcpm_prompt_text_file", "prompt_text_file"),
        language=language,
    )
    resolved_lora = _resolve_setting_path(
        explicit=lora_path,
        profile=profile,
        keys=("voxcpm_lora_path", "lora_path"),
        language=language,
        require_exists=False,
    )

    if resolved_reference is None:
        warnings.append("reference_audio_missing")
    elif not resolved_reference.exists():
        warnings.append("reference_audio_not_found")
    if resolved_prompt_text is not None and not resolved_prompt_text.exists():
        warnings.append("prompt_text_file_not_found")
    if resolved_lora is None:
        warnings.append("voxcpm_lora_missing_using_base_model")
    elif not resolved_lora.exists():
        warnings.append("voxcpm_lora_path_not_found")

    plan = VoxCpmSynthesisPlan(
        engine="voxcpm",
        text=text,
        output_path=Path(output_path),
        voice_profile=profile,
        role=role,
        python_executable=_resolve_python_executable(python_executable, profile=profile, language=language),
        model_path=_resolve_model_path(model_path, profile=profile, language=language),
        reference_audio=resolved_reference,
        prompt_audio=resolved_prompt_audio,
        prompt_text_file=resolved_prompt_text,
        lora_path=resolved_lora,
        cfg_value=cfg_value if cfg_value is not None else _float_setting(profile, language, "cfg_weight", 2.0),
        inference_timesteps=inference_timesteps,
        role_audio_transform=role_audio_transform,
        normalize=normalize,
        manifest_path=Path(manifest_path) if manifest_path else Path(output_path).with_suffix(".manifest.json"),
        warnings=warnings,
    )
    return plan


def render_voxcpm_speech(plan: VoxCpmSynthesisPlan) -> dict[str, Any]:
    if plan.reference_audio is None:
        raise VoxCpmRenderError("VoxCPM rendering requires reference_audio.")
    if not plan.reference_audio.exists():
        raise VoxCpmRenderError(f"Reference audio does not exist: {plan.reference_audio}")

    raw_output = _raw_output_path(plan.output_path) if plan.normalize else plan.output_path
    raw_output.parent.mkdir(parents=True, exist_ok=True)

    payload = _runner_payload(plan, raw_output)
    completed = _run_voxcpm_payload(plan.python_executable, payload)
    runner_result = _parse_runner_result(completed.stdout)
    if completed.returncode != 0:
        raise VoxCpmRenderError(
            f"VoxCPM runner failed with exit code {completed.returncode}",
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    role_postprocess: dict[str, Any] = {"applied": False, "reason": "disabled"}
    postprocess_input = raw_output
    role_controls = _role_controls(plan.role)
    if plan.role_audio_transform and role_controls:
        role_output = _role_output_path(plan.output_path)
        role_postprocess = apply_role_audio_transform(raw_output, role_output, role_controls)
        if role_postprocess.get("applied"):
            postprocess_input = role_output
        elif role_postprocess.get("reason") != "neutral_role_controls":
            plan.warnings.append(f"role_audio_transform_{role_postprocess.get('reason', 'failed')}")

    postprocess: dict[str, Any] = {"applied": False, "reason": "disabled"}
    if plan.normalize:
        postprocess = normalize_wav_with_ffmpeg(postprocess_input, plan.output_path)
        if not postprocess.get("applied"):
            plan.warnings.append(f"audio_normalization_{postprocess.get('reason', 'failed')}")
    elif postprocess_input != plan.output_path and postprocess_input.exists():
        plan.output_path.write_bytes(postprocess_input.read_bytes())

    manifest = build_generation_manifest(
        audio_path=plan.output_path,
        voice_profile_path=(plan.voice_profile or {}).get("profile_config"),
        role=plan.role,
    )
    manifest["synthesis"] = {
        "engine": plan.engine,
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "text": plan.text,
        "python_executable": plan.python_executable,
        "model_path": plan.model_path,
        "reference_audio": str(plan.reference_audio),
        "prompt_audio": _path_or_none(plan.prompt_audio),
        "prompt_text_file": _path_or_none(plan.prompt_text_file),
        "lora_path": _path_or_none(plan.lora_path),
        "cfg_value": plan.cfg_value,
        "inference_timesteps": plan.inference_timesteps,
        "role_controls": role_controls,
        "raw_output_path": str(raw_output),
        "role_postprocess": role_postprocess,
        "postprocess": postprocess,
        "runner_result": runner_result,
        "warnings": plan.warnings,
    }
    if plan.manifest_path:
        plan.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        plan.manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": manifest.get("audio", {}).get("exists", False),
        "plan": plan.to_dict(),
        "audio": analyze_wav(plan.output_path),
        "manifest_path": _path_or_none(plan.manifest_path),
        "manifest": manifest,
    }


def _runner_payload(plan: VoxCpmSynthesisPlan, output_path: Path) -> dict[str, Any]:
    prompt_text = None
    if plan.prompt_text_file and plan.prompt_text_file.exists():
        prompt_text = plan.prompt_text_file.read_text(encoding="utf-8-sig").strip()

    return {
        "text": plan.text,
        "output_path": str(output_path),
        "reference_wav_path": str(plan.reference_audio),
        "prompt_wav_path": str(plan.prompt_audio or plan.reference_audio),
        "prompt_text": prompt_text,
        "lora_path": _path_or_none(plan.lora_path),
        "model_path": plan.model_path,
        "cfg_value": plan.cfg_value,
        "inference_timesteps": plan.inference_timesteps,
    }


def _run_voxcpm_payload(python_executable: str, payload: dict[str, Any]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="kva-voxcpm-") as temp_dir:
        payload_path = Path(temp_dir) / "payload.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [python_executable, "-c", VOXCPM_RUNNER_CODE, str(payload_path)],
            capture_output=True,
            text=True,
            check=False,
        )


def _parse_runner_result(stdout: str) -> dict[str, Any]:
    for line in reversed(stdout.splitlines()):
        if line.startswith(KVA_RESULT_PREFIX):
            return json.loads(line.removeprefix(KVA_RESULT_PREFIX))
    return {"warning": "runner_result_marker_missing"}


def _resolve_python_executable(
    explicit: str | None,
    *,
    profile: dict[str, Any] | None,
    language: dict[str, Any],
) -> str:
    if explicit:
        return explicit
    for value in (
        os.environ.get(VOXCPM_PYTHON_ENV),
        language.get("voxcpm_python"),
        (profile or {}).get("voxcpm_python"),
    ):
        if value:
            return str(value)

    science_short_python = Path.home() / "workspace" / "ScienceShort" / ".venv-voxcpm" / "Scripts" / "python.exe"
    if science_short_python.exists():
        return str(science_short_python)
    return sys.executable


def _resolve_model_path(
    explicit: str | None,
    *,
    profile: dict[str, Any] | None,
    language: dict[str, Any],
) -> str:
    for value in (
        explicit,
        os.environ.get(VOXCPM_MODEL_ENV),
        language.get("voxcpm_model_path"),
        (profile or {}).get("voxcpm_model_path"),
    ):
        if value:
            return str(value)

    local_model = Path.home() / "workspace" / "ScienceShort" / "models" / "VoxCPM2"
    if local_model.exists():
        return str(local_model)
    return "openbmb/VoxCPM2"


def _resolve_setting_path(
    *,
    explicit: str | Path | None,
    profile: dict[str, Any] | None,
    keys: tuple[str, ...],
    language: dict[str, Any],
    require_exists: bool = True,
) -> Path | None:
    value = explicit
    if value is None:
        for key in keys:
            value = language.get(key)
            if value is not None:
                break
    if value is None and profile:
        for key in keys:
            value = profile.get(key)
            if value is not None:
                break
    if value is None:
        return None

    path = Path(value)
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    else:
        candidates.extend(base / path for base in _profile_base_dirs(profile))
        candidates.append(path)

    for candidate in candidates:
        if candidate.exists():
            return candidate
        if not candidate.suffix:
            for suffix in (".wav", ".m4a", ".mp3", ".flac"):
                with_suffix = candidate.with_suffix(suffix)
                if with_suffix.exists():
                    return with_suffix
    return candidates[0] if candidates and not require_exists else (candidates[0] if candidates else None)


def _profile_base_dirs(profile: dict[str, Any] | None) -> list[Path]:
    if not profile:
        return [Path.cwd()]

    bases: list[Path] = []
    for key in ("profile_root",):
        value = profile.get(key)
        if value:
            bases.append(Path(value))
    for key in ("profile_config", "profile_json"):
        value = profile.get(key)
        if value:
            bases.append(Path(value).parent)
    reference = profile.get("reference_audio")
    if reference:
        bases.append(Path(reference).parent)

    unique: list[Path] = []
    for base in bases + [Path.cwd()]:
        if base not in unique:
            unique.append(base)
    return unique


def _language_settings(profile: dict[str, Any] | None) -> dict[str, Any]:
    languages = (profile or {}).get("languages", {})
    if not isinstance(languages, dict) or not languages:
        return {}
    ko = languages.get("ko")
    if isinstance(ko, dict):
        return ko
    first = next(iter(languages.values()))
    return first if isinstance(first, dict) else {}


def _float_setting(profile: dict[str, Any] | None, language: dict[str, Any], key: str, default: float) -> float:
    value = language.get(key, (profile or {}).get(key, default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _raw_output_path(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.raw{output_path.suffix}")


def _role_output_path(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.role{output_path.suffix}")


def _path_or_none(path: Path | None) -> str | None:
    return str(path) if path is not None else None


def _role_controls(role: str | None) -> dict[str, Any]:
    if not role:
        return {}
    try:
        return get_preset(role).to_dict()
    except ValueError:
        return {}


VOXCPM_RUNNER_CODE = r'''
from __future__ import annotations

import json
import sys
from pathlib import Path

import soundfile as sf

from voxcpm import VoxCPM
from voxcpm.model.voxcpm import LoRAConfig

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
kwargs = {"load_denoiser": False}
lora_path = payload.get("lora_path")
if lora_path:
    lora_dir = Path(lora_path)
    lora_info = json.loads((lora_dir / "lora_config.json").read_text(encoding="utf-8"))
    kwargs["lora_config"] = LoRAConfig(**lora_info["lora_config"])
    kwargs["lora_weights_path"] = str(lora_dir)

model = VoxCPM.from_pretrained(payload["model_path"], **kwargs)
generate_kwargs = {
    "text": payload["text"],
    "reference_wav_path": payload["reference_wav_path"],
    "cfg_value": payload["cfg_value"],
    "inference_timesteps": payload["inference_timesteps"],
}
if payload.get("prompt_text"):
    generate_kwargs["prompt_text"] = payload["prompt_text"]
if payload.get("prompt_wav_path"):
    generate_kwargs["prompt_wav_path"] = payload["prompt_wav_path"]

wav = model.generate(**generate_kwargs)
output_path = Path(payload["output_path"])
output_path.parent.mkdir(parents=True, exist_ok=True)
sf.write(str(output_path), wav, model.tts_model.sample_rate)
print("KVA_RESULT_JSON=" + json.dumps({
    "saved": str(output_path),
    "sample_rate": model.tts_model.sample_rate,
    "lora_loaded": bool(lora_path),
}, ensure_ascii=False))
'''
