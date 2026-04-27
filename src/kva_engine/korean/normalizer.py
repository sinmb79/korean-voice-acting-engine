from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from kva_engine.korean.english_reader import (
    apply_dotted_spelling,
    apply_english_terms,
    apply_unknown_acronyms,
)
from kva_engine.korean.number_reader import normalize_numbers
from kva_engine.korean.pronunciation import plan_pronunciation
from kva_engine.korean.prosody import split_phrases
from kva_engine.korean.symbol_reader import normalize_symbols
from kva_engine.schemas import NormalizationTrace, SpeechScript, SpeechToken


WHITESPACE_RE = re.compile(r"\s+")
ASCII_LEFTOVER_RE = re.compile(r"[A-Za-z0-9$%]")


def load_pronunciation_dict(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def normalize_text(
    display_text: str,
    *,
    pronunciation_dict: dict[str, Any] | None = None,
) -> SpeechScript:
    pronunciation_dict = pronunciation_dict or {}
    custom_terms = pronunciation_dict.get("terms", {})
    traces: list[NormalizationTrace] = []

    speech_text = display_text
    speech_text, new_traces = apply_dotted_spelling(speech_text)
    traces.extend(new_traces)
    speech_text, new_traces = apply_english_terms(speech_text, custom_terms=custom_terms)
    traces.extend(new_traces)
    speech_text, new_traces = normalize_symbols(speech_text)
    traces.extend(new_traces)
    speech_text, new_traces = normalize_numbers(speech_text)
    traces.extend(new_traces)
    speech_text, new_traces = apply_unknown_acronyms(speech_text)
    traces.extend(new_traces)

    speech_text = _clean_spacing(speech_text)
    phoneme_text, pronunciation_traces = plan_pronunciation(speech_text)
    traces.extend(pronunciation_traces)

    warnings = _build_warnings(speech_text)
    return SpeechScript(
        display_text=display_text,
        speech_text=speech_text,
        phoneme_text=phoneme_text,
        tokens=_tokens_from_traces(traces),
        phrases=split_phrases(speech_text),
        normalization_trace=traces,
        warnings=warnings,
    )


def normalize_file(path: str | Path, *, pronunciation_dict: dict[str, Any] | None = None) -> SpeechScript:
    text = Path(path).read_text(encoding="utf-8")
    return normalize_text(text.strip(), pronunciation_dict=pronunciation_dict)


def _clean_spacing(text: str) -> str:
    text = WHITESPACE_RE.sub(" ", text)
    text = text.replace(" .", ".").replace(" ,", ",").replace(" ?", "?").replace(" !", "!")
    return text.strip()


def _tokens_from_traces(traces: list[NormalizationTrace]) -> list[SpeechToken]:
    return [
        SpeechToken(
            text=trace.output,
            source=trace.source,
            kind=trace.kind,
            say_as=trace.rule if trace.kind in {"number", "spelling"} else None,
        )
        for trace in traces
        if trace.kind != "pronunciation"
    ]


def _build_warnings(speech_text: str) -> list[str]:
    warnings: list[str] = []
    if ASCII_LEFTOVER_RE.search(speech_text):
        warnings.append("ascii_leftover_requires_review")
    if len(speech_text.split()) <= 3:
        warnings.append("very_short_input_may_be_unstable")
    return warnings

