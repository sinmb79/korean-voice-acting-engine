from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from kva_engine.review.manifest import build_generation_manifest
from kva_engine.review.text_metrics import transcript_metrics


def review_audio(
    *,
    audio_path: str | Path,
    expected_text: str | None = None,
    expected_text_path: str | Path | None = None,
    asr_model: str | None = None,
    asr_text: str | None = None,
    role: str | None = None,
    voice_profile_path: str | Path | None = None,
) -> dict[str, Any]:
    expected = _resolve_expected_text(expected_text=expected_text, expected_text_path=expected_text_path)
    manifest = build_generation_manifest(
        audio_path=audio_path,
        voice_profile_path=voice_profile_path,
        role=role,
    )
    review = {
        "job_id": _job_id(),
        "task": "audio_review",
        "audio_path": str(audio_path),
        "role": role,
        "expected_text_path": str(expected_text_path) if expected_text_path else None,
        "expected_text": expected,
        "asr": {
            "status": "provided" if asr_text is not None else "not_run",
            "model": asr_model,
            "text": asr_text,
        },
        "quality": _quality_gate(manifest.get("audio", {})),
        "metrics": None,
        "manifest": manifest,
    }

    if asr_text is None and asr_model:
        review["asr"] = _transcribe_with_whisper(audio_path=audio_path, model_name=asr_model)

    hypothesis = (review.get("asr") or {}).get("text")
    if expected and hypothesis:
        review["metrics"] = transcript_metrics(expected, hypothesis)

    review["ok"] = _is_review_ok(review)
    warnings = list(review["quality"]["warnings"])
    if (review.get("asr") or {}).get("status") == "error":
        warnings.append("asr_failed")
    if expected and not hypothesis:
        warnings.append("transcript_metrics_not_available")
    if review["metrics"] and review["metrics"]["cer"]["rate"] > 0.25:
        warnings.append("high_cer")
    if review["metrics"] and review["metrics"]["wer"]["rate"] > 0.4:
        warnings.append("high_wer")
    review["warnings"] = sorted(set(warnings))
    return review


def recording_check(*, audio_path: str | Path) -> dict[str, Any]:
    review = review_audio(audio_path=audio_path)
    review["task"] = "recording_check"
    review["recording_recommendations"] = _recording_recommendations(review.get("manifest", {}).get("audio", {}))
    review["warnings"] = sorted(set(review["warnings"] + review["recording_recommendations"]["warnings"]))
    review["ok"] = not review["warnings"]
    return review


def write_review(review: dict[str, Any], output_path: str | Path) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _resolve_expected_text(*, expected_text: str | None, expected_text_path: str | Path | None) -> str | None:
    if expected_text is not None:
        return expected_text
    if expected_text_path is None:
        return None
    return Path(expected_text_path).read_text(encoding="utf-8-sig").strip()


def _transcribe_with_whisper(*, audio_path: str | Path, model_name: str) -> dict[str, Any]:
    try:
        import whisper  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on optional local package
        return {
            "status": "error",
            "model": model_name,
            "text": None,
            "error": f"whisper_unavailable:{exc}",
        }

    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(str(audio_path), language="ko", fp16=False)
    except Exception as exc:  # pragma: no cover - depends on optional local package/model
        return {
            "status": "error",
            "model": model_name,
            "text": None,
            "error": f"whisper_transcribe_failed:{exc}",
        }

    return {
        "status": "ok",
        "model": model_name,
        "text": (result.get("text") or "").strip(),
        "segments": [
            {
                "start": round(float(segment.get("start", 0.0)), 3),
                "end": round(float(segment.get("end", 0.0)), 3),
                "text": (segment.get("text") or "").strip(),
            }
            for segment in result.get("segments", [])
        ],
    }


def _quality_gate(audio: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    if not audio.get("exists"):
        warnings.append("audio_missing")
        return {"status": "fail", "warnings": warnings}
    if audio.get("error"):
        warnings.append("audio_invalid")
    if audio.get("duration_sec", 0.0) < 1.0:
        warnings.append("audio_too_short")
    if audio.get("channels") not in (1, None):
        warnings.append("audio_not_mono")
    if audio.get("sample_rate_hz") not in (16000, 22050, 24000, 32000, 44100, 48000, None):
        warnings.append("unexpected_sample_rate")
    if audio.get("peak", 0.0) >= 0.99:
        warnings.append("possible_clipping")
    if audio.get("peak", 1.0) < 0.05:
        warnings.append("audio_peak_too_low")
    if audio.get("rms", 1.0) < 0.005:
        warnings.append("audio_rms_too_low")
    if audio.get("silence_ratio", 0.0) > 0.8:
        warnings.append("audio_mostly_silent")

    return {
        "status": "pass" if not warnings else "warn",
        "warnings": warnings,
        "duration_sec": audio.get("duration_sec"),
        "sample_rate_hz": audio.get("sample_rate_hz"),
        "channels": audio.get("channels"),
        "peak": audio.get("peak"),
        "rms": audio.get("rms"),
        "silence_ratio": audio.get("silence_ratio"),
    }


def _recording_recommendations(audio: dict[str, Any]) -> dict[str, Any]:
    warnings: list[str] = []
    suggestions: list[str] = []
    if not audio.get("exists"):
        warnings.append("recording_missing")
        suggestions.append("녹음 파일 경로를 다시 확인하세요.")
        return {"warnings": warnings, "suggestions": suggestions}

    duration = audio.get("duration_sec", 0.0)
    if duration < 30.0:
        warnings.append("recording_too_short_for_training")
        suggestions.append("프로 목소리 학습용 원본은 최소 10분, 권장 30분 이상으로 모으세요.")
    if audio.get("sample_rate_hz") not in (44100, 48000):
        warnings.append("recording_sample_rate_not_production_grade")
        suggestions.append("가능하면 44.1kHz 또는 48kHz WAV로 녹음하세요.")
    if audio.get("channels") != 1:
        warnings.append("recording_should_be_mono")
        suggestions.append("학습 입력은 mono WAV가 가장 관리하기 쉽습니다.")
    if audio.get("silence_ratio", 0.0) > 0.35:
        warnings.append("recording_has_many_pauses")
        suggestions.append("문장 사이 쉬는 구간은 남기되, 긴 무음은 분리/정리하세요.")

    return {"warnings": warnings, "suggestions": suggestions}


def _is_review_ok(review: dict[str, Any]) -> bool:
    if review["quality"]["status"] == "fail":
        return False
    if review["metrics"] and review["metrics"]["cer"]["rate"] > 0.25:
        return False
    return True


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
