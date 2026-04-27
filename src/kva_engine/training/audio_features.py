from __future__ import annotations

import hashlib
import math
import wave
from pathlib import Path
from typing import Any


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def analyze_wav(path: str | Path) -> dict[str, Any]:
    wav_path = Path(path)
    analysis: dict[str, Any] = {
        "path": str(wav_path),
        "file_name": wav_path.name,
        "exists": wav_path.exists(),
        "format": "wav",
    }
    if not wav_path.exists():
        analysis["error"] = "missing_file"
        return analysis

    analysis["file_size_bytes"] = wav_path.stat().st_size
    analysis["sha256"] = sha256_file(wav_path)

    try:
        with wave.open(str(wav_path), "rb") as reader:
            channels = reader.getnchannels()
            sample_width = reader.getsampwidth()
            sample_rate = reader.getframerate()
            frame_count = reader.getnframes()

            stats = _stream_pcm_stats(
                reader=reader,
                sample_width=sample_width,
                sample_rate=sample_rate,
                channels=channels,
            )
    except wave.Error as exc:
        analysis["error"] = f"invalid_wav:{exc}"
        return analysis

    duration_sec = frame_count / sample_rate if sample_rate else 0.0
    sample_count = max(frame_count * channels, 1)
    rms = math.sqrt(stats["sum_squares"] / sample_count)

    analysis.update(
        {
            "sample_rate_hz": sample_rate,
            "channels": channels,
            "sample_width_bytes": sample_width,
            "frame_count": frame_count,
            "duration_sec": round(duration_sec, 3),
            "sample_count": stats["sample_count"],
            "rms": round(rms, 6),
            "peak": round(stats["peak"], 6),
            "dc_offset": round(stats["sum_values"] / sample_count, 6),
            "zero_crossing_rate": round(
                stats["zero_crossings"] / max(stats["sample_count"] - 1, 1),
                6,
            ),
            "silence_ratio": round(
                stats["silent_chunks"] / max(stats["chunk_count"], 1),
                6,
            ),
        }
    )
    return analysis


def _stream_pcm_stats(
    *,
    reader: wave.Wave_read,
    sample_width: int,
    sample_rate: int,
    channels: int,
) -> dict[str, float | int]:
    chunk_frames = max(sample_rate // 20, 1)
    max_abs = float(_max_abs_value(sample_width))

    sum_squares = 0.0
    sum_values = 0.0
    sample_count = 0
    peak = 0.0
    zero_crossings = 0
    previous_sign = 0
    chunk_count = 0
    silent_chunks = 0

    while True:
        frames = reader.readframes(chunk_frames)
        if not frames:
            break
        chunk_count += 1
        chunk_sum_squares = 0.0
        chunk_sample_count = 0

        for sample in _iter_pcm_samples(frames, sample_width):
            normalized = sample / max_abs
            abs_normalized = abs(normalized)
            peak = max(peak, abs_normalized)
            sum_values += normalized
            sum_squares += normalized * normalized
            chunk_sum_squares += normalized * normalized
            sample_count += 1
            chunk_sample_count += 1

            sign = 1 if sample > 0 else -1 if sample < 0 else 0
            if sign and previous_sign and sign != previous_sign:
                zero_crossings += 1
            if sign:
                previous_sign = sign

        chunk_rms = math.sqrt(chunk_sum_squares / max(chunk_sample_count, 1))
        if chunk_rms < 0.01:
            silent_chunks += 1

    return {
        "sum_squares": sum_squares,
        "sum_values": sum_values,
        "sample_count": sample_count,
        "peak": min(peak, 1.0),
        "zero_crossings": zero_crossings,
        "chunk_count": chunk_count,
        "silent_chunks": silent_chunks,
    }


def _iter_pcm_samples(frames: bytes, sample_width: int):
    if sample_width not in (1, 2, 3, 4):
        raise wave.Error(f"unsupported sample width: {sample_width}")

    for offset in range(0, len(frames), sample_width):
        raw = frames[offset : offset + sample_width]
        if len(raw) != sample_width:
            break
        if sample_width == 1:
            yield raw[0] - 128
        elif sample_width == 3:
            sign_byte = b"\xff" if raw[-1] & 0x80 else b"\x00"
            yield int.from_bytes(raw + sign_byte, "little", signed=True)
        else:
            yield int.from_bytes(raw, "little", signed=True)


def _max_abs_value(sample_width: int) -> int:
    if sample_width == 1:
        return 128
    return 2 ** (sample_width * 8 - 1)

