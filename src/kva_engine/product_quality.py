from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

from kva_engine.tts_backends import get_tts_backend


USE_CASE_THRESHOLDS: dict[str, dict[str, float]] = {
    "cleanup": {
        "cer_max": 0.12,
        "wer_max": 0.22,
        "peak_max": 0.98,
        "rms_min": 0.006,
        "silence_ratio_max": 0.35,
        "human_overall_min": 4.0,
        "human_naturalness_min": 4.0,
    },
    "announcer": {
        "cer_max": 0.08,
        "wer_max": 0.16,
        "peak_max": 0.98,
        "rms_min": 0.008,
        "silence_ratio_max": 0.25,
        "human_overall_min": 4.2,
        "human_naturalness_min": 4.0,
    },
    "shorts": {
        "cer_max": 0.08,
        "wer_max": 0.18,
        "peak_max": 0.98,
        "rms_min": 0.01,
        "silence_ratio_max": 0.22,
        "human_overall_min": 4.2,
        "human_naturalness_min": 4.1,
    },
    "drama": {
        "cer_max": 0.10,
        "wer_max": 0.20,
        "peak_max": 0.98,
        "rms_min": 0.005,
        "silence_ratio_max": 0.35,
        "human_overall_min": 4.3,
        "human_naturalness_min": 4.3,
    },
    "documentary": {
        "cer_max": 0.08,
        "wer_max": 0.16,
        "peak_max": 0.98,
        "rms_min": 0.007,
        "silence_ratio_max": 0.30,
        "human_overall_min": 4.2,
        "human_naturalness_min": 4.2,
    },
}


MANUAL_SCORE_FIELDS = (
    "korean_pronunciation",
    "naturalness",
    "emotion_fit",
    "artifact_control",
    "use_case_fit",
    "overall",
)


def build_product_quality_report(
    *,
    backend_id: str,
    use_case: str = "shorts",
    review_path: str | Path | None = None,
    human_scores_path: str | Path | None = None,
) -> dict[str, Any]:
    if use_case not in USE_CASE_THRESHOLDS:
        raise KeyError(f"Unknown use case: {use_case}")

    backend = get_tts_backend(backend_id)
    thresholds = USE_CASE_THRESHOLDS[use_case]
    review = _load_json(review_path) if review_path else None
    human_scores = _load_json(human_scores_path) if human_scores_path else None

    gates = [
        _backend_gate(backend),
        _privacy_gate(backend),
        _review_gate(review, thresholds),
        _asr_metric_gate(review, thresholds),
        _audio_gate(review, thresholds),
        _human_gate(human_scores, thresholds),
        _release_disclosure_gate(review),
    ]
    return {
        "schema_version": "kva.product_quality.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "backend_id": backend_id,
        "use_case": use_case,
        "thresholds": thresholds,
        "backend": backend,
        "review_path": str(review_path) if review_path else None,
        "human_scores_path": str(human_scores_path) if human_scores_path else None,
        "release_state": _release_state(gates),
        "gates": gates,
        "next_actions": _next_actions(gates),
    }


def _backend_gate(backend: dict[str, Any]) -> dict[str, Any]:
    status = backend["kvae_status"]
    if status in {"integrated_default", "external_production_service"}:
        gate_status = "pass"
    elif "noncommercial" in status or "license_gated" in status:
        gate_status = "fail"
    else:
        gate_status = "warn"
    return {
        "id": "backend_status",
        "status": gate_status,
        "message": f"{backend['name']} status is {status}.",
        "evidence": {
            "license": backend["license"],
            "runtime": backend["runtime"],
            "korean_support": backend["korean_support"],
        },
    }


def _privacy_gate(backend: dict[str, Any]) -> dict[str, Any]:
    if backend["kvae_status"] == "external_production_service":
        return {
            "id": "privacy_boundary",
            "status": "warn",
            "message": "External cloud/service backend requires explicit consent and service-term review.",
        }
    return {
        "id": "privacy_boundary",
        "status": "pass",
        "message": "Backend can remain local or is not a production handoff by default.",
    }


def _review_gate(review: dict[str, Any] | None, thresholds: dict[str, float]) -> dict[str, Any]:
    if review is None:
        return {
            "id": "review_report",
            "status": "missing",
            "message": "Run kva review-audio and provide --review before product release.",
        }
    return {
        "id": "review_report",
        "status": "pass" if review.get("ok") else "fail",
        "message": "KVAE review-audio report is attached.",
        "evidence": {
            "ok": review.get("ok"),
            "warnings": review.get("warnings", []),
            "quality": review.get("quality", {}),
        },
    }


def _asr_metric_gate(review: dict[str, Any] | None, thresholds: dict[str, float]) -> dict[str, Any]:
    if review is None:
        return {
            "id": "transcript_accuracy",
            "status": "missing",
            "message": "Transcript metrics require review-audio with expected text and ASR text/model.",
        }
    metrics = review.get("metrics")
    if not metrics:
        return {
            "id": "transcript_accuracy",
            "status": "missing",
            "message": "CER/WER metrics are missing; provide expected text and ASR transcript before release.",
        }
    cer = float(metrics.get("cer", {}).get("rate", 1.0))
    wer = float(metrics.get("wer", {}).get("rate", 1.0))
    status = "pass" if cer <= thresholds["cer_max"] and wer <= thresholds["wer_max"] else "fail"
    return {
        "id": "transcript_accuracy",
        "status": status,
        "message": f"CER={cer:.3f}, WER={wer:.3f}.",
        "evidence": {"cer": cer, "wer": wer},
    }


def _audio_gate(review: dict[str, Any] | None, thresholds: dict[str, float]) -> dict[str, Any]:
    if review is None:
        return {
            "id": "audio_technical",
            "status": "missing",
            "message": "Audio technical checks require a review report.",
        }
    quality = review.get("quality", {})
    peak = quality.get("peak")
    rms = quality.get("rms")
    silence_ratio = quality.get("silence_ratio")
    if peak is None or rms is None or silence_ratio is None:
        return {
            "id": "audio_technical",
            "status": "missing",
            "message": "Peak, RMS, or silence ratio is missing from review quality data.",
        }
    status = "pass"
    if float(peak) > thresholds["peak_max"] or float(rms) < thresholds["rms_min"]:
        status = "fail"
    if float(silence_ratio) > thresholds["silence_ratio_max"]:
        status = "fail"
    return {
        "id": "audio_technical",
        "status": status,
        "message": f"peak={float(peak):.3f}, rms={float(rms):.4f}, silence={float(silence_ratio):.3f}.",
        "evidence": {"peak": peak, "rms": rms, "silence_ratio": silence_ratio},
    }


def _human_gate(human_scores: dict[str, Any] | None, thresholds: dict[str, float]) -> dict[str, Any]:
    if human_scores is None:
        return {
            "id": "human_listening_review",
            "status": "missing",
            "message": "Top-tier release requires human listening scores on Korean naturalness and use-case fit.",
            "required_fields": list(MANUAL_SCORE_FIELDS),
        }
    missing = [field for field in MANUAL_SCORE_FIELDS if field not in human_scores]
    if missing:
        return {
            "id": "human_listening_review",
            "status": "missing",
            "message": "Human listening score file is incomplete.",
            "missing_fields": missing,
        }
    naturalness = float(human_scores["naturalness"])
    overall = float(human_scores["overall"])
    status = "pass"
    if naturalness < thresholds["human_naturalness_min"] or overall < thresholds["human_overall_min"]:
        status = "fail"
    return {
        "id": "human_listening_review",
        "status": status,
        "message": f"naturalness={naturalness:.1f}, overall={overall:.1f}.",
        "evidence": {field: human_scores[field] for field in MANUAL_SCORE_FIELDS},
    }


def _release_disclosure_gate(review: dict[str, Any] | None) -> dict[str, Any]:
    if review is None:
        return {
            "id": "release_disclosure",
            "status": "missing",
            "message": "Disclosure gate requires the KVAE review manifest.",
        }
    safety = review.get("manifest", {}).get("safety", {})
    ai_generated = safety.get("ai_generated")
    consent_required = safety.get("voice_consent_required")
    if ai_generated is True and consent_required is True:
        return {
            "id": "release_disclosure",
            "status": "pass",
            "message": "Manifest carries AI-generated and voice-consent-required flags.",
        }
    return {
        "id": "release_disclosure",
        "status": "fail",
        "message": "Manifest safety metadata is incomplete.",
        "evidence": safety,
    }


def _release_state(gates: list[dict[str, Any]]) -> str:
    statuses = {gate["status"] for gate in gates}
    if "fail" in statuses:
        return "blocked"
    if "missing" in statuses:
        return "needs_evidence"
    if "warn" in statuses:
        return "conditional"
    return "ready"


def _next_actions(gates: list[dict[str, Any]]) -> list[str]:
    actions: list[str] = []
    for gate in gates:
        if gate["status"] == "fail":
            actions.append(f"Fix failed gate: {gate['id']} - {gate['message']}")
        elif gate["status"] == "missing":
            actions.append(f"Add missing evidence: {gate['id']} - {gate['message']}")
        elif gate["status"] == "warn":
            actions.append(f"Review warning: {gate['id']} - {gate['message']}")
    if not actions:
        actions.append("Release candidate satisfies the configured product-quality gates.")
    return actions


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
