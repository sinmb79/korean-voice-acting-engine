from __future__ import annotations

from kva_engine.schemas import NormalizationTrace


SYMBOLS = {
    "&": "앤드",
    "@": "골뱅이",
    "#": "샵",
    "+": "플러스",
    "=": "는",
    "/": "슬래시",
    "\\": "역슬래시",
}


def normalize_symbols(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []
    for source, output in SYMBOLS.items():
        if source not in text:
            continue
        text = text.replace(source, f" {output} ")
        traces.append(
            NormalizationTrace(
                source=source,
                output=output,
                rule="symbol_dictionary",
                kind="symbol",
            )
        )
    return text, traces
