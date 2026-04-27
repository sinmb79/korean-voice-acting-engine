from __future__ import annotations

from kva_engine.schemas import NormalizationTrace


PRONUNCIATION_OVERRIDES = {
    "국립": "궁닙",
    "신라": "실라",
    "읽는": "잉는",
    "읽다": "익따",
    "값이": "갑씨",
    "값은": "갑쓴",
    "같이": "가치",
    "많하": "마나",
    "합니다": "함니다",
    "입니다": "임니다",
    "습니다": "슴니다",
}


def plan_pronunciation(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []
    phoneme_text = text
    for source, output in PRONUNCIATION_OVERRIDES.items():
        if source not in phoneme_text:
            continue
        phoneme_text = phoneme_text.replace(source, output)
        traces.append(
            NormalizationTrace(
                source=source,
                output=output,
                rule="pronunciation_override",
                kind="pronunciation",
            )
        )
    return phoneme_text, traces
