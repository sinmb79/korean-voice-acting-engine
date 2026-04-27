from __future__ import annotations

import re

from kva_engine.schemas import NormalizationTrace


JOSA = ("으로", "로", "은", "는", "이", "가", "을", "를", "와", "과", "에", "에서", "에게", "께", "도", "만")
JOSA_RE = re.compile(r"([가-힣A-Za-z0-9]+)(" + "|".join(map(re.escape, JOSA)) + r")\b")


def has_final_consonant(text: str) -> bool:
    last = _last_hangul_syllable(text)
    if last is None:
        return False
    code = ord(last) - 0xAC00
    return code % 28 != 0


def ends_with_rieul(text: str) -> bool:
    last = _last_hangul_syllable(text)
    if last is None:
        return False
    code = ord(last) - 0xAC00
    return code % 28 == 8


def select_josa(reading: str, pair: str) -> str:
    if pair not in {"은/는", "이/가", "을/를", "과/와", "으로/로"}:
        raise ValueError(f"Unsupported josa pair: {pair}")
    first, second = pair.split("/")
    if pair == "으로/로" and ends_with_rieul(reading):
        return second
    return first if has_final_consonant(reading) else second


def join_josa(reading: str, pair: str) -> str:
    return reading + select_josa(reading, pair)


def trace_josa_after_terms(text: str, term_outputs: set[str] | None = None) -> list[NormalizationTrace]:
    traces: list[NormalizationTrace] = []
    for match in JOSA_RE.finditer(text):
        stem, josa = match.groups()
        if term_outputs is not None and stem not in term_outputs:
            continue
        if term_outputs is None and not any(char.isalpha() for char in stem):
            continue
        traces.append(
            NormalizationTrace(
                source=match.group(0),
                output=match.group(0),
                rule="josa_after_term",
                kind="josa",
            )
        )
    return traces


def _last_hangul_syllable(text: str) -> str | None:
    for char in reversed(text.strip()):
        if "가" <= char <= "힣":
            return char
    return None
