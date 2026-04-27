from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_corrections(path: str | Path) -> dict[str, Any]:
    correction_path = Path(path)
    if not correction_path.exists():
        return {"terms": {}}
    with correction_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def add_term_correction(path: str | Path, source: str, preferred_reading: str) -> dict[str, Any]:
    data = load_corrections(path)
    data.setdefault("terms", {})[source] = preferred_reading
    with Path(path).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    return data

