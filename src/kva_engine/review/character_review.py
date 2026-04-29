from __future__ import annotations

import datetime as dt
import json
import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kva_engine.acting.presets import get_preset
from kva_engine.training.audio_features import analyze_wav


@dataclass(frozen=True)
class TargetMetric:
    key: str
    label: str
    minimum: float | None
    maximum: float | None
    weight: float
    recommendation_low: str
    recommendation_high: str


ROLE_TARGETS: dict[str, tuple[TargetMetric, ...]] = {
    "dinosaur": (
        TargetMetric("body_index", "sub-bass body", 0.46, None, 1.4, "add_low_body_resonance", ""),
        TargetMetric("human_speech_trace_index", "human speech trace", None, 0.2, 1.8, "", "remove_speech_formant_trace"),
        TargetMetric("brightness_index", "small-mouth brightness", None, 0.5, 1.0, "", "reduce_bright_human_presence"),
        TargetMetric("grit_index", "throat pressure grit", 0.18, 0.86, 1.0, "add_pressure_grit", "reduce_noisy_grit"),
    ),
    "monster": (
        TargetMetric("body_index", "large body", 0.36, None, 1.3, "add_low_body_resonance", ""),
        TargetMetric("grit_index", "rough throat", 0.28, None, 1.1, "add_roughness_and_subharmonics", ""),
        TargetMetric("human_speech_trace_index", "human speech trace", None, 0.52, 1.1, "", "reduce_clean_speech_formants"),
        TargetMetric("brightness_index", "presence", 0.06, 0.68, 0.8, "restore_audibility", "reduce_harsh_brightness"),
    ),
    "wolf": (
        TargetMetric("body_index", "canine body", 0.28, 0.86, 1.1, "add_chest_growl", "reduce_body_boom"),
        TargetMetric("grit_index", "growl texture", 0.22, 0.88, 1.1, "add_growl_modulation", "reduce_distortion"),
        TargetMetric("human_speech_trace_index", "human speech trace", None, 0.58, 1.0, "", "reduce_clean_speech_formants"),
        TargetMetric("brightness_index", "bite presence", 0.06, 0.66, 0.8, "restore_bite_presence", "reduce_harsh_brightness"),
    ),
    "child": (
        TargetMetric("brightness_index", "small bright tract", 0.38, None, 1.4, "raise_formants_and_presence", ""),
        TargetMetric("body_index", "adult body residue", None, 0.48, 1.3, "", "reduce_adult_low_body"),
        TargetMetric("human_speech_trace_index", "speech clarity", 0.22, 0.86, 1.0, "restore_child_speech_clarity", "reduce_whistly_artifacts"),
        TargetMetric("stability_index", "stable child line", 0.34, None, 0.7, "smooth_pitch_and_envelope", ""),
    ),
    "female_lead": (
        TargetMetric("brightness_index", "lead brightness", 0.28, 0.88, 1.2, "raise_formants_and_air", "reduce_harsh_presence"),
        TargetMetric("body_index", "male body residue", None, 0.58, 1.2, "", "reduce_male_body_anchor"),
        TargetMetric("human_speech_trace_index", "dialogue clarity", 0.2, 0.86, 1.0, "restore_dialogue_clarity", "reduce_sibilant_artifacts"),
        TargetMetric("stability_index", "graceful stability", 0.34, None, 0.8, "smooth_delivery_envelope", ""),
    ),
    "male_lead": (
        TargetMetric("body_index", "male lead body", 0.24, 0.78, 1.1, "add_chest_resonance", "reduce_boominess"),
        TargetMetric("brightness_index", "controlled presence", 0.08, 0.62, 0.9, "restore_presence", "reduce_bright_artifacts"),
        TargetMetric("human_speech_trace_index", "dialogue clarity", 0.2, 0.82, 1.0, "restore_dialogue_clarity", "reduce_clean_source_leak"),
        TargetMetric("stability_index", "composed stability", 0.36, None, 0.8, "smooth_delivery_envelope", ""),
    ),
    "narration": (
        TargetMetric("human_speech_trace_index", "speech clarity", 0.24, 0.86, 1.1, "restore_speech_clarity", "reduce_artifacts"),
        TargetMetric("body_index", "body", 0.16, 0.74, 0.8, "add_warmth", "reduce_muddiness"),
        TargetMetric("brightness_index", "presence", 0.08, 0.7, 0.8, "restore_presence", "reduce_harshness"),
        TargetMetric("stability_index", "stability", 0.34, None, 0.8, "smooth_delivery_envelope", ""),
    ),
}


def review_character_audio(
    *,
    audio_path: str | Path,
    role: str,
    out_path: str | Path | None = None,
) -> dict[str, Any]:
    features = analyze_character_features(audio_path)
    role_family = _role_family(role)
    targets = ROLE_TARGETS[role_family]
    findings = _evaluate_targets(features, targets)
    score = _score(features, targets)
    status = "pass" if score >= 78.0 and not _has_high_severity(findings) else "warn" if score >= 52.0 else "fail"
    warnings = sorted({finding["warning"] for finding in findings})
    preset = _role_controls(role)

    review = {
        "job_id": _job_id(),
        "task": "character_review",
        "audio_path": str(audio_path),
        "role": role,
        "role_family": role_family,
        "status": status,
        "ok": status != "fail",
        "score": round(score, 3),
        "warnings": warnings,
        "features": features,
        "role_controls": preset,
        "target_metrics": [_target_to_dict(target) for target in targets],
        "findings": findings,
        "development_actions": _development_actions(findings, role_family),
        "note": (
            "This review is an in-engine perceptual proxy. It does not replace human listening, "
            "but it makes role mismatch visible and repeatable."
        ),
    }
    if out_path:
        destination = Path(out_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return review


def analyze_character_features(audio_path: str | Path) -> dict[str, Any]:
    base = analyze_wav(audio_path)
    features: dict[str, Any] = {
        "audio": base,
        "exists": base.get("exists", False),
        "valid": not bool(base.get("error")) and bool(base.get("exists")),
    }
    if not features["valid"]:
        features["error"] = base.get("error", "missing_file")
        return features

    try:
        sample_rate, samples = _read_mono_wav(audio_path)
    except wave.Error as exc:
        features["valid"] = False
        features["error"] = f"invalid_wav:{exc}"
        return features

    total_energy = _energy(samples)
    if total_energy <= 0.00000001:
        features.update(
            {
                "low_band_ratio": 0.0,
                "low_mid_ratio": 0.0,
                "speech_band_ratio": 0.0,
                "presence_band_ratio": 0.0,
                "air_band_ratio": 0.0,
                "body_index": 0.0,
                "brightness_index": 0.0,
                "grit_index": 0.0,
                "human_speech_trace_index": 0.0,
                "stability_index": 0.0,
                "envelope_modulation": 0.0,
            }
        )
        return features

    lp_180 = _one_pole_lowpass(samples, sample_rate, 180.0)
    lp_700 = _one_pole_lowpass(samples, sample_rate, 700.0)
    lp_3000 = _one_pole_lowpass(samples, sample_rate, 3000.0)
    lp_6500 = _one_pole_lowpass(samples, sample_rate, 6500.0)

    low_ratio = _energy(lp_180) / total_energy
    low_mid_ratio = _energy(_subtract(lp_700, lp_180)) / total_energy
    speech_ratio = _energy(_subtract(lp_3000, lp_700)) / total_energy
    presence_ratio = _energy(_subtract(lp_6500, lp_3000)) / total_energy
    air_ratio = _energy(_subtract(samples, lp_6500)) / total_energy
    envelope_modulation = _envelope_modulation(samples, sample_rate)
    zcr = float(base.get("zero_crossing_rate", 0.0) or 0.0)

    body_index = _clamp(low_ratio * 1.35 + low_mid_ratio * 0.35)
    brightness_index = _clamp((presence_ratio + air_ratio) * 3.0 + zcr * 2.0)
    grit_index = _clamp((presence_ratio + air_ratio) * 1.35 + envelope_modulation * 0.32 + zcr * 1.15)
    human_speech_trace = _clamp(speech_ratio * 2.2 + presence_ratio * 0.8 - low_ratio * 0.22)
    stability_index = _clamp(1.0 - envelope_modulation * 0.62)

    features.update(
        {
            "sample_rate_hz": sample_rate,
            "low_band_ratio": round(low_ratio, 6),
            "low_mid_ratio": round(low_mid_ratio, 6),
            "speech_band_ratio": round(speech_ratio, 6),
            "presence_band_ratio": round(presence_ratio, 6),
            "air_band_ratio": round(air_ratio, 6),
            "zero_crossing_rate": round(zcr, 6),
            "brightness_proxy_hz": round(zcr * sample_rate / 2.0, 3),
            "body_index": round(body_index, 6),
            "brightness_index": round(brightness_index, 6),
            "grit_index": round(grit_index, 6),
            "human_speech_trace_index": round(human_speech_trace, 6),
            "stability_index": round(stability_index, 6),
            "envelope_modulation": round(envelope_modulation, 6),
        }
    )
    return features


def _evaluate_targets(features: dict[str, Any], targets: tuple[TargetMetric, ...]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not features.get("valid"):
        return [
            {
                "metric": "audio",
                "warning": "audio_invalid_for_character_review",
                "severity": "high",
                "value": features.get("error"),
                "target": "valid wav",
                "recommendation": "render_or_convert_to_valid_wav",
            }
        ]

    for target in targets:
        value = float(features.get(target.key, 0.0) or 0.0)
        if target.minimum is not None and value < target.minimum:
            findings.append(
                _finding(
                    target=target,
                    value=value,
                    direction="low",
                    recommendation=target.recommendation_low,
                )
            )
        if target.maximum is not None and value > target.maximum:
            findings.append(
                _finding(
                    target=target,
                    value=value,
                    direction="high",
                    recommendation=target.recommendation_high,
                )
            )
    return findings


def _finding(*, target: TargetMetric, value: float, direction: str, recommendation: str) -> dict[str, Any]:
    limit = target.minimum if direction == "low" else target.maximum
    assert limit is not None
    distance = abs(value - limit)
    severity = "high" if distance > 0.18 or target.weight >= 1.6 else "medium" if distance > 0.08 else "low"
    return {
        "metric": target.key,
        "label": target.label,
        "warning": f"{target.key}_{direction}",
        "severity": severity,
        "value": round(value, 6),
        "target": _target_range(target),
        "recommendation": recommendation,
    }


def _score(features: dict[str, Any], targets: tuple[TargetMetric, ...]) -> float:
    if not features.get("valid"):
        return 0.0
    weighted = 0.0
    total_weight = 0.0
    for target in targets:
        value = float(features.get(target.key, 0.0) or 0.0)
        weighted += _metric_score(value, target) * target.weight
        total_weight += target.weight
    return 100.0 * weighted / max(total_weight, 0.000001)


def _metric_score(value: float, target: TargetMetric) -> float:
    if target.minimum is not None and value < target.minimum:
        return _falloff(target.minimum - value)
    if target.maximum is not None and value > target.maximum:
        return _falloff(value - target.maximum)
    return 1.0


def _falloff(distance: float) -> float:
    return _clamp(1.0 - distance / 0.42)


def _development_actions(findings: list[dict[str, Any]], role_family: str) -> list[str]:
    actions = [finding["recommendation"] for finding in findings if finding.get("recommendation")]
    if role_family == "dinosaur" and not actions:
        actions.append("keep_source_identity_removed_and_compare_against_human_listener_notes")
    if not actions:
        actions.append("keep_current_role_settings_and_collect_human_ab_preference_notes")
    return sorted(set(actions))


def _role_family(role: str) -> str:
    if role.startswith("dinosaur_"):
        return "dinosaur"
    if role.startswith("monster_"):
        return "monster"
    if role.startswith("wolf_"):
        return "wolf"
    if role.startswith("child") or role == "child_bright":
        return "child"
    if role == "twentyfirst_grand_lady_lead":
        return "female_lead"
    if role == "twentyfirst_prince_lead":
        return "male_lead"
    return "narration"


def _role_controls(role: str) -> dict[str, Any]:
    try:
        return get_preset(role).to_dict()
    except ValueError:
        return {}


def _target_to_dict(target: TargetMetric) -> dict[str, Any]:
    return {
        "key": target.key,
        "label": target.label,
        "minimum": target.minimum,
        "maximum": target.maximum,
        "weight": target.weight,
    }


def _target_range(target: TargetMetric) -> str:
    low = "-inf" if target.minimum is None else f"{target.minimum:.3f}"
    high = "inf" if target.maximum is None else f"{target.maximum:.3f}"
    return f"{low}..{high}"


def _has_high_severity(findings: list[dict[str, Any]]) -> bool:
    return any(finding.get("severity") == "high" for finding in findings)


def _read_mono_wav(path: str | Path) -> tuple[int, list[float]]:
    wav_path = Path(path)
    with wave.open(str(wav_path), "rb") as reader:
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        sample_rate = reader.getframerate()
        frames = reader.readframes(reader.getnframes())

    max_abs = float(_max_abs_value(sample_width))
    samples: list[float] = []
    frame_width = sample_width * channels
    for offset in range(0, len(frames), frame_width):
        frame = frames[offset : offset + frame_width]
        if len(frame) < frame_width:
            break
        values = [
            _decode_pcm_sample(frame[channel * sample_width : (channel + 1) * sample_width], sample_width)
            for channel in range(channels)
        ]
        samples.append(sum(values) / (len(values) * max_abs))
    return sample_rate, samples


def _one_pole_lowpass(samples: list[float], sample_rate: int, cutoff_hz: float) -> list[float]:
    coeff = 1.0 - math.exp(-2.0 * math.pi * cutoff_hz / max(sample_rate, 1))
    state = 0.0
    output: list[float] = []
    for sample in samples:
        state += coeff * (sample - state)
        output.append(state)
    return output


def _subtract(left: list[float], right: list[float]) -> list[float]:
    return [left[index] - right[index] for index in range(min(len(left), len(right)))]


def _energy(samples: list[float]) -> float:
    return sum(sample * sample for sample in samples) / max(len(samples), 1)


def _envelope_modulation(samples: list[float], sample_rate: int) -> float:
    chunk_size = max(sample_rate // 50, 1)
    envelopes: list[float] = []
    for offset in range(0, len(samples), chunk_size):
        chunk = samples[offset : offset + chunk_size]
        if not chunk:
            continue
        envelopes.append(math.sqrt(sum(sample * sample for sample in chunk) / len(chunk)))
    if not envelopes:
        return 0.0
    mean = sum(envelopes) / len(envelopes)
    if mean <= 0.000001:
        return 0.0
    variance = sum((value - mean) ** 2 for value in envelopes) / len(envelopes)
    return _clamp(math.sqrt(variance) / mean, 0.0, 2.0)


def _decode_pcm_sample(raw: bytes, sample_width: int) -> int:
    if sample_width == 1:
        return raw[0] - 128
    if sample_width == 3:
        sign_byte = b"\xff" if raw[-1] & 0x80 else b"\x00"
        return int.from_bytes(raw + sign_byte, "little", signed=True)
    if sample_width in (2, 4):
        return int.from_bytes(raw, "little", signed=True)
    raise wave.Error(f"unsupported sample width: {sample_width}")


def _max_abs_value(sample_width: int) -> int:
    if sample_width == 1:
        return 128
    return 2 ** (sample_width * 8 - 1)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
