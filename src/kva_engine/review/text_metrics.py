from __future__ import annotations

import re
import unicodedata
from collections.abc import Sequence
from typing import Any


_SPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s가-힣]", re.UNICODE)

_ASR_ALIAS_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"케이\s*브이\s*에이\s*이|케이브이에이이"), "kvae"),
    (re.compile(r"\bkvav\b"), "kvae"),
    (re.compile(r"\bvox\s*cpm\s*2\b"), "voxcpm2"),
    (re.compile(r"복스\s*cpm\s*2|복스\s*씨피엠\s*(?:투|이|2)|복스씨피엠\s*(?:투|이|2)?"), "voxcpm2"),
    (re.compile(r"\bonyx\b|오닉스"), "onnx"),
    (re.compile(r"씨\s*피\s*유|씨피유"), "cpu"),
)


def normalize_for_asr_metric(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = re.sub(r"(?<=\d),(?=\d)", "", normalized)
    normalized = re.sub(r"(?<!\d)(0\d{1,2})[-\s]+(\d{3,4})[-\s]+(\d{4})(?=\D|$)", r"\1\2\3", normalized)
    normalized = re.sub(r"(\d+)만\s*(\d+)천\s*원", r"\1만\2천원", normalized)
    normalized = re.sub(r"([1-9])0{4}원", r"\1만원", normalized)
    normalized = re.sub(r"([1-9])([1-9])000원", r"\1만\2천원", normalized)
    normalized = re.sub(r"([가-힣]+구)\s+([가-힣]+대로)", r"\1\2", normalized)
    normalized = re.sub(r"\b3\s*번", "세 번", normalized)
    normalized = normalized.replace("%", "퍼센트")
    normalized = re.sub(r"\bpercent\b", "퍼센트", normalized)
    normalized = re.sub(r"(\d)\s*(퍼센트|프로)", r"\1 퍼센트", normalized)
    for pattern, replacement in _ASR_ALIAS_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    normalized = _PUNCT_RE.sub(" ", normalized)
    return _SPACE_RE.sub(" ", normalized).strip()


def character_error_rate(reference: str, hypothesis: str) -> dict[str, Any]:
    normalized_reference = normalize_for_asr_metric(reference).replace(" ", "")
    normalized_hypothesis = normalize_for_asr_metric(hypothesis).replace(" ", "")
    return _rate_payload(
        name="cer",
        reference=normalized_reference,
        hypothesis=normalized_hypothesis,
        distance=_levenshtein(list(normalized_reference), list(normalized_hypothesis)),
    )


def word_error_rate(reference: str, hypothesis: str) -> dict[str, Any]:
    normalized_reference = normalize_for_asr_metric(reference).split()
    normalized_hypothesis = normalize_for_asr_metric(hypothesis).split()
    return _rate_payload(
        name="wer",
        reference=normalized_reference,
        hypothesis=normalized_hypothesis,
        distance=_levenshtein(normalized_reference, normalized_hypothesis),
    )


def transcript_metrics(reference: str, hypothesis: str) -> dict[str, Any]:
    return {
        "reference": reference,
        "hypothesis": hypothesis,
        "normalized_reference": normalize_for_asr_metric(reference),
        "normalized_hypothesis": normalize_for_asr_metric(hypothesis),
        "cer": character_error_rate(reference, hypothesis),
        "wer": word_error_rate(reference, hypothesis),
    }


def _rate_payload(*, name: str, reference: Sequence[str], hypothesis: Sequence[str], distance: int) -> dict[str, Any]:
    reference_length = len(reference)
    hypothesis_length = len(hypothesis)
    rate = distance / reference_length if reference_length else 0.0 if hypothesis_length == 0 else 1.0
    return {
        "metric": name,
        "distance": distance,
        "reference_length": reference_length,
        "hypothesis_length": hypothesis_length,
        "rate": round(rate, 6),
        "percent": round(rate * 100, 3),
    }


def _levenshtein(reference: Sequence[str], hypothesis: Sequence[str]) -> int:
    if not reference:
        return len(hypothesis)
    if not hypothesis:
        return len(reference)

    previous = list(range(len(hypothesis) + 1))
    for row_index, reference_item in enumerate(reference, start=1):
        current = [row_index]
        for column_index, hypothesis_item in enumerate(hypothesis, start=1):
            substitution_cost = 0 if reference_item == hypothesis_item else 1
            current.append(
                min(
                    previous[column_index] + 1,
                    current[column_index - 1] + 1,
                    previous[column_index - 1] + substitution_cost,
                )
            )
        previous = current
    return previous[-1]
