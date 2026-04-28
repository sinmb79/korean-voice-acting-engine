from __future__ import annotations

import math
import random
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kva_engine.acting.presets import get_preset
from kva_engine.acting.vocal_tract import build_vocal_tract_design
from kva_engine.synthesis.bioacoustic import render_bioacoustic_dinosaur


@dataclass(frozen=True)
class NativeCharacterControls:
    role: str
    mode: str
    pitch_ratio: float
    tempo_ratio: float
    formant_shift_ratio: float
    spectral_tilt_db: float
    roughness: float
    breath_noise: float
    subharmonic_mix: float
    articulation_precision: float
    source_identity_mix: float
    character_mix: float
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "mode": self.mode,
            "pitch_ratio": self.pitch_ratio,
            "tempo_ratio": self.tempo_ratio,
            "formant_shift_ratio": self.formant_shift_ratio,
            "spectral_tilt_db": self.spectral_tilt_db,
            "roughness": self.roughness,
            "breath_noise": self.breath_noise,
            "subharmonic_mix": self.subharmonic_mix,
            "articulation_precision": self.articulation_precision,
            "source_identity_mix": self.source_identity_mix,
            "character_mix": self.character_mix,
            "notes": list(self.notes),
        }


def build_native_character_controls(role: str, *, intensity: float = 1.0) -> NativeCharacterControls:
    preset = get_preset(role)
    design = build_vocal_tract_design(role, intensity=intensity)
    identity = preset.identity_strength * (1.0 - preset.role_strength * 0.28)
    notes = [
        "source_filter_controls_rendered_inside_kvae_without_ffmpeg",
        "source_performance_timing_and_energy_drive_the_character",
    ]
    mode = "source_filter_character_voice"

    if role.startswith("dinosaur_"):
        identity = 0.0
        mode = "bioacoustic_nonhuman_body"
        notes.append("audible_source_speaker_identity_removed")
    elif role.startswith(("wolf_", "monster_")):
        identity *= 0.55
        notes.append("creature_roles_reduce_human_identity_anchor")
    elif role == "twentyfirst_grand_lady_lead":
        identity *= 0.82
        notes.append("high_distance_original_female_lead_from_male_source_reference")

    source_identity_mix = round(_clamp(identity, 0.0, 0.86), 6)
    character_mix = round(1.0 - source_identity_mix, 6)

    return NativeCharacterControls(
        role=role,
        mode=mode,
        pitch_ratio=round(design.source.pitch_ratio, 6),
        tempo_ratio=round(design.performance.tempo_ratio, 6),
        formant_shift_ratio=round(design.filter.formant_shift_ratio, 6),
        spectral_tilt_db=round(design.filter.spectral_tilt_db, 6),
        roughness=round(design.source.roughness, 6),
        breath_noise=round(design.source.breath_noise, 6),
        subharmonic_mix=round(design.source.subharmonic_mix, 6),
        articulation_precision=round(design.articulation.consonant_precision, 6),
        source_identity_mix=source_identity_mix,
        character_mix=character_mix,
        notes=notes,
    )


def render_native_character_voice(
    input_wav: str | Path,
    output_wav: str | Path,
    *,
    role: str,
    seed: int = 2204,
    intensity: float = 1.0,
    normalize: bool = True,
) -> dict[str, Any]:
    controls = build_native_character_controls(role, intensity=intensity)
    input_path = Path(input_wav)
    output_path = Path(output_wav)

    if role.startswith("dinosaur_"):
        dinosaur = render_bioacoustic_dinosaur(input_path, output_path, role=role, seed=seed)
        layering = dict(dinosaur.get("layering") or {})
        layering["external_audio_tool"] = "not_used"
        return {
            "applied": True,
            "engine": "kva-native-character-v1",
            "sub_engine": dinosaur.get("engine"),
            "output": str(output_path),
            "input": str(input_path),
            "sample_rate_hz": dinosaur.get("sample_rate_hz"),
            "frame_count": dinosaur.get("frame_count"),
            "duration_sec": dinosaur.get("duration_sec"),
            "controls": controls.to_dict(),
            "native_normalization": "bioacoustic_peak_normalized",
            "theory": _theory_note(role),
            "layering": layering,
        }

    source = _read_mono_wav(input_path)
    sample_rate = int(source["sample_rate_hz"])
    samples: list[float] = source["samples"]
    design = build_vocal_tract_design(role, intensity=intensity)

    character = _render_source_filter_character(samples, sample_rate, role=role, controls=controls, seed=seed)
    anchor = _resample_to_length(samples, len(character))
    mixed = _mix_character_and_identity(character, anchor, controls)
    mixed = _apply_role_signature(mixed, sample_rate, role=role, controls=controls, seed=seed)
    output = _normalize_peak(mixed, target_peak=0.88) if normalize else _limit(mixed)
    _write_mono_wav(output_path, output, sample_rate)

    return {
        "applied": True,
        "engine": "kva-native-character-v1",
        "output": str(output_path),
        "input": str(input_path),
        "sample_rate_hz": sample_rate,
        "frame_count": len(output),
        "duration_sec": round(len(output) / sample_rate, 3) if sample_rate else 0.0,
        "controls": controls.to_dict(),
        "vocal_tract_design": design.to_dict(),
        "native_normalization": "peak" if normalize else "disabled",
        "theory": _theory_note(role),
        "layering": {
            "pitch_and_tempo": "linear-resampled glottal source branch",
            "vocal_tract": "in-engine formant peak filters and spectral tilt",
            "source_texture": "breath, roughness, subharmonic body, and saturation",
            "identity_mix": "explicit source identity anchor blended after character rendering",
            "external_audio_tool": "not_used",
        },
    }


def _render_source_filter_character(
    samples: list[float],
    sample_rate: int,
    *,
    role: str,
    controls: NativeCharacterControls,
    seed: int,
) -> list[float]:
    pitch_tempo_ratio = _clamp(controls.pitch_ratio * (controls.tempo_ratio**0.35), 0.55, 1.55)
    voiced = _resample_by_ratio(samples, pitch_tempo_ratio)
    voiced = _one_pole_highpass(
        voiced,
        sample_rate,
        45.0 if controls.formant_shift_ratio < 0.76 else 70.0,
    )
    voiced = _one_pole_lowpass(
        voiced,
        sample_rate,
        _clamp(9400.0 * controls.formant_shift_ratio, 3600.0, 11800.0),
    )
    voiced = _apply_formant_model(voiced, sample_rate, role=role)
    voiced = _apply_spectral_tilt(voiced, sample_rate, controls.spectral_tilt_db)
    voiced = _apply_articulation(voiced, sample_rate, controls.articulation_precision)
    return _apply_source_texture(voiced, sample_rate, controls=controls, role=role, seed=seed)


def _apply_formant_model(samples: list[float], sample_rate: int, *, role: str) -> list[float]:
    design = build_vocal_tract_design(role)
    output = list(samples)
    for formant in design.formants:
        gain = float(formant["gain_db"]) * (1.0 + design.performance.character_distance * 0.85)
        frequency = float(formant["frequency_hz"])
        bandwidth = max(float(formant["bandwidth_hz"]), 1.0)
        q = _clamp(frequency / bandwidth, 0.35, 12.0)
        output = _peaking_eq(output, sample_rate, frequency_hz=frequency, q=q, gain_db=gain)
    return output


def _apply_spectral_tilt(samples: list[float], sample_rate: int, tilt_db: float) -> list[float]:
    output = list(samples)
    if tilt_db < -0.25:
        output = _peaking_eq(output, sample_rate, frequency_hz=145.0, q=0.8, gain_db=abs(tilt_db) * 0.75)
        output = _peaking_eq(output, sample_rate, frequency_hz=3600.0, q=0.9, gain_db=tilt_db * 0.65)
        output = _one_pole_lowpass(output, sample_rate, _clamp(8200.0 + tilt_db * 250.0, 4200.0, 9000.0))
    elif tilt_db > 0.25:
        output = _peaking_eq(output, sample_rate, frequency_hz=2400.0, q=0.9, gain_db=tilt_db * 0.55)
        output = _peaking_eq(output, sample_rate, frequency_hz=5600.0, q=1.1, gain_db=tilt_db * 0.35)
        output = _one_pole_highpass(output, sample_rate, 95.0)
    return output


def _apply_articulation(samples: list[float], sample_rate: int, precision: float) -> list[float]:
    if precision >= 0.75:
        transient = _one_pole_highpass(samples, sample_rate, 1900.0)
        return [sample + transient[index] * _clamp((precision - 0.75) * 0.7, 0.0, 0.18) for index, sample in enumerate(samples)]
    if precision <= 0.5:
        return _one_pole_lowpass(samples, sample_rate, _clamp(5200.0 + precision * 3600.0, 4800.0, 7200.0))
    return samples


def _apply_source_texture(
    samples: list[float],
    sample_rate: int,
    *,
    controls: NativeCharacterControls,
    role: str,
    seed: int,
) -> list[float]:
    rng = random.Random(seed + sum(ord(char) for char in role))
    attack = _time_coeff(sample_rate, 0.006)
    release = _time_coeff(sample_rate, 0.09)
    breath_smooth = _time_coeff(sample_rate, 0.018)
    envelope = 0.0
    breath_state = 0.0
    output: list[float] = []
    base_body_hz = _body_frequency(role)
    body_phase = 0.0

    for index, sample in enumerate(samples):
        energy = abs(sample)
        envelope += (energy - envelope) * (attack if energy > envelope else release)
        random_air = rng.uniform(-1.0, 1.0)
        breath_state += (random_air - breath_state) * breath_smooth
        breath = (random_air - breath_state * 0.35) * (envelope**0.62) * controls.breath_noise * 0.22

        rough_lfo = math.sin(2.0 * math.pi * (22.0 + controls.roughness * 34.0) * index / sample_rate)
        pressure = 1.0 + controls.roughness * 0.16 * rough_lfo + rng.uniform(-0.04, 0.04) * controls.roughness
        body_phase = _advance_phase(body_phase, base_body_hz * (1.0 + rough_lfo * 0.035), sample_rate)
        body = math.sin(body_phase) * (envelope**0.74) * controls.subharmonic_mix * 0.42
        textured = sample * pressure + breath + body
        if controls.roughness >= 0.18:
            drive = 1.0 + controls.roughness * 3.4
            textured = math.tanh(textured * drive) / math.tanh(drive)
        output.append(textured)
    return output


def _apply_role_signature(
    samples: list[float],
    sample_rate: int,
    *,
    role: str,
    controls: NativeCharacterControls,
    seed: int,
) -> list[float]:
    output = list(samples)
    if role == "twentyfirst_prince_lead":
        output = _add_body_resonance(output, sample_rate, frequency_hz=92.0, amount=0.16)
        output = _soft_compress(output, drive=1.18)
        return _short_delay(output, sample_rate, delay_ms=42.0, feedback=0.08)
    if role == "twentyfirst_grand_lady_lead":
        output = _peaking_eq(output, sample_rate, frequency_hz=3100.0, q=1.0, gain_db=2.8)
        output = _add_air(output, sample_rate, amount=0.035, seed=seed + 17)
        return _soft_compress(output, drive=1.08)
    if role.startswith("child"):
        output = _peaking_eq(output, sample_rate, frequency_hz=3800.0, q=1.2, gain_db=3.2)
        return _add_air(output, sample_rate, amount=0.018, seed=seed + 23)
    if role.startswith("wolf_"):
        output = _add_body_resonance(output, sample_rate, frequency_hz=68.0, amount=0.25)
        output = _throat_pulse(output, sample_rate, frequency_hz=39.0, amount=0.18)
        return _short_delay(output, sample_rate, delay_ms=28.0, feedback=0.12)
    if role.startswith("monster_"):
        output = _add_body_resonance(output, sample_rate, frequency_hz=46.0, amount=0.34)
        output = _throat_pulse(output, sample_rate, frequency_hz=31.0, amount=0.24)
        output = _short_delay(output, sample_rate, delay_ms=76.0, feedback=0.16)
        return _soft_compress(output, drive=1.55 + controls.roughness)
    return output


def _mix_character_and_identity(
    character: list[float],
    anchor: list[float],
    controls: NativeCharacterControls,
) -> list[float]:
    identity = controls.source_identity_mix
    character_gain = controls.character_mix
    return [
        character[index] * character_gain + anchor[index] * identity * 0.72
        for index in range(min(len(character), len(anchor)))
    ]


def _add_body_resonance(samples: list[float], sample_rate: int, *, frequency_hz: float, amount: float) -> list[float]:
    envelope = _envelope(samples, sample_rate)
    phase = 0.0
    output: list[float] = []
    for index, sample in enumerate(samples):
        phase = _advance_phase(phase, frequency_hz, sample_rate)
        output.append(sample + math.sin(phase) * (envelope[index] ** 0.7) * amount)
    return output


def _throat_pulse(samples: list[float], sample_rate: int, *, frequency_hz: float, amount: float) -> list[float]:
    output: list[float] = []
    for index, sample in enumerate(samples):
        pulse = 0.5 + 0.5 * math.sin(2.0 * math.pi * frequency_hz * index / sample_rate)
        output.append(sample * (1.0 + amount * (pulse**3 - 0.5)))
    return output


def _add_air(samples: list[float], sample_rate: int, *, amount: float, seed: int) -> list[float]:
    rng = random.Random(seed)
    envelope = _envelope(samples, sample_rate)
    state = 0.0
    coeff = _time_coeff(sample_rate, 0.006)
    output: list[float] = []
    for index, sample in enumerate(samples):
        noise = rng.uniform(-1.0, 1.0)
        state += (noise - state) * coeff
        output.append(sample + (noise - state) * amount * (envelope[index] ** 0.5))
    return output


def _short_delay(samples: list[float], sample_rate: int, *, delay_ms: float, feedback: float) -> list[float]:
    delay_frames = max(int(sample_rate * delay_ms / 1000.0), 1)
    buffer = [0.0] * delay_frames
    index = 0
    output: list[float] = []
    for sample in samples:
        delayed = buffer[index]
        mixed = sample + delayed * feedback
        buffer[index] = mixed
        index = (index + 1) % delay_frames
        output.append(mixed)
    return output


def _soft_compress(samples: list[float], *, drive: float) -> list[float]:
    normalizer = math.tanh(max(drive, 1.0))
    return [math.tanh(sample * drive) / normalizer for sample in samples]


def _body_frequency(role: str) -> float:
    if role.startswith("monster_"):
        return 44.0
    if role.startswith("wolf_"):
        return 67.0
    if role == "twentyfirst_prince_lead":
        return 92.0
    if role == "twentyfirst_grand_lady_lead":
        return 176.0
    if role.startswith("child"):
        return 220.0
    return 110.0


def _envelope(samples: list[float], sample_rate: int) -> list[float]:
    attack = _time_coeff(sample_rate, 0.008)
    release = _time_coeff(sample_rate, 0.16)
    value = 0.0
    envelope: list[float] = []
    for sample in samples:
        energy = abs(sample)
        value += (energy - value) * (attack if energy > value else release)
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


def _resample_by_ratio(samples: list[float], ratio: float) -> list[float]:
    if not samples:
        return []
    new_length = max(int(len(samples) / max(ratio, 0.001)), 1)
    return _resample_to_length(samples, new_length)


def _resample_to_length(samples: list[float], target_length: int) -> list[float]:
    if not samples or target_length <= 0:
        return []
    if len(samples) == 1:
        return [samples[0]] * target_length
    if target_length == len(samples):
        return list(samples)

    scale = (len(samples) - 1) / max(target_length - 1, 1)
    output: list[float] = []
    for index in range(target_length):
        source_position = index * scale
        left = int(source_position)
        right = min(left + 1, len(samples) - 1)
        fraction = source_position - left
        output.append(samples[left] * (1.0 - fraction) + samples[right] * fraction)
    return output


def _advance_phase(phase: float, frequency_hz: float, sample_rate: int) -> float:
    next_phase = phase + (2.0 * math.pi * frequency_hz / max(sample_rate, 1))
    return math.fmod(next_phase, 2.0 * math.pi)


def _time_coeff(sample_rate: int, seconds: float) -> float:
    return 1.0 - math.exp(-1.0 / max(sample_rate * seconds, 1.0))


def _normalize_peak(samples: list[float], *, target_peak: float) -> list[float]:
    limited = _remove_dc(samples)
    peak = max((abs(sample) for sample in limited), default=0.0)
    if peak <= 0.000001:
        return limited
    scale = target_peak / peak
    return _limit([sample * scale for sample in limited])


def _remove_dc(samples: list[float]) -> list[float]:
    if not samples:
        return samples
    offset = sum(samples) / len(samples)
    return [sample - offset for sample in samples]


def _limit(samples: list[float]) -> list[float]:
    return [max(min(sample, 0.98), -0.98) for sample in samples]


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


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _theory_note(role: str) -> dict[str, Any]:
    return {
        "model": "kvae_native_source_filter_character_renderer",
        "role": role,
        "principle": (
            "A recorded performance provides timing and energy; KVAE rebuilds a character "
            "branch through pitch, tract resonance, source texture, body resonance, and "
            "explicit identity mixing."
        ),
        "external_program_dependency": "none_for_native_wav_render_path",
    }
