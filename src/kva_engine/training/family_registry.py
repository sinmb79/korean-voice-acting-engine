from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kva_engine.training.audio_features import analyze_wav, sha256_file


NEURAL_TRAINING_PACKAGES = ("torch", "torchaudio", "numpy", "soundfile", "librosa")
AUDIO_KEYS = ("reference_clip", "preview_clip", "voxcpm_reference_clip")


def inspect_neural_environment() -> dict[str, Any]:
    packages = {
        package: importlib.util.find_spec(package) is not None
        for package in NEURAL_TRAINING_PACKAGES
    }
    missing = [package for package, present in packages.items() if not present]
    return {
        "neural_training_available": not missing,
        "packages": packages,
        "missing_packages": missing,
        "execution_mode": "local-only",
        "note": (
            "Neural fine-tuning is disabled until the required local packages "
            "and model weights are supplied inside the secure environment."
        )
        if missing
        else "Required Python packages are visible; model weights still must be checked locally.",
    }


def build_family_registry_training_manifest(
    registry_root: str | Path,
    *,
    role: str | None = None,
    profile_id: str | None = None,
) -> dict[str, Any]:
    root = Path(registry_root).resolve()
    registry_path = root / "registry.json"
    registry = _read_json(registry_path)

    manifest: dict[str, Any] = {
        "schema_version": "kva.family_voice_training_manifest.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_registry": {
            "root": str(root),
            "registry_version": registry.get("registry_version"),
            "updated_at": registry.get("updated_at"),
            "privacy": registry.get("privacy"),
            "defaults": registry.get("defaults", {}),
            "registry_sha256": sha256_file(registry_path),
        },
        "safety": {
            "biometric_sensitive": True,
            "no_audio_copy": True,
            "no_network_upload": True,
            "consent_review_required": True,
            "recommended_public_release": "publish code and manifests only; keep family audio private",
        },
        "environment": inspect_neural_environment(),
        "filters": {"role": role, "profile_id": profile_id},
        "profiles": [],
        "warnings": [],
    }

    for entry in registry.get("profiles", []):
        if role and entry.get("role") != role:
            continue
        if profile_id and entry.get("id") != profile_id:
            continue
        profile = _inspect_profile(root, entry)
        manifest["profiles"].append(profile)

    manifest["summary"] = _summarize(manifest["profiles"], manifest["environment"])
    if not manifest["profiles"]:
        manifest["warnings"].append("no_profiles_matched_filter")
    if registry.get("privacy") != "private-shared-only":
        manifest["warnings"].append("unexpected_registry_privacy")
    return manifest


def _inspect_profile(registry_root: Path, entry: dict[str, Any]) -> dict[str, Any]:
    profile_root = registry_root / entry["path"]
    profile_path = profile_root / "profile.json"
    result: dict[str, Any] = {
        "id": entry.get("id"),
        "role": entry.get("role"),
        "use_case": entry.get("use_case"),
        "profile_name": entry.get("profile_name"),
        "path": str(profile_root),
        "registry_languages": entry.get("languages", []),
        "registry_engines": entry.get("engines", []),
        "profile_exists": profile_path.exists(),
        "languages": {},
        "warnings": [],
    }
    if not profile_path.exists():
        result["warnings"].append("missing_profile_json")
        return result

    profile = _read_json(profile_path)
    result.update(
        {
            "owner": profile.get("owner"),
            "profile_version": profile.get("profile_version"),
            "created_at": profile.get("created_at"),
            "source_note": profile.get("source_note"),
            "profile_sha256": sha256_file(profile_path),
        }
    )

    for language, language_config in profile.get("languages", {}).items():
        result["languages"][language] = _inspect_language(profile_root, language_config)

    return result


def _inspect_language(profile_root: Path, language_config: dict[str, Any]) -> dict[str, Any]:
    inspected: dict[str, Any] = {
        "label": language_config.get("label"),
        "controls": _extract_controls(language_config),
        "audio": {},
        "prompt_text": _inspect_prompt(profile_root, language_config),
        "lora": _inspect_lora(profile_root, language_config),
        "training_ready": False,
        "warnings": [],
    }

    for key in AUDIO_KEYS:
        relative = language_config.get(key)
        if not relative:
            continue
        audio_path = profile_root / relative
        inspected["audio"][key] = analyze_wav(audio_path)

    has_reference = any(
        item.get("exists") and not item.get("error")
        for item in inspected["audio"].values()
    )
    has_lora = inspected["lora"].get("status") == "present"
    inspected["training_ready"] = bool(has_reference or has_lora)
    if not has_reference:
        inspected["warnings"].append("missing_reference_audio")
    if not has_lora:
        inspected["warnings"].append("no_existing_lora_adapter")
    return inspected


def _extract_controls(language_config: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "cfg_weight",
        "exaggeration",
        "temperature",
        "target_peak",
        "target_rms",
        "voxcpm_control_text",
    )
    return {key: language_config[key] for key in keys if key in language_config}


def _inspect_prompt(profile_root: Path, language_config: dict[str, Any]) -> dict[str, Any] | None:
    prompt_file = language_config.get("voxcpm_prompt_text_file")
    prompt_text = language_config.get("voxcpm_control_text")
    if prompt_file:
        path = profile_root / prompt_file
        if not path.exists():
            return {"path": str(path), "exists": False, "error": "missing_prompt_file"}
        text = path.read_text(encoding="utf-8")
        return {
            "path": str(path),
            "exists": True,
            "sha256": sha256_file(path),
            "char_count": len(text),
            "line_count": len(text.splitlines()),
        }
    if prompt_text:
        return {
            "inline": True,
            "char_count": len(prompt_text),
            "line_count": len(prompt_text.splitlines()) or 1,
        }
    return None


def _inspect_lora(profile_root: Path, language_config: dict[str, Any]) -> dict[str, Any]:
    relative = language_config.get("voxcpm_lora_path")
    if not relative:
        return {"status": "not_configured"}

    lora_root = profile_root / relative
    result: dict[str, Any] = {
        "status": "present" if lora_root.exists() else "missing",
        "path": str(lora_root),
        "files": {},
    }
    if not lora_root.exists():
        return result

    for name in ("lora_config.json", "training_state.json", "lora_weights.safetensors"):
        path = lora_root / name
        if path.exists():
            result["files"][name] = {
                "exists": True,
                "file_size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            if name.endswith(".json"):
                result["files"][name]["json"] = _read_json(path)
        else:
            result["files"][name] = {"exists": False}

    weights = result["files"].get("lora_weights.safetensors", {})
    if not weights.get("exists"):
        result["status"] = "incomplete"
    return result


def _summarize(profiles: list[dict[str, Any]], environment: dict[str, Any]) -> dict[str, Any]:
    language_count = 0
    clip_count = 0
    total_duration_sec = 0.0
    existing_lora_languages = 0
    roles: dict[str, int] = {}

    for profile in profiles:
        role = profile.get("role") or "unknown"
        roles[role] = roles.get(role, 0) + 1
        for language_data in profile.get("languages", {}).values():
            language_count += 1
            if language_data.get("lora", {}).get("status") == "present":
                existing_lora_languages += 1
            for audio in language_data.get("audio", {}).values():
                if audio.get("exists") and not audio.get("error"):
                    clip_count += 1
                    total_duration_sec += float(audio.get("duration_sec") or 0.0)

    return {
        "profile_count": len(profiles),
        "language_profile_count": language_count,
        "audio_clip_count": clip_count,
        "total_audio_duration_sec": round(total_duration_sec, 3),
        "existing_lora_language_count": existing_lora_languages,
        "roles": roles,
        "neural_training_available": environment["neural_training_available"],
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

