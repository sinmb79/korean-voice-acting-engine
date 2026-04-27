from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def public_voice_catalog_path() -> Path:
    return repo_root() / "data" / "public_voice_catalog.json"


def load_public_voice_catalog(path: str | Path | None = None) -> dict[str, Any]:
    catalog_path = Path(path) if path else public_voice_catalog_path()
    with catalog_path.open("r", encoding="utf-8") as file:
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
