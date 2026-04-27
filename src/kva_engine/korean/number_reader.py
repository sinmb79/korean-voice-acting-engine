from __future__ import annotations

import re

from kva_engine.schemas import NormalizationTrace


SINO_DIGITS = ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
SMALL_UNITS = ["", "십", "백", "천"]
BIG_UNITS = ["", "만", "억", "조", "경"]
NATIVE_NUMBERS = {
    1: "한",
    2: "두",
    3: "세",
    4: "네",
    5: "다섯",
    6: "여섯",
    7: "일곱",
    8: "여덟",
    9: "아홉",
    10: "열",
    11: "열한",
    12: "열두",
    13: "열세",
    14: "열네",
    15: "열다섯",
    16: "열여섯",
    17: "열일곱",
    18: "열여덟",
    19: "열아홉",
    20: "스무",
}

COUNT_UNITS = {"개", "명", "번", "살", "권", "마리"}
SINO_UNIT_SUFFIXES = {
    "년",
    "월",
    "일",
    "분",
    "초",
    "원",
    "달러",
    "퍼센트",
    "단계",
    "배",
    "장",
    "절",
    "페이지",
}


def read_int_sino(value: int) -> str:
    if value == 0:
        return "영"
    if value < 0:
        return "마이너스 " + read_int_sino(abs(value))

    groups: list[str] = []
    group_index = 0
    while value > 0:
        group_value = value % 10000
        if group_value:
            group_text = "" if group_value == 1 and group_index > 0 else _read_under_10000(group_value)
            groups.append(group_text + BIG_UNITS[group_index])
        value //= 10000
        group_index += 1
    return "".join(reversed(groups))


def _read_under_10000(value: int) -> str:
    parts: list[str] = []
    digits = list(map(int, f"{value:04d}"))
    for index, digit in enumerate(digits):
        if digit == 0:
            continue
        unit_index = 3 - index
        if digit == 1 and unit_index > 0:
            parts.append(SMALL_UNITS[unit_index])
        else:
            parts.append(SINO_DIGITS[digit] + SMALL_UNITS[unit_index])
    return "".join(parts)


def read_int_native(value: int) -> str:
    if value in NATIVE_NUMBERS:
        return NATIVE_NUMBERS[value]
    return read_int_sino(value)


def read_digits(value: str, *, zero: str = "영", separator: str = "") -> str:
    digit_map = dict(zip("0123456789", [zero, "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]))
    return separator.join(digit_map.get(char, char) for char in value if char.isdigit())


def read_decimal(source: str) -> str:
    integer, fraction = source.split(".", 1)
    return f"{read_int_sino(int(integer))} 점 {read_digits(fraction, zero='영', separator=' ')}"


def read_number_with_unit(number: int, unit: str) -> str:
    if unit in COUNT_UNITS:
        return f"{read_int_native(number)} {unit}"
    return f"{read_int_sino(number)} {unit}"


def normalize_numbers(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []
    rules: list[tuple[re.Pattern[str], str, callable]] = [
        (re.compile(r"\b(0\d{1,2}-\d{3,4}-\d{4})\b"), "telephone", _replace_phone),
        (re.compile(r"\$([0-9][0-9,]*)"), "currency_usd", _replace_usd),
        (re.compile(r"\b[vV](\d+(?:\.\d+)+)([가-힣]*)"), "version_number", _replace_version),
        (re.compile(r"(\d+):(\d+)"), "score", _replace_score),
        (re.compile(r"(\d+)-(\d+)(단계|구간|회차)"), "range_with_unit", _replace_range),
        (re.compile(r"(\d{4})년"), "year", _replace_year),
        (re.compile(r"(\d{1,2})월\s*(\d{1,2})일"), "month_day", _replace_month_day),
        (re.compile(r"(\d{1,2})시\s*(?:(\d{1,2})분)?"), "time", _replace_time),
        (re.compile(r"(\d+)\.(\d+)([가-힣A-Za-z%]+)?"), "decimal", _replace_decimal),
        (re.compile(r"(\d+)(M)\b"), "million_suffix", _replace_million_suffix),
        (re.compile(r"(\d+)(%)"), "percent_symbol", _replace_percent_symbol),
        (re.compile(r"(\d+)([가-힣]+)"), "number_with_unit", _replace_number_with_unit),
        (re.compile(r"\b\d[\d,]*\b"), "integer", _replace_integer),
    ]

    for pattern, rule, callback in rules:

        def replace(match: re.Match[str], *, current_rule: str = rule, current_callback: callable = callback) -> str:
            source = match.group(0)
            output = current_callback(match)
            traces.append(
                NormalizationTrace(
                    source=source,
                    output=output,
                    rule=current_rule,
                    kind="number",
                )
            )
            return output

        text = pattern.sub(replace, text)

    return text, traces


def _clean_int(source: str) -> int:
    return int(source.replace(",", ""))


def _replace_phone(match: re.Match[str]) -> str:
    return " ".join(read_digits(part, zero="공") for part in match.group(1).split("-"))


def _replace_usd(match: re.Match[str]) -> str:
    return f"{read_int_sino(_clean_int(match.group(1)))} 달러"


def _replace_version(match: re.Match[str]) -> str:
    suffix = match.group(2) or ""
    return "버전 " + read_decimal(match.group(1)) + suffix


def _replace_score(match: re.Match[str]) -> str:
    return f"{read_int_sino(int(match.group(1)))} 대 {read_int_sino(int(match.group(2)))}"


def _replace_range(match: re.Match[str]) -> str:
    start, end, unit = match.groups()
    return f"{read_int_sino(int(start))}에서 {read_int_sino(int(end))} {unit}"


def _replace_year(match: re.Match[str]) -> str:
    return f"{read_int_sino(int(match.group(1)))} 년"


def _replace_month_day(match: re.Match[str]) -> str:
    month, day = match.groups()
    return f"{read_int_sino(int(month))}월 {read_int_sino(int(day))}일"


def _replace_time(match: re.Match[str]) -> str:
    hour = int(match.group(1))
    minute = match.group(2)
    hour_text = read_int_native(hour) if 1 <= hour <= 12 else read_int_sino(hour)
    if minute is None:
        return f"{hour_text} 시"
    return f"{hour_text} 시 {read_int_sino(int(minute))} 분"


def _replace_decimal(match: re.Match[str]) -> str:
    integer, fraction, unit = match.groups()
    output = read_decimal(f"{integer}.{fraction}")
    if unit:
        unit = "퍼센트" if unit == "%" else unit
        output = f"{output} {unit}"
    return output


def _replace_million_suffix(match: re.Match[str]) -> str:
    return f"{read_int_sino(int(match.group(1)))} 밀리언"


def _replace_percent_symbol(match: re.Match[str]) -> str:
    return f"{read_int_sino(int(match.group(1)))} 퍼센트"


def _replace_number_with_unit(match: re.Match[str]) -> str:
    number = _clean_int(match.group(1))
    unit = match.group(2)
    if unit in SINO_UNIT_SUFFIXES or unit in COUNT_UNITS:
        return read_number_with_unit(number, unit)
    return f"{read_int_sino(number)} {unit}"


def _replace_integer(match: re.Match[str]) -> str:
    return read_int_sino(_clean_int(match.group(0)))
