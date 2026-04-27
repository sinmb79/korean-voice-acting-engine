from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kva_engine.acting.presets import PRESETS
from kva_engine.training.family_registry import build_family_registry_training_manifest


FEATURE_KEYS = (
    "rms",
    "peak",
    "zero_crossing_rate",
    "silence_ratio",
    "dc_offset",
)


def train_native_voice_model(
    registry_root: str | Path,
    *,
    role: str | None = None,
    profile_id: str | None = None,
) -> dict[str, Any]:
    manifest = build_family_registry_training_manifest(
        registry_root,
        role=role,
        profile_id=profile_id,
    )
    rows = _collect_feature_rows(manifest)
    feature_stats = _feature_stats(rows)

    model = {
        "schema_version": "kva.native_voice_model.v1",
        "engine": "kva-native",
        "training_mode": "statistical_voiceprint_v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_registry": manifest["source_registry"],
        "safety": manifest["safety"],
        "environment": manifest["environment"],
        "feature_space": {
            "keys": list(FEATURE_KEYS),
            "stats": feature_stats,
            "pitch_note": (
                "Pitch contour is not learned in this stage because the secure "
                "environment has no DSP/ML dependency. Role pitch controls are "
                "stored separately for the future neural trainer."
            ),
        },
        "actors": [],
        "role_averages": {},
        "warnings": list(manifest.get("warnings", [])),
        "next_training_plan": [
            "Load this model as the KVA-native voice identity seed.",
            "Train a Korean acoustic model on consented speech-text pairs.",
            "Attach a neural vocoder only after pronunciation and prosody tests pass.",
            "Keep family voice weights private; publish code and example schemas only.",
        ],
    }

    for profile in manifest["profiles"]:
        actor = _build_actor(profile, feature_stats)
        model["actors"].append(actor)

    model["role_averages"] = _build_role_averages(model["actors"], feature_stats)
    model["summary"] = {
        "actor_count": len(model["actors"]),
        "language_actor_count": sum(len(actor["languages"]) for actor in model["actors"]),
        "audio_clip_count": len(rows),
        "total_audio_duration_sec": round(
            sum(float(row["duration_sec"]) for row in rows),
            3,
        ),
        "neural_training_available": manifest["environment"]["neural_training_available"],
    }
    if not rows:
        model["warnings"].append("no_audio_features_trained")
    return model


def _collect_feature_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for profile in manifest["profiles"]:
        for language, language_data in profile.get("languages", {}).items():
            for audio_key, audio in language_data.get("audio", {}).items():
                if not audio.get("exists") or audio.get("error"):
                    continue
                row = {
                    "profile_id": profile.get("id"),
                    "role": profile.get("role"),
                    "use_case": profile.get("use_case"),
                    "language": language,
                    "audio_key": audio_key,
                    "duration_sec": float(audio.get("duration_sec") or 0.0),
                }
                for key in FEATURE_KEYS:
                    row[key] = float(audio.get(key) or 0.0)
                rows.append(row)
    return rows


def _feature_stats(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    for key in FEATURE_KEYS:
        values = [float(row[key]) for row in rows]
        mean = sum(values) / len(values) if values else 0.0
        variance = (
            sum((value - mean) ** 2 for value in values) / len(values)
            if values
            else 0.0
        )
        stats[key] = {
            "mean": round(mean, 8),
            "std": round(math.sqrt(variance), 8),
        }
    return stats


def _build_actor(profile: dict[str, Any], feature_stats: dict[str, dict[str, float]]) -> dict[str, Any]:
    actor = {
        "id": profile.get("id"),
        "role": profile.get("role"),
        "use_case": profile.get("use_case"),
        "profile_name": profile.get("profile_name"),
        "owner": profile.get("owner"),
        "languages": {},
        "warnings": list(profile.get("warnings", [])),
    }
    for language, language_data in profile.get("languages", {}).items():
        audio_rows = []
        for audio_key, audio in language_data.get("audio", {}).items():
            if not audio.get("exists") or audio.get("error"):
                continue
            row = {"audio_key": audio_key, "duration_sec": float(audio.get("duration_sec") or 0.0)}
            for key in FEATURE_KEYS:
                row[key] = float(audio.get(key) or 0.0)
            audio_rows.append(row)

        aggregate = _weighted_feature_average(audio_rows)
        actor["languages"][language] = {
            "label": language_data.get("label"),
            "clip_count": len(audio_rows),
            "total_duration_sec": round(sum(row["duration_sec"] for row in audio_rows), 3),
            "acoustic_profile": aggregate,
            "normalized_voiceprint": _normalize_features(aggregate, feature_stats),
            "kva_timbre_controls": _derive_timbre_controls(aggregate),
            "acting_role_controls": _derive_role_controls(),
            "source_controls": language_data.get("controls", {}),
            "warnings": list(language_data.get("warnings", [])),
        }
    return actor


def _weighted_feature_average(rows: list[dict[str, Any]]) -> dict[str, float]:
    total_weight = sum(max(float(row["duration_sec"]), 0.001) for row in rows)
    aggregate: dict[str, float] = {}
    for key in FEATURE_KEYS:
        if not rows:
            aggregate[key] = 0.0
            continue
        value = sum(float(row[key]) * max(float(row["duration_sec"]), 0.001) for row in rows)
        aggregate[key] = round(value / total_weight, 8)
    return aggregate


def _normalize_features(
    aggregate: dict[str, float],
    feature_stats: dict[str, dict[str, float]],
) -> dict[str, float]:
    normalized = {}
    for key, value in aggregate.items():
        std = feature_stats[key]["std"] or 1.0
        normalized[key] = round((value - feature_stats[key]["mean"]) / std, 6)
    return normalized


def _derive_timbre_controls(aggregate: dict[str, float]) -> dict[str, float]:
    rms = aggregate.get("rms", 0.0)
    peak = aggregate.get("peak", 0.0)
    zcr = aggregate.get("zero_crossing_rate", 0.0)
    silence = aggregate.get("silence_ratio", 0.0)
    return {
        "energy": round(_clamp(rms / 0.2), 6),
        "brightness_proxy": round(_clamp(zcr / 0.25), 6),
        "dynamic_range_proxy": round(_clamp((peak - rms) / 0.8), 6),
        "breath_pause_proxy": round(_clamp(silence), 6),
        "warmth_proxy": round(_clamp(1.0 - zcr / 0.25), 6),
    }


def _derive_role_controls() -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = {}
    for name, preset in PRESETS.items():
        data = preset.to_dict()
        controls[name] = {
            "identity_strength": data["identity_strength"],
            "role_strength": data["role_strength"],
            "pitch_shift": data["pitch_shift"],
            "pitch_variance": data["pitch_variance"],
            "speed": data["speed"],
            "breathiness": data["breathiness"],
            "articulation_strength": data["articulation_strength"],
            "pause_scale": data["pause_scale"],
            "ending_style": data["ending_style"],
            "formality": data["formality"],
        }
    return controls


def _build_role_averages(
    actors: list[dict[str, Any]],
    feature_stats: dict[str, dict[str, float]],
) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, float]]] = {}
    for actor in actors:
        role = actor.get("role") or "unknown"
        for language_data in actor.get("languages", {}).values():
            grouped.setdefault(role, []).append(language_data["acoustic_profile"])

    averages = {}
    for role, profiles in grouped.items():
        average = {}
        for key in FEATURE_KEYS:
            average[key] = round(sum(profile[key] for profile in profiles) / len(profiles), 8)
        averages[role] = {
            "language_profile_count": len(profiles),
            "acoustic_profile": average,
            "normalized_voiceprint": _normalize_features(average, feature_stats),
            "kva_timbre_controls": _derive_timbre_controls(average),
        }
    return averages


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))
