from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from kva_engine.acting.vocal_tract import build_vocal_tract_design, build_vocal_tract_filter_chain


def normalize_wav_with_ffmpeg(
    input_path: str | Path,
    output_path: str | Path,
    *,
    integrated_loudness: int = -20,
    loudness_range: int = 11,
    true_peak: int = -2,
    sample_rate: int = 48000,
) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    input_wav = Path(input_path)
    output_wav = Path(output_path)
    if not ffmpeg:
        if input_wav != output_wav:
            shutil.copyfile(input_wav, output_wav)
        return {"applied": False, "reason": "ffmpeg_missing", "output": str(output_wav)}

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    filter_arg = f"loudnorm=I={integrated_loudness}:LRA={loudness_range}:TP={true_peak}"
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_wav),
        "-af",
        filter_arg,
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_wav),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "applied": completed.returncode == 0,
        "command": command,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "output": str(output_wav),
    }


def apply_role_audio_transform(
    input_path: str | Path,
    output_path: str | Path,
    role_controls: dict[str, Any],
    *,
    sample_rate: int = 48000,
) -> dict[str, Any]:
    ffmpeg = shutil.which("ffmpeg")
    input_wav = Path(input_path)
    output_wav = Path(output_path)
    if not ffmpeg:
        if input_wav != output_wav:
            shutil.copyfile(input_wav, output_wav)
        return {"applied": False, "reason": "ffmpeg_missing", "output": str(output_wav)}

    pitch_shift = float(role_controls.get("pitch_shift", 0.0) or 0.0)
    speed = float(role_controls.get("speed", 1.0) or 1.0)
    filters = _role_filter_chain(pitch_shift=pitch_shift, speed=speed, sample_rate=sample_rate)
    vocal_tract_filters = build_vocal_tract_filter_chain(str(role_controls.get("role", "")))
    filters.extend(vocal_tract_filters)
    character_filters = _character_filter_chain(str(role_controls.get("role", "")))
    filters.extend(character_filters)
    if not filters:
        if input_wav != output_wav:
            shutil.copyfile(input_wav, output_wav)
        return {"applied": False, "reason": "neutral_role_controls", "output": str(output_wav)}

    output_wav.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_wav),
        "-af",
        ",".join(filters),
        "-ar",
        str(sample_rate),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_wav),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "applied": completed.returncode == 0,
        "command": command,
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip(),
        "output": str(output_wav),
        "pitch_shift": pitch_shift,
        "speed": speed,
        "vocal_tract_effects": vocal_tract_filters,
        "vocal_tract_design": _vocal_tract_design_dict(str(role_controls.get("role", ""))),
        "character_effects": character_filters,
    }


def _role_filter_chain(*, pitch_shift: float, speed: float, sample_rate: int) -> list[str]:
    filters: list[str] = []
    pitch_factor = 2 ** (pitch_shift / 12.0)
    tempo_factor = speed
    if abs(pitch_shift) >= 0.01:
        filters.extend([f"asetrate={sample_rate}*{pitch_factor:.6f}", f"aresample={sample_rate}"])
        tempo_factor = speed / pitch_factor
    if abs(tempo_factor - 1.0) >= 0.01:
        filters.extend(f"atempo={part:.6f}" for part in _split_atempo(tempo_factor))
    return filters


def _split_atempo(factor: float) -> list[float]:
    parts: list[float] = []
    while factor > 2.0:
        parts.append(2.0)
        factor /= 2.0
    while factor < 0.5:
        parts.append(0.5)
        factor /= 0.5
    parts.append(factor)
    return parts


def _character_filter_chain(role: str) -> list[str]:
    if role == "wolf_growl_clear":
        return [
            "highpass=f=60",
            "lowpass=f=8200",
            "equalizer=f=120:t=q:w=1.0:g=3.5",
            "equalizer=f=380:t=q:w=1.0:g=2",
            "acrusher=bits=14:mix=0.08:mode=1:aa=0.75",
        ]
    if role == "wolf_growl":
        return [
            "highpass=f=55",
            "lowpass=f=7600",
            "equalizer=f=115:t=q:w=1.1:g=5",
            "equalizer=f=360:t=q:w=1.0:g=3",
            "acrusher=bits=13:mix=0.18:mode=1:aa=0.7",
            "tremolo=f=8:d=0.10",
            "aecho=0.8:0.22:42:0.22",
        ]
    if role == "wolf_growl_heavy":
        return [
            "highpass=f=50",
            "lowpass=f=6800",
            "equalizer=f=105:t=q:w=1.1:g=6",
            "equalizer=f=330:t=q:w=0.9:g=4",
            "acrusher=bits=11:mix=0.28:mode=1:aa=0.65",
            "tremolo=f=7:d=0.16",
            "aecho=0.85:0.30:55|95:0.28|0.16",
        ]
    if role == "monster_deep_clear":
        return [
            "highpass=f=50",
            "lowpass=f=7000",
            "equalizer=f=95:t=q:w=1.0:g=5",
            "equalizer=f=260:t=q:w=0.9:g=2.5",
            "acrusher=bits=13:mix=0.10:mode=1:aa=0.75",
            "aecho=0.8:0.18:52:0.16",
        ]
    if role == "monster_deep":
        return [
            "highpass=f=45",
            "lowpass=f=6200",
            "equalizer=f=90:t=q:w=1.0:g=7",
            "equalizer=f=240:t=q:w=0.9:g=4",
            "acrusher=bits=11:mix=0.24:mode=1:aa=0.65",
            "tremolo=f=5:d=0.12",
            "aecho=0.85:0.32:65|118:0.28|0.18",
        ]
    if role == "monster_deep_fx":
        return [
            "highpass=f=40",
            "lowpass=f=5400",
            "equalizer=f=80:t=q:w=1.0:g=8",
            "equalizer=f=220:t=q:w=0.8:g=5",
            "acrusher=bits=10:mix=0.32:mode=1:aa=0.55",
            "tremolo=f=4.5:d=0.18",
            "aecho=0.9:0.4:80|145:0.34|0.2",
        ]
    if role == "dinosaur_giant_clear":
        return [
            "highpass=f=40",
            "lowpass=f=6500",
            "equalizer=f=80:t=q:w=1.0:g=5.5",
            "equalizer=f=210:t=q:w=0.9:g=3",
            "acrusher=bits=13:mix=0.08:mode=1:aa=0.75",
            "aecho=0.84:0.20:70:0.18",
        ]
    if role == "dinosaur_giant":
        return [
            "highpass=f=35",
            "lowpass=f=5800",
            "equalizer=f=75:t=q:w=1.0:g=7",
            "equalizer=f=190:t=q:w=0.9:g=4",
            "acrusher=bits=12:mix=0.14:mode=1:aa=0.65",
            "tremolo=f=3.8:d=0.09",
            "aecho=0.88:0.30:85|160:0.25|0.16",
        ]
    if role == "dinosaur_giant_roar":
        return [
            "highpass=f=30",
            "lowpass=f=4500",
            "equalizer=f=60:t=q:w=1.0:g=10",
            "equalizer=f=150:t=q:w=0.8:g=6",
            "acrusher=bits=9:mix=0.34:mode=1:aa=0.5",
            "tremolo=f=3.2:d=0.22",
            "aecho=0.94:0.5:110|220:0.42|0.28",
        ]
    if role == "child_bright":
        return [
            "highpass=f=125",
            "equalizer=f=2800:t=q:w=1.0:g=2.5",
            "equalizer=f=5200:t=q:w=1.2:g=1.5",
        ]
    return []


def _vocal_tract_design_dict(role: str) -> dict[str, Any] | None:
    try:
        return build_vocal_tract_design(role).to_dict()
    except ValueError:
        return None
