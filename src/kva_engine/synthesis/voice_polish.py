from __future__ import annotations

import datetime as dt
import json
import math
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from kva_engine.training.audio_features import analyze_wav
from kva_engine.voice_profile import load_voice_profile


@dataclass(frozen=True)
class VoicePolishPreset:
    name: str
    label: str
    highpass_hz: float
    lowpass_hz: float
    warmth_db: float
    clarity_db: float
    presence_db: float
    air_db: float
    de_ess_strength: float
    gate_threshold: float
    compression_drive: float
    target_peak: float
    silence_lift: float
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


POLISH_PRESETS: dict[str, VoicePolishPreset] = {
    "cleanup": VoicePolishPreset(
        name="cleanup",
        label="Clean natural voice",
        highpass_hz=72.0,
        lowpass_hz=10500.0,
        warmth_db=0.8,
        clarity_db=1.1,
        presence_db=0.8,
        air_db=0.2,
        de_ess_strength=0.12,
        gate_threshold=0.012,
        compression_drive=1.08,
        target_peak=0.86,
        silence_lift=0.35,
        description="Light cleanup that keeps the speaker close to the original recording.",
    ),
    "announcer": VoicePolishPreset(
        name="announcer",
        label="Korean announcer clarity",
        highpass_hz=88.0,
        lowpass_hz=11200.0,
        warmth_db=1.0,
        clarity_db=2.8,
        presence_db=2.2,
        air_db=0.8,
        de_ess_strength=0.26,
        gate_threshold=0.014,
        compression_drive=1.34,
        target_peak=0.9,
        silence_lift=0.45,
        description="Clear broadcast-style Korean speech with controlled body and forward consonants.",
    ),
    "shorts": VoicePolishPreset(
        name="shorts",
        label="Short-form punch",
        highpass_hz=96.0,
        lowpass_hz=10800.0,
        warmth_db=0.5,
        clarity_db=3.1,
        presence_db=2.7,
        air_db=0.6,
        de_ess_strength=0.3,
        gate_threshold=0.018,
        compression_drive=1.52,
        target_peak=0.92,
        silence_lift=0.62,
        description="Tighter, louder, more forward speech for shorts and social video narration.",
    ),
    "drama": VoicePolishPreset(
        name="drama",
        label="Drama dialogue",
        highpass_hz=64.0,
        lowpass_hz=9800.0,
        warmth_db=1.9,
        clarity_db=1.4,
        presence_db=0.9,
        air_db=0.25,
        de_ess_strength=0.18,
        gate_threshold=0.01,
        compression_drive=1.14,
        target_peak=0.86,
        silence_lift=0.22,
        description="Natural Korean dialogue polish with softer compression and preserved acting breath.",
    ),
    "documentary": VoicePolishPreset(
        name="documentary",
        label="Documentary narration",
        highpass_hz=70.0,
        lowpass_hz=10200.0,
        warmth_db=2.1,
        clarity_db=1.8,
        presence_db=1.2,
        air_db=0.35,
        de_ess_strength=0.2,
        gate_threshold=0.011,
        compression_drive=1.22,
        target_peak=0.88,
        silence_lift=0.3,
        description="Warm but clear long-form Korean narration for documentaries and explainers.",
    ),
}


def list_voice_polish_presets() -> list[dict[str, Any]]:
    return [preset.to_dict() for preset in POLISH_PRESETS.values()]


def polish_voice_file(
    *,
    input_path: str | Path,
    output_path: str | Path,
    preset: str = "announcer",
    voice_profile_path: str | Path | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(input_path)
    destination = Path(output_path)
    selected = _preset(preset)
    if not source.exists():
        return {"ok": False, "error": f"Input audio does not exist: {source}"}

    sample_rate, samples = _read_mono_wav(source)
    polished = _apply_polish(samples, sample_rate, selected)
    _write_mono_wav(destination, polished, sample_rate)

    audio = analyze_wav(destination)
    result = {
        "ok": bool(audio.get("exists")) and not bool(audio.get("error")),
        "job_id": _job_id(),
        "task": "voice_polish",
        "engine": "kva-korean-voice-polish-v1",
        "input_path": str(source),
        "output_path": str(destination),
        "preset": selected.to_dict(),
        "voice_profile": load_voice_profile(voice_profile_path),
        "audio": audio,
        "source_audio": analyze_wav(source) if source.suffix.lower() == ".wav" else {"path": str(source)},
        "safety": {
            "voice_identity_preserved": True,
            "not_a_new_speaker_or_child_voice": True,
            "private_voice_data_should_remain_local": True,
        },
        "note": (
            "KVAE polish keeps the source speaker identity. It improves clarity, level, tonal balance, "
            "and use-case fit; it does not claim to create a different actor, child, or creature voice."
        ),
    }
    if manifest_path:
        manifest = Path(manifest_path)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result["manifest_path"] = str(manifest)
    return result


def _apply_polish(samples: list[float], sample_rate: int, preset: VoicePolishPreset) -> list[float]:
    if not samples:
        return []
    output = _remove_dc(samples)
    output = _one_pole_highpass(output, sample_rate, preset.highpass_hz)
    output = _one_pole_lowpass(output, sample_rate, preset.lowpass_hz)
    output = _peaking_eq(output, sample_rate, frequency_hz=170.0, q=0.75, gain_db=preset.warmth_db)
    output = _peaking_eq(output, sample_rate, frequency_hz=1650.0, q=0.9, gain_db=preset.clarity_db)
    output = _peaking_eq(output, sample_rate, frequency_hz=3200.0, q=0.95, gain_db=preset.presence_db)
    output = _peaking_eq(output, sample_rate, frequency_hz=7200.0, q=1.1, gain_db=preset.air_db)
    output = _de_ess(output, sample_rate, preset.de_ess_strength)
    output = _soft_noise_floor(output, sample_rate, preset.gate_threshold, preset.silence_lift)
    output = _compress(output, drive=preset.compression_drive)
    return _normalize_peak(output, target_peak=preset.target_peak)


def _preset(name: str) -> VoicePolishPreset:
    if name not in POLISH_PRESETS:
        available = ", ".join(sorted(POLISH_PRESETS))
        raise ValueError(f"Unknown polish preset: {name}. Available presets: {available}")
    return POLISH_PRESETS[name]


def _de_ess(samples: list[float], sample_rate: int, strength: float) -> list[float]:
    if strength <= 0.0:
        return samples
    sibilance = _one_pole_highpass(samples, sample_rate, 5200.0)
    envelope = _envelope([abs(sample) for sample in sibilance], sample_rate, attack=0.002, release=0.035)
    output: list[float] = []
    for index, sample in enumerate(samples):
        reduction = _clamp(envelope[index] * strength * 4.5, 0.0, strength)
        output.append(sample - sibilance[index] * reduction)
    return output


def _soft_noise_floor(samples: list[float], sample_rate: int, threshold: float, silence_lift: float) -> list[float]:
    envelope = _envelope([abs(sample) for sample in samples], sample_rate, attack=0.006, release=0.12)
    output: list[float] = []
    for index, sample in enumerate(samples):
        if envelope[index] < threshold:
            gain = _clamp(silence_lift + envelope[index] / max(threshold, 0.000001) * (1.0 - silence_lift), 0.12, 1.0)
        else:
            gain = 1.0
        output.append(sample * gain)
    return output


def _compress(samples: list[float], *, drive: float) -> list[float]:
    if drive <= 1.0:
        return samples
    normalizer = math.tanh(drive)
    return [math.tanh(sample * drive) / normalizer for sample in samples]


def _envelope(samples: list[float], sample_rate: int, *, attack: float, release: float) -> list[float]:
    attack_coeff = _time_coeff(sample_rate, attack)
    release_coeff = _time_coeff(sample_rate, release)
    value = 0.0
    envelope: list[float] = []
    for sample in samples:
        value += (sample - value) * (attack_coeff if sample > value else release_coeff)
        envelope.append(value)
    return envelope


def _one_pole_lowpass(samples: list[float], sample_rate: int, cutoff_hz: float) -> list[float]:
    coeff = 1.0 - math.exp(-2.0 * math.pi * cutoff_hz / max(sample_rate, 1))
    state = 0.0
    output: list[float] = []
    for sample in samples:
        state += coeff * (sample - state)
        output.append(state)
    return output


def _one_pole_highpass(samples: list[float], sample_rate: int, cutoff_hz: float) -> list[float]:
    low = _one_pole_lowpass(samples, sample_rate, cutoff_hz)
    return [sample - low[index] for index, sample in enumerate(samples)]


def _peaking_eq(
    samples: list[float],
    sample_rate: int,
    *,
    frequency_hz: float,
    q: float,
    gain_db: float,
) -> list[float]:
    if not samples or abs(gain_db) < 0.05 or sample_rate <= 0:
        return samples
    frequency_hz = _clamp(frequency_hz, 20.0, sample_rate * 0.45)
    q = max(q, 0.05)
    amplitude = 10.0 ** (gain_db / 40.0)
    omega = 2.0 * math.pi * frequency_hz / sample_rate
    alpha = math.sin(omega) / (2.0 * q)
    cos_omega = math.cos(omega)
    b0 = 1.0 + alpha * amplitude
    b1 = -2.0 * cos_omega
    b2 = 1.0 - alpha * amplitude
    a0 = 1.0 + alpha / amplitude
    a1 = -2.0 * cos_omega
    a2 = 1.0 - alpha / amplitude
    b0 /= a0
    b1 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0
    x1 = x2 = y1 = y2 = 0.0
    output: list[float] = []
    for sample in samples:
        y0 = b0 * sample + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        output.append(y0)
        x2, x1 = x1, sample
        y2, y1 = y1, y0
    return output


def _normalize_peak(samples: list[float], *, target_peak: float) -> list[float]:
    centered = _remove_dc(samples)
    peak = max((abs(sample) for sample in centered), default=0.0)
    if peak <= 0.000001:
        return centered
    scale = target_peak / peak
    return [max(min(sample * scale, 0.98), -0.98) for sample in centered]


def _remove_dc(samples: list[float]) -> list[float]:
    if not samples:
        return []
    dc = sum(samples) / len(samples)
    return [sample - dc for sample in samples]


def _time_coeff(sample_rate: int, seconds: float) -> float:
    return 1.0 - math.exp(-1.0 / max(sample_rate * seconds, 1.0))


def _read_mono_wav(path: str | Path) -> tuple[int, list[float]]:
    wav_path = Path(path)
    with wave.open(str(wav_path), "rb") as reader:
        channels = reader.getnchannels()
        sample_width = reader.getsampwidth()
        sample_rate = reader.getframerate()
        frames = reader.readframes(reader.getnframes())
    max_abs = float(_max_abs_value(sample_width))
    samples: list[float] = []
    frame_width = sample_width * channels
    for offset in range(0, len(frames), frame_width):
        frame = frames[offset : offset + frame_width]
        if len(frame) < frame_width:
            break
        values = [
            _decode_pcm_sample(frame[channel * sample_width : (channel + 1) * sample_width], sample_width)
            for channel in range(channels)
        ]
        samples.append(sum(values) / (len(values) * max_abs))
    return sample_rate, samples


def _write_mono_wav(path: str | Path, samples: list[float], sample_rate: int) -> None:
    wav_path = Path(path)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(
            b"".join(
                int(max(min(sample, 0.98), -0.98) * 32767).to_bytes(2, "little", signed=True)
                for sample in samples
            )
        )


def _decode_pcm_sample(raw: bytes, sample_width: int) -> int:
    if sample_width == 1:
        return raw[0] - 128
    if sample_width == 3:
        sign_byte = b"\xff" if raw[-1] & 0x80 else b"\x00"
        return int.from_bytes(raw + sign_byte, "little", signed=True)
    if sample_width in (2, 4):
        return int.from_bytes(raw, "little", signed=True)
    raise wave.Error(f"unsupported sample width: {sample_width}")


def _max_abs_value(sample_width: int) -> int:
    if sample_width == 1:
        return 128
    return 2 ** (sample_width * 8 - 1)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _job_id() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
