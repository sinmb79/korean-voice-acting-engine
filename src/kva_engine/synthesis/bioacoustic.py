from __future__ import annotations

import math
import random
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BioacousticDinosaurControls:
    role: str
    mode: str
    closed_mouth_boom_hz: float
    throat_pulse_hz: float
    body_rumble_hz: float
    source_identity_mix: float
    breath_noise_mix: float
    grit_mix: float
    wideband_roar_mix: float
    pressure_drive: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "mode": self.mode,
            "closed_mouth_boom_hz": self.closed_mouth_boom_hz,
            "throat_pulse_hz": self.throat_pulse_hz,
            "body_rumble_hz": self.body_rumble_hz,
            "source_identity_mix": self.source_identity_mix,
            "breath_noise_mix": self.breath_noise_mix,
            "grit_mix": self.grit_mix,
            "wideband_roar_mix": self.wideband_roar_mix,
            "pressure_drive": self.pressure_drive,
        }


def build_bioacoustic_dinosaur_controls(role: str) -> BioacousticDinosaurControls:
    if role == "dinosaur_giant_roar":
        return BioacousticDinosaurControls(
            role=role,
            mode="closed_mouth_boom_plus_body_roar",
            closed_mouth_boom_hz=34.0,
            throat_pulse_hz=71.0,
            body_rumble_hz=22.0,
            source_identity_mix=0.0,
            breath_noise_mix=0.34,
            grit_mix=0.46,
            wideband_roar_mix=0.24,
            pressure_drive=1.35,
        )
    return BioacousticDinosaurControls(
        role=role,
        mode="large_reptile_boom_from_performance_envelope",
        closed_mouth_boom_hz=42.0,
        throat_pulse_hz=84.0,
        body_rumble_hz=28.0,
        source_identity_mix=0.0,
        breath_noise_mix=0.22,
        grit_mix=0.3,
        wideband_roar_mix=0.14,
        pressure_drive=1.05,
    )


def render_bioacoustic_dinosaur(
    input_wav: str | Path,
    output_wav: str | Path,
    *,
    role: str,
    seed: int = 2204,
) -> dict[str, Any]:
    controls = build_bioacoustic_dinosaur_controls(role)
    source = _read_mono_wav(input_wav)
    sample_rate = int(source["sample_rate_hz"])
    samples: list[float] = source["samples"]
    output = _synthesize_bioacoustic_dinosaur(samples, sample_rate, controls, seed=seed)
    _write_mono_wav(output_wav, output, sample_rate)
    return {
        "applied": True,
        "engine": "kva-bioacoustic-dinosaur-v3",
        "output": str(output_wav),
        "input": str(input_wav),
        "sample_rate_hz": sample_rate,
        "frame_count": len(output),
        "duration_sec": round(len(output) / sample_rate, 3) if sample_rate else 0.0,
        "controls": controls.to_dict(),
        "layering": {
            "performance_envelope": "source recording amplitude controls the nonhuman vocal body",
            "closed_mouth_boom": "low archosaur-inspired boom/hoot carrier",
            "body_rumble": "sub-bass chest and neck air-sac resonance",
            "throat_grit": "irregular pressure and rough airflow",
            "wideband_roar": "non-speech air tearing for audibility on small speakers",
            "source_identity": "removed from the audible signal; only timing and energy drive the render",
        },
    }


def _synthesize_bioacoustic_dinosaur(
    samples: list[float],
    sample_rate: int,
    controls: BioacousticDinosaurControls,
    *,
    seed: int,
) -> list[float]:
    rng = random.Random(seed)
    attack = _time_coeff(sample_rate, 0.012)
    release = _time_coeff(sample_rate, 0.18)
    rumble_release = _time_coeff(sample_rate, 0.42)
    source_lowpass = _time_coeff(sample_rate, 0.004)
    noise_lowpass = _time_coeff(sample_rate, 0.022)

    boom_phase = 0.0
    throat_phase = 0.0
    rumble_phase = 0.0
    envelope = 0.0
    rumble_envelope = 0.0
    source_body = 0.0
    noise_body = 0.0
    previous_noise = 0.0

    delay_a = [0.0] * max(int(sample_rate * 0.085), 1)
    delay_b = [0.0] * max(int(sample_rate * 0.19), 1)
    delay_c = [0.0] * max(int(sample_rate * 0.33), 1)
    delay_index_a = 0
    delay_index_b = 0
    delay_index_c = 0

    output: list[float] = []
    for index, sample in enumerate(samples):
        energy = abs(sample)
        envelope += (energy - envelope) * (attack if energy > envelope else release)
        rumble_envelope += (energy - rumble_envelope) * (attack if energy > rumble_envelope else rumble_release)
        drive = min(max(envelope * controls.pressure_drive, 0.0), 1.0)
        shaped = drive**0.45
        rumble_drive = min(max(rumble_envelope * controls.pressure_drive, 0.0), 1.0) ** 0.32

        source_body += (sample - source_body) * source_lowpass
        random_air = rng.uniform(-1.0, 1.0)
        noise_body += (random_air - noise_body) * noise_lowpass
        breath_noise = noise_body - previous_noise * 0.35
        wideband_air = (random_air - noise_body) * (0.4 + 0.6 * drive)
        previous_noise = noise_body

        slow_wobble = math.sin(2.0 * math.pi * 0.37 * index / sample_rate)
        pressure_wobble = 1.0 + 0.11 * slow_wobble + 0.08 * breath_noise

        boom_phase = _advance_phase(
            boom_phase,
            controls.closed_mouth_boom_hz * pressure_wobble,
            sample_rate,
        )
        throat_phase = _advance_phase(
            throat_phase,
            controls.throat_pulse_hz * (1.0 + 0.18 * slow_wobble + 0.12 * drive),
            sample_rate,
        )
        rumble_phase = _advance_phase(
            rumble_phase,
            controls.body_rumble_hz * (1.0 + 0.08 * slow_wobble),
            sample_rate,
        )

        closed_boom = (
            math.sin(boom_phase)
            + 0.42 * math.sin(boom_phase * 2.0 + 0.7)
            + 0.2 * math.sin(boom_phase * 3.0 + 1.4)
        )
        throat = math.tanh(
            2.8
            * (
                math.sin(throat_phase)
                + 0.48 * math.sin(throat_phase * 0.5)
                + 0.22 * math.sin(throat_phase * 1.5)
            )
        )
        rumble = math.sin(rumble_phase) + 0.32 * math.sin(rumble_phase * 1.7 + 0.9)

        dry = (
            closed_boom * shaped * 0.48
            + rumble * rumble_drive * 0.36
            + throat * shaped * controls.grit_mix
            + breath_noise * shaped * controls.breath_noise_mix
            + wideband_air * shaped * controls.wideband_roar_mix
            + source_body * shaped * controls.source_identity_mix
        )

        delayed = (
            dry
            + delay_a[delay_index_a] * 0.28
            + delay_b[delay_index_b] * 0.19
            + delay_c[delay_index_c] * 0.12
        )
        delay_a[delay_index_a] = dry
        delay_b[delay_index_b] = dry
        delay_c[delay_index_c] = dry
        delay_index_a = (delay_index_a + 1) % len(delay_a)
        delay_index_b = (delay_index_b + 1) % len(delay_b)
        delay_index_c = (delay_index_c + 1) % len(delay_c)

        output.append(math.tanh(delayed * 1.2) * 0.88)

    return _normalize_peak(output, target_peak=0.88)


def _advance_phase(phase: float, frequency_hz: float, sample_rate: int) -> float:
    next_phase = phase + (2.0 * math.pi * frequency_hz / sample_rate)
    return math.fmod(next_phase, 2.0 * math.pi)


def _time_coeff(sample_rate: int, seconds: float) -> float:
    return 1.0 - math.exp(-1.0 / max(sample_rate * seconds, 1.0))


def _normalize_peak(samples: list[float], *, target_peak: float) -> list[float]:
    if not samples:
        return samples
    dc_offset = sum(samples) / len(samples)
    centered = [sample - dc_offset for sample in samples]
    peak = max((abs(sample) for sample in centered), default=0.0)
    if peak <= 0.000001:
        return centered
    scale = target_peak / peak
    return [max(min(sample * scale, 0.98), -0.98) for sample in centered]


def _read_mono_wav(path: str | Path) -> dict[str, Any]:
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
        channel_values = [
            _decode_pcm_sample(frame[channel * sample_width : (channel + 1) * sample_width], sample_width)
            for channel in range(channels)
        ]
        samples.append(sum(channel_values) / (len(channel_values) * max_abs))

    return {"sample_rate_hz": sample_rate, "samples": samples}


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
