from __future__ import annotations

import re

from kva_engine.korean.number_reader import read_digits
from kva_engine.schemas import NormalizationTrace


TELEPHONE_RE = re.compile(r"(?<!\d)(\+82[-\s]?)?(0\d{1,2})[-\s]?(\d{3,4})[-\s]?(\d{4})(?!\d)")


def normalize_telephone(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []

    def replace(match: re.Match[str]) -> str:
        source = match.group(0)
        groups = [group for group in match.groups() if group and group.strip("- ")]
        output_parts: list[str] = []
        if groups and groups[0].startswith("+82"):
            output_parts.append("플러스 팔이")
            groups = groups[1:]
        output_parts.extend(read_digits(group, zero="공") for group in groups)
        output = ", ".join(output_parts)
        traces.append(
            NormalizationTrace(
                source=source,
                output=output,
                rule="telephone_digits",
                kind="number",
            )
        )
        return output

    return TELEPHONE_RE.sub(replace, text), traces
