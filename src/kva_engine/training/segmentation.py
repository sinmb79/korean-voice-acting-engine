from __future__ import annotations

import datetime as dt
import json
import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kva_engine.training.audio_features import analyze_wav


@dataclass(frozen=True)
class AudioSegment:
    index: int
    start_frame: int
    end_frame: int
    sample_rate: int

    @property
    def start_sec(self) -> float:
        return self.start_frame / self.sample_rate

    @property
    def end_sec(self) -> float:
        return self.end_frame / self.sample_rate

    @property
    def duration_sec(self) -> float:
        return (self.end_frame - self.start_frame) / self.sample_rate

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "start_sec": round(self.start_sec, 3),
            "end_sec": round(self.end_sec, 3),
            "duration_sec": round(self.duration_sec, 3),
        }


def split_wav_on_silence(
    *,
    audio_path: str | Path,
    output_dir: str | Path,
    transcript_path: str | Path | None = None,
    silence_threshold: float = 0.015,
    min_silence_ms: int = 450,
    min_segment_ms: int = 400,
    padding_ms: int = 80,
) -> dict[str, Any]:
    source = Path(audio_path)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    segments = detect_wav_segments(
        audio_path=source,
        silence_threshold=silence_threshold,
        min_silence_ms=min_silence_ms,
        min_segment_ms=min_segment_ms,
        padding_ms=padding_ms,
    )
    transcript_lines = _read_transcript_lines(transcript_path)
    warnings: list[str] = []
    if transcript_lines and len(transcript_lines) != len(segments):
        warnings.append("transcript_line_count_does_not_match_segments")
    if not segments:
        warnings.append("no_segments_detected_adjust_threshold_or_recording_level")

    output_segments = _write_segments(
        source=source,
        destination=destination,
        segments=segments,
        transcript_lines=transcript_lines,
    )
    manifest = {
        "job_id": _job_id(),
        "task": "split_recording",
        "source_audio": analyze_wav(source),
        "output_dir": str(destination),
        "transcript_path": str(transcript_path) if transcript_path else None,
        "config": {
            "silence_threshold": silence_threshold,
            "min_silence_ms": min_silence_ms,
            "min_segment_ms": min_segment_ms,
            "padding_ms": padding_ms,
        },
        "segments": output_segments,
        "segment_count": len(output_segments),
        "warnings": warnings,
        "next_steps": [
            "Review segment transcripts before training.",
            "Remove bad segments with clipping, noise, or incorrect transcript.",
            "Use reviewed segments for train/validation/test split.",
        ],
    }
    manifest_path = destination / "segments_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path)
    return manifest


def detect_wav_segments(
    *,
    audio_path: str | Path,
    silence_threshold: float = 0.015,
    min_silence_ms: int = 450,
    min_segment_ms: int = 400,
    padding_ms: int = 80,
) -> list[AudioSegment]:
    source = Path(audio_path)
    with wave.open(str(source), "rb") as reader:
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        sample_rate = reader.getframerate()
        frame_count = reader.getnframes()
        frames = reader.readframes(frame_count)

    chunk_frames = max(sample_rate // 50, 1)
    min_silence_frames = int(sample_rate * min_silence_ms / 1000)
    min_segment_frames = int(sample_rate * min_segment_ms / 1000)
    padding_frames = int(sample_rate * padding_ms / 1000)

    voiced_ranges: list[tuple[int, int]] = []
    in_segment = False
    segment_start = 0
    last_voiced_end = 0

    for start_frame in range(0, frame_count, chunk_frames):
        end_frame = min(start_frame + chunk_frames, frame_count)
        chunk = _slice_frames(frames, start_frame, end_frame, channels, sample_width)
        rms = _rms(chunk, sample_width)
        voiced = rms >= silence_threshold
        if voiced and not in_segment:
            segment_start = start_frame
            in_segment = True
        if voiced:
            last_voiced_end = end_frame
        if in_segment and not voiced and (start_frame - last_voiced_end) >= min_silence_frames:
            if (last_voiced_end - segment_start) >= min_segment_frames:
                voiced_ranges.append((segment_start, last_voiced_end))
            in_segment = False

    if in_segment and (last_voiced_end - segment_start) >= min_segment_frames:
        voiced_ranges.append((segment_start, last_voiced_end))

    padded = [
        (
            max(0, start - padding_frames),
            min(frame_count, end + padding_frames),
        )
        for start, end in voiced_ranges
    ]
    merged = _merge_ranges(padded, max_gap_frames=padding_frames)
    return [
        AudioSegment(index=index, start_frame=start, end_frame=end, sample_rate=sample_rate)
        for index, (start, end) in enumerate(merged, start=1)
        if (end - start) >= min_segment_frames
    ]


def _write_segments(
    *,
    source: Path,
    destination: Path,
    segments: list[AudioSegment],
    transcript_lines: list[str],
) -> list[dict[str, Any]]:
    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        frame_count = reader.getnframes()
        frames = reader.readframes(frame_count)

    results: list[dict[str, Any]] = []
    for segment in segments:
        segment_name = f"segment_{segment.index:04d}.wav"
        segment_path = destination / segment_name
        chunk = _slice_frames(frames, segment.start_frame, segment.end_frame, channels, sample_width)
        with wave.open(str(segment_path), "wb") as writer:
            writer.setparams(params)
            writer.writeframes(chunk)

        row = segment.to_dict()
        row["path"] = str(segment_path)
        row["file_name"] = segment_name
        row["transcript"] = transcript_lines[segment.index - 1] if segment.index <= len(transcript_lines) else None
        row["audio"] = analyze_wav(segment_path)
        results.append(row)
    return results


def _read_transcript_lines(path: str | Path | None) -> list[str]:
    if not path:
        return []
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def _slice_frames(frames: bytes, start_frame: int, end_frame: int, channels: int, sample_width: int) -> bytes:
    frame_size = channels * sample_width
    return frames[start_frame * frame_size : end_frame * frame_size]


def _rms(frames: bytes, sample_width: int) -> float:
    if not frames:
        return 0.0
    max_abs = float(_max_abs_value(sample_width))
    samples = list(_iter_pcm_samples(frames, sample_width))
    if not samples:
        return 0.0
    sum_squares = sum((sample / max_abs) ** 2 for sample in samples)
    return math.sqrt(sum_squares / len(samples))


def _iter_pcm_samples(frames: bytes, sample_width: int):
    for offset in range(0, len(frames), sample_width):
        raw = frames[offset : offset + sample_width]
        if len(raw) != sample_width:
            break
        if sample_width == 1:
            yield raw[0] - 128
        elif sample_width == 3:
            sign_byte = b"\xff" if raw[-1] & 0x80 else b"\x00"
            yield int.from_bytes(raw + sign_byte, "little", signed=True)
        elif sample_width in (2, 4):
            yield int.from_bytes(raw, "little", signed=True)
        else:
            raise wave.Error(f"unsupported sample width: {sample_width}")


def _max_abs_value(sample_width: int) -> int:
    if sample_width == 1:
        return 128
    return 2 ** (sample_width * 8 - 1)


def _merge_ranges(ranges: list[tuple[int, int]], *, max_gap_frames: int) -> list[tuple[int, int]]:
    if not ranges:
        return []
    merged: list[tuple[int, int]] = []
    current_start, current_end = ranges[0]
    for start, end in ranges[1:]:
        if start - current_end <= max_gap_frames:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    merged.append((current_start, current_end))
    return merged


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
