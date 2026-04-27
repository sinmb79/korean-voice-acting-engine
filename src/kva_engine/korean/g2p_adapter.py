from __future__ import annotations

from kva_engine.korean.pronunciation import plan_pronunciation
from kva_engine.schemas import NormalizationTrace


G2P_MODES = {"rules", "external", "auto"}


def apply_g2p(text: str, *, mode: str = "rules") -> tuple[str, list[NormalizationTrace], list[str]]:
    if mode not in G2P_MODES:
        raise ValueError(f"Unsupported g2p mode: {mode}")
    if mode in {"external", "auto"}:
        external = _try_g2pk(text)
        if external is not None:
            output, traces = external
            return output, traces, []
        if mode == "external":
            return text, [], ["g2pk_not_available"]

    output, traces = plan_pronunciation(text)
    return output, traces, []


def _try_g2pk(text: str) -> tuple[str, list[NormalizationTrace]] | None:
    try:
        from g2pk import G2p  # type: ignore
    except Exception:
        return None

    g2p = G2p()
    output = g2p(text)
    return (
        output,
        [
            NormalizationTrace(
                source=text,
                output=output,
                rule="g2pk_external",
                kind="pronunciation",
            )
        ],
    )
