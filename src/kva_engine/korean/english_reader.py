from __future__ import annotations

import re
from collections.abc import Mapping

from kva_engine.schemas import NormalizationTrace


DEFAULT_TERMS: dict[str, str] = {
    "22B Labs": "이십이비 랩스",
    "OpenAI": "오픈에이아이",
    "ChatGPT": "챗지피티",
    "Codex": "코덱스",
    "API": "에이피아이",
    "AI": "에이아이",
    "TTS": "티티에스",
    "STT": "에스티티",
    "ASR": "에이에스알",
    "JSON": "제이슨",
    "YAML": "야믈",
    "LoRA": "로라",
    "GPU": "지피유",
    "CPU": "씨피유",
    "CLI": "씨엘아이",
    "MVP": "엠브이피",
    "ONNX": "오닉스",
}

LETTER_NAMES: dict[str, str] = {
    "A": "에이",
    "B": "비",
    "C": "씨",
    "D": "디",
    "E": "이",
    "F": "에프",
    "G": "지",
    "H": "에이치",
    "I": "아이",
    "J": "제이",
    "K": "케이",
    "L": "엘",
    "M": "엠",
    "N": "엔",
    "O": "오",
    "P": "피",
    "Q": "큐",
    "R": "알",
    "S": "에스",
    "T": "티",
    "U": "유",
    "V": "브이",
    "W": "더블유",
    "X": "엑스",
    "Y": "와이",
    "Z": "지",
}

ASCII_TOKEN_RE = re.compile(r"(?<![A-Za-z])([A-Z]{2,})(?![A-Za-z])")
DOTTED_SPELLING_RE = re.compile(r"\b(?:[A-Za-z]\.){2,}")


def merge_terms(custom_terms: Mapping[str, str] | None = None) -> dict[str, str]:
    terms = dict(DEFAULT_TERMS)
    if custom_terms:
        terms.update({str(key): str(value) for key, value in custom_terms.items()})
    return terms


def spell_letters(token: str, *, separator: str = "") -> str:
    letters = [letter for letter in token.upper() if letter.isalpha()]
    return separator.join(LETTER_NAMES.get(letter, letter) for letter in letters)


def apply_english_terms(
    text: str,
    custom_terms: Mapping[str, str] | None = None,
) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []
    terms = merge_terms(custom_terms)

    for source, output in sorted(terms.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(re.escape(source), re.IGNORECASE)

        def replace(match: re.Match[str]) -> str:
            actual = match.group(0)
            traces.append(
                NormalizationTrace(
                    source=actual,
                    output=output,
                    rule="english_term_dictionary",
                    kind="term",
                )
            )
            return output

        text = pattern.sub(replace, text)

    return text, traces


def apply_dotted_spelling(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []

    def replace(match: re.Match[str]) -> str:
        source = match.group(0)
        output = spell_letters(source, separator=", ")
        traces.append(
            NormalizationTrace(
                source=source,
                output=output,
                rule="dotted_spelling",
                kind="spelling",
            )
        )
        return output

    return DOTTED_SPELLING_RE.sub(replace, text), traces


def apply_unknown_acronyms(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []

    def replace(match: re.Match[str]) -> str:
        source = match.group(1)
        output = spell_letters(source)
        traces.append(
            NormalizationTrace(
                source=source,
                output=output,
                rule="unknown_acronym_spelling",
                kind="spelling",
            )
        )
        return output

    return ASCII_TOKEN_RE.sub(replace, text), traces

