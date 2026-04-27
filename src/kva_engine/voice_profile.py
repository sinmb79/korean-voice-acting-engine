from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from kva_engine.public_voices import public_voice_profile


VOICE_PROFILE_ENV = "KVA_DEFAULT_VOICE_PROFILE"
AUDIO_SUFFIXES = (".wav", ".m4a", ".mp3", ".flac")
PUBLIC_VOICE_PREFIX = "public:"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_local_voice_config() -> Path:
    return repo_root() / "configs" / "default_voice.local.json"


def load_voice_profile(path: str | Path | None = None) -> dict[str, Any] | None:
    if isinstance(path, str) and path.startswith(PUBLIC_VOICE_PREFIX):
        return public_voice_profile(path)

    profile_path = Path(path) if path else _default_profile_path()
    if profile_path is None:
        return None

    resolved_path = _resolve_existing_path(profile_path)
    if resolved_path is None:
        return {
            "id": profile_path.stem,
            "reference_audio": str(profile_path),
            "exists": False,
            "warning": "voice_profile_path_missing",
        }

    if resolved_path.suffix.lower() == ".json":
        data = _read_json_profile(resolved_path)
        reference = data.get("reference_audio") or data.get("reference_clip")
        if reference:
            reference_path = _resolve_existing_path(Path(reference), base_dir=resolved_path.parent)
            data["reference_audio"] = str(reference_path or reference)
            data["exists"] = bool(reference_path)
        else:
            data["exists"] = True
        data["profile_config"] = str(resolved_path)
        return data

    if resolved_path.is_dir():
        profile_json = resolved_path / "profile.json"
        if profile_json.exists():
            data = _read_json_profile(profile_json)
            data["profile_config"] = str(profile_json)
            data["profile_root"] = str(resolved_path)
            reference = _reference_from_profile(data, resolved_path)
            data["reference_audio"] = str(reference) if reference else None
            data["exists"] = reference.exists() if reference else True
            return data
        reference = _first_audio_file(resolved_path)
        return _audio_profile(reference or resolved_path)

    return _audio_profile(resolved_path)


def _default_profile_path() -> Path | None:
    env_path = os.environ.get(VOICE_PROFILE_ENV)
    if env_path:
        return Path(env_path)
    local_config = default_local_voice_config()
    if local_config.exists():
        return local_config
    return None


def _read_json_profile(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _resolve_existing_path(path: Path, *, base_dir: Path | None = None) -> Path | None:
    candidates = []
    if path.is_absolute():
        candidates.append(path)
    elif base_dir is not None:
        candidates.append(base_dir / path)
    candidates.append(path)

    for candidate in candidates:
        if candidate.exists():
            return candidate
        if candidate.suffix:
            continue
        for suffix in AUDIO_SUFFIXES:
            with_suffix = candidate.with_suffix(suffix)
            if with_suffix.exists():
                return with_suffix
    return None


def _reference_from_profile(data: dict[str, Any], profile_root: Path) -> Path | None:
    languages = data.get("languages", {})
    if isinstance(languages, dict):
        ko = languages.get("ko") or next(iter(languages.values()), {})
        if isinstance(ko, dict):
            reference = ko.get("reference_clip") or ko.get("reference_audio")
            if reference:
                return _resolve_existing_path(Path(reference), base_dir=profile_root)
    return _first_audio_file(profile_root)


def _first_audio_file(root: Path) -> Path | None:
    for suffix in AUDIO_SUFFIXES:
        match = next(root.rglob(f"*{suffix}"), None)
        if match:
            return match
    return None


def _audio_profile(path: Path) -> dict[str, Any]:
    return {
        "id": path.stem,
        "label": path.stem,
        "reference_audio": str(path),
        "exists": path.exists(),
        "privacy": "private-local-only",
    }
