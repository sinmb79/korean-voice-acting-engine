from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def public_voice_catalog_path() -> Path:
    return repo_root() / "data" / "public_voice_catalog.json"


def load_public_voice_catalog(path: str | Path | None = None) -> dict[str, Any]:
    if path:
        with Path(path).open("r", encoding="utf-8") as file:
            return json.load(file)

    catalog_path = public_voice_catalog_path()
    if catalog_path.exists():
        with catalog_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    resource = resources.files("kva_engine.resources").joinpath("public_voice_catalog.json")
    with resource.open("r", encoding="utf-8") as file:
        return json.load(file)


def list_public_voices(
    *,
    include_experimental: bool = False,
    commercial_only: bool = False,
    path: str | Path | None = None,
) -> list[dict[str, Any]]:
    catalog = load_public_voice_catalog(path)
    voices = []
    for voice in catalog.get("voices", []):
        if commercial_only and voice.get("commercial_use_allowed") is not True:
            continue
        if not include_experimental and "manual_review" in str(voice.get("review_status", "")):
            continue
        voices.append(voice)
    return voices


def get_public_voice(voice_id: str, *, path: str | Path | None = None) -> dict[str, Any]:
    normalized_id = voice_id.removeprefix("public:")
    for voice in load_public_voice_catalog(path).get("voices", []):
        if voice.get("id") == normalized_id:
            return voice
    raise KeyError(f"Unknown public voice id: {voice_id}")


def public_voice_profile(voice_id: str, *, path: str | Path | None = None) -> dict[str, Any]:
    voice = get_public_voice(voice_id, path=path)
    return {
        "id": f"public:{voice['id']}",
        "label": voice.get("label"),
        "language": voice.get("language"),
        "privacy": "public-ai-voice",
        "exists": True,
        "public_voice": True,
        "source_url": voice.get("source_url"),
        "model_id": voice.get("model_id"),
        "dataset_id": voice.get("dataset_id"),
        "engine_hint": voice.get("engine_hint"),
        "license": voice.get("license"),
        "commercial_use_allowed": voice.get("commercial_use_allowed"),
        "redistribution_allowed": voice.get("redistribution_allowed"),
        "ai_voice_disclosure": voice.get("ai_voice_disclosure"),
        "attribution": voice.get("attribution"),
        "citation": voice.get("citation"),
        "review_status": voice.get("review_status"),
        "install_mode": voice.get("install_mode"),
    }


def build_public_voice_install_plan(
    voice_id: str,
    *,
    install_root: str | Path | None = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    voice = get_public_voice(voice_id, path=path)
    target_root = Path(install_root) if install_root else _default_install_root()
    target_dir = target_root / str(voice["id"])
    warnings = _install_warnings(voice)
    return {
        "voice_id": voice["id"],
        "label": voice.get("label"),
        "status": "plan_only",
        "target_dir": str(target_dir),
        "source_url": voice.get("source_url"),
        "model_id": voice.get("model_id"),
        "dataset_id": voice.get("dataset_id"),
        "engine_hint": voice.get("engine_hint"),
        "license": voice.get("license"),
        "commercial_use_allowed": voice.get("commercial_use_allowed"),
        "redistribution_allowed": voice.get("redistribution_allowed"),
        "license_ack_required": True,
        "download_is_automatic": False,
        "ai_voice_disclosure": voice.get("ai_voice_disclosure"),
        "attribution": voice.get("attribution"),
        "citation": voice.get("citation"),
        "warnings": warnings,
        "suggested_steps": _suggested_install_steps(voice, target_dir),
        "manifest_fields": {
            "voice_profile": public_voice_profile(voice_id, path=path),
            "required_disclosure": voice.get("ai_voice_disclosure"),
            "required_attribution": voice.get("attribution"),
            "license": voice.get("license"),
        },
    }


def _default_install_root() -> Path:
    env_value = os.environ.get("KVA_PUBLIC_VOICE_CACHE")
    if env_value:
        return Path(env_value)
    return Path.home() / ".cache" / "kvae" / "public-voices"


def _install_warnings(voice: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if voice.get("commercial_use_allowed") is not True:
        warnings.append("non_commercial_or_commercial_use_not_confirmed")
    if "manual_review" in str(voice.get("review_status", "")):
        warnings.append("manual_license_or_data_provenance_review_required")
    if voice.get("kind") == "training_dataset":
        warnings.append("dataset_source_not_a_ready_voice_model")
    return warnings


def _suggested_install_steps(voice: dict[str, Any], target_dir: Path) -> list[dict[str, Any]]:
    model_id = voice.get("model_id") or voice.get("dataset_id")
    steps: list[dict[str, Any]] = [
        {
            "step": "review_license",
            "description": "Open the source URL and review the license before downloading.",
            "url": voice.get("source_url"),
        },
        {
            "step": "acknowledge_ai_voice_disclosure",
            "description": voice.get("ai_voice_disclosure"),
        },
    ]
    if model_id:
        steps.append(
            {
                "step": "download_external_assets",
                "description": "KVAE does not download this automatically. Run only after license review.",
                "suggested_command": f"huggingface-cli download {model_id} --local-dir \"{target_dir}\"",
            }
        )
    steps.append(
        {
            "step": "register_local_cache",
            "description": "Keep downloaded model files outside the public git repository and reference them from local config.",
            "target_dir": str(target_dir),
        }
    )
    return steps
