from __future__ import annotations

import re

from kva_engine.korean.number_reader import read_counter_number, read_int_sino
from kva_engine.schemas import NormalizationTrace


ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})[.-](\d{1,2})[.-](\d{1,2})(?!\d)")
FULL_DATE_RE = re.compile(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일")
MONTH_DAY_RE = re.compile(r"(?<!\d)(\d{1,2})월\s*(\d{1,2})일")
TIME_RE = re.compile(r"(?:(오전|오후)\s*)?(\d{1,2})시(?:\s*(\d{1,2})분)?(?:\s*(\d{1,2})초)?")
COLON_TIME_RE = re.compile(r"(?:(오전|오후)\s*)?(?<!\d)(\d{1,2}):(\d{2})(?::(\d{2}))?(?!\d)")


def normalize_datetime(text: str) -> tuple[str, list[NormalizationTrace]]:
    traces: list[NormalizationTrace] = []

    def apply(pattern: re.Pattern[str], rule: str, callback):
        nonlocal text

        def replace(match: re.Match[str]) -> str:
            source = match.group(0)
            output = callback(match)
            traces.append(
                NormalizationTrace(
                    source=source,
                    output=output,
                    rule=rule,
                    kind="number",
                )
            )
            return output

        text = pattern.sub(replace, text)

    apply(ISO_DATE_RE, "iso_date", _replace_ymd)
    apply(FULL_DATE_RE, "full_date", _replace_ymd)
    apply(MONTH_DAY_RE, "month_day", _replace_month_day)
    apply(TIME_RE, "time", _replace_time)
    apply(COLON_TIME_RE, "colon_time", _replace_colon_time)
    return text, traces


def _replace_ymd(match: re.Match[str]) -> str:
    year, month, day = match.groups()
    return f"{read_int_sino(int(year))}년 {read_int_sino(int(month))}월 {read_int_sino(int(day))}일"


def _replace_month_day(match: re.Match[str]) -> str:
    month, day = match.groups()
    return f"{read_int_sino(int(month))}월 {read_int_sino(int(day))}일"


def _replace_time(match: re.Match[str]) -> str:
    meridiem, hour, minute, second = match.groups()
    return _format_time(meridiem, hour, minute, second)


def _replace_colon_time(match: re.Match[str]) -> str:
    meridiem, hour, minute, second = match.groups()
    return _format_time(meridiem, hour, minute, second)


def _format_time(meridiem: str | None, hour: str, minute: str | None, second: str | None) -> str:
    hour_value = int(hour)
    hour_text = read_counter_number(hour_value) if 1 <= hour_value <= 12 else read_int_sino(hour_value)
    parts = []
    if meridiem:
        parts.append(meridiem)
    parts.append(f"{hour_text} 시")
    if minute is not None:
        parts.append(f"{read_int_sino(int(minute))} 분")
    if second is not None:
        parts.append(f"{read_int_sino(int(second))} 초")
    return " ".join(parts)
