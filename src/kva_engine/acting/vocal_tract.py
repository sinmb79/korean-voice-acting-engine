from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from kva_engine.acting.presets import get_preset


BASE_FORMANTS = (
    ("F1", 500.0, 90.0),
    ("F2", 1500.0, 130.0),
    ("F3", 2500.0, 180.0),
    ("F4", 3500.0, 240.0),
)


@dataclass(frozen=True)
class GlottalSource:
    pitch_ratio: float
    glottal_tension: float
    breath_noise: float
    roughness: float
    subharmonic_mix: float


@dataclass(frozen=True)
class VocalTractFilter:
    vocal_tract_length_scale: float
    formant_shift_ratio: float
    formant_bandwidth_scale: float
    pharynx_width: float
    oral_frontness: float
    lip_rounding: float
    nasal_resonance: float
    spectral_tilt_db: float


@dataclass(frozen=True)
class ArticulationModel:
    jaw_opening: float
    tongue_height: float
    consonant_precision: float
    vowel_stability: float


@dataclass(frozen=True)
class PerformanceModel:
    identity_anchor_strength: float
    character_distance: float
    tempo_ratio: float
    pause_scale: float
    intensity: float


@dataclass(frozen=True)
class VocalTractVoiceDesign:
    role: str
    archetype: str
    source: GlottalSource
    filter: VocalTractFilter
    articulation: ArticulationModel
    performance: PerformanceModel
    formants: list[dict[str, float | str]]
    filter_chain: list[str]
    theory: dict[str, Any]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "kva.vocal_tract_voice_design.v1",
            "role": self.role,
            "archetype": self.archetype,
            "source": asdict(self.source),
            "filter": asdict(self.filter),
            "articulation": asdict(self.articulation),
            "performance": asdict(self.performance),
            "formants": self.formants,
            "filter_chain": self.filter_chain,
            "theory": self.theory,
            "warnings": self.warnings,
        }


VOCAL_TRACT_PRESETS: dict[str, dict[str, Any]] = {
    "calm_narrator": {
        "archetype": "adult_male_clear",
        "vocal_tract_length_scale": 1.04,
        "formant_shift_ratio": 0.96,
        "formant_bandwidth_scale": 1.0,
        "pharynx_width": 0.55,
        "oral_frontness": 0.5,
        "lip_rounding": 0.35,
        "nasal_resonance": 0.12,
        "spectral_tilt_db": -1.5,
        "roughness": 0.06,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.48,
        "tongue_height": 0.52,
        "vowel_stability": 0.8,
    },
    "documentary": {
        "archetype": "large_warm_narrator",
        "vocal_tract_length_scale": 1.1,
        "formant_shift_ratio": 0.9,
        "formant_bandwidth_scale": 1.05,
        "pharynx_width": 0.62,
        "oral_frontness": 0.46,
        "lip_rounding": 0.42,
        "nasal_resonance": 0.1,
        "spectral_tilt_db": -3.5,
        "roughness": 0.08,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.5,
        "tongue_height": 0.48,
        "vowel_stability": 0.82,
    },
    "news_anchor": {
        "archetype": "neutral_broadcast_tract",
        "vocal_tract_length_scale": 1.0,
        "formant_shift_ratio": 1.0,
        "formant_bandwidth_scale": 0.9,
        "pharynx_width": 0.5,
        "oral_frontness": 0.58,
        "lip_rounding": 0.3,
        "nasal_resonance": 0.08,
        "spectral_tilt_db": 0.5,
        "roughness": 0.02,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.52,
        "tongue_height": 0.55,
        "vowel_stability": 0.92,
    },
    "bright_teacher": {
        "archetype": "forward_friendly_tract",
        "vocal_tract_length_scale": 0.96,
        "formant_shift_ratio": 1.04,
        "formant_bandwidth_scale": 0.95,
        "pharynx_width": 0.48,
        "oral_frontness": 0.66,
        "lip_rounding": 0.24,
        "nasal_resonance": 0.1,
        "spectral_tilt_db": 1.5,
        "roughness": 0.03,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.56,
        "tongue_height": 0.58,
        "vowel_stability": 0.84,
    },
    "old_storyteller": {
        "archetype": "aged_warm_tract",
        "vocal_tract_length_scale": 1.12,
        "formant_shift_ratio": 0.89,
        "formant_bandwidth_scale": 1.2,
        "pharynx_width": 0.6,
        "oral_frontness": 0.42,
        "lip_rounding": 0.44,
        "nasal_resonance": 0.18,
        "spectral_tilt_db": -4.0,
        "roughness": 0.22,
        "subharmonic_mix": 0.04,
        "jaw_opening": 0.44,
        "tongue_height": 0.42,
        "vowel_stability": 0.68,
    },
    "villain_low": {
        "archetype": "compressed_low_villain",
        "vocal_tract_length_scale": 1.18,
        "formant_shift_ratio": 0.84,
        "formant_bandwidth_scale": 1.08,
        "pharynx_width": 0.66,
        "oral_frontness": 0.34,
        "lip_rounding": 0.5,
        "nasal_resonance": 0.08,
        "spectral_tilt_db": -5.5,
        "roughness": 0.18,
        "subharmonic_mix": 0.1,
        "jaw_opening": 0.4,
        "tongue_height": 0.38,
        "vowel_stability": 0.72,
    },
    "childlike_fast": {
        "archetype": "short_bright_childlike",
        "vocal_tract_length_scale": 0.78,
        "formant_shift_ratio": 1.22,
        "formant_bandwidth_scale": 0.92,
        "pharynx_width": 0.38,
        "oral_frontness": 0.72,
        "lip_rounding": 0.18,
        "nasal_resonance": 0.16,
        "spectral_tilt_db": 3.5,
        "roughness": 0.02,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.62,
        "tongue_height": 0.66,
        "vowel_stability": 0.7,
    },
    "ai_assistant": {
        "archetype": "clean_precise_synthetic",
        "vocal_tract_length_scale": 0.98,
        "formant_shift_ratio": 1.02,
        "formant_bandwidth_scale": 0.86,
        "pharynx_width": 0.48,
        "oral_frontness": 0.62,
        "lip_rounding": 0.25,
        "nasal_resonance": 0.06,
        "spectral_tilt_db": 1.0,
        "roughness": 0.01,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.52,
        "tongue_height": 0.58,
        "vowel_stability": 0.9,
    },
    "wolf_growl": {
        "archetype": "canine_low_warning",
        "vocal_tract_length_scale": 1.26,
        "formant_shift_ratio": 0.78,
        "formant_bandwidth_scale": 1.28,
        "pharynx_width": 0.72,
        "oral_frontness": 0.28,
        "lip_rounding": 0.58,
        "nasal_resonance": 0.22,
        "spectral_tilt_db": -6.5,
        "roughness": 0.54,
        "subharmonic_mix": 0.22,
        "jaw_opening": 0.38,
        "tongue_height": 0.34,
        "vowel_stability": 0.5,
    },
    "wolf_growl_clear": {
        "archetype": "canine_clear_warning",
        "vocal_tract_length_scale": 1.18,
        "formant_shift_ratio": 0.84,
        "formant_bandwidth_scale": 1.16,
        "pharynx_width": 0.66,
        "oral_frontness": 0.34,
        "lip_rounding": 0.5,
        "nasal_resonance": 0.16,
        "spectral_tilt_db": -4.5,
        "roughness": 0.34,
        "subharmonic_mix": 0.12,
        "jaw_opening": 0.42,
        "tongue_height": 0.38,
        "vowel_stability": 0.62,
    },
    "wolf_growl_heavy": {
        "archetype": "canine_heavy_rough",
        "vocal_tract_length_scale": 1.34,
        "formant_shift_ratio": 0.72,
        "formant_bandwidth_scale": 1.42,
        "pharynx_width": 0.8,
        "oral_frontness": 0.24,
        "lip_rounding": 0.66,
        "nasal_resonance": 0.25,
        "spectral_tilt_db": -8.0,
        "roughness": 0.68,
        "subharmonic_mix": 0.32,
        "jaw_opening": 0.34,
        "tongue_height": 0.3,
        "vowel_stability": 0.42,
    },
    "monster_deep": {
        "archetype": "large_cavernous_monster",
        "vocal_tract_length_scale": 1.44,
        "formant_shift_ratio": 0.68,
        "formant_bandwidth_scale": 1.38,
        "pharynx_width": 0.86,
        "oral_frontness": 0.2,
        "lip_rounding": 0.72,
        "nasal_resonance": 0.1,
        "spectral_tilt_db": -9.0,
        "roughness": 0.58,
        "subharmonic_mix": 0.35,
        "jaw_opening": 0.36,
        "tongue_height": 0.28,
        "vowel_stability": 0.45,
    },
    "monster_deep_clear": {
        "archetype": "large_clear_monster",
        "vocal_tract_length_scale": 1.32,
        "formant_shift_ratio": 0.74,
        "formant_bandwidth_scale": 1.22,
        "pharynx_width": 0.78,
        "oral_frontness": 0.25,
        "lip_rounding": 0.65,
        "nasal_resonance": 0.08,
        "spectral_tilt_db": -6.5,
        "roughness": 0.34,
        "subharmonic_mix": 0.18,
        "jaw_opening": 0.4,
        "tongue_height": 0.32,
        "vowel_stability": 0.58,
    },
    "monster_deep_fx": {
        "archetype": "large_distorted_monster",
        "vocal_tract_length_scale": 1.52,
        "formant_shift_ratio": 0.62,
        "formant_bandwidth_scale": 1.52,
        "pharynx_width": 0.92,
        "oral_frontness": 0.16,
        "lip_rounding": 0.78,
        "nasal_resonance": 0.12,
        "spectral_tilt_db": -10.0,
        "roughness": 0.75,
        "subharmonic_mix": 0.46,
        "jaw_opening": 0.34,
        "tongue_height": 0.24,
        "vowel_stability": 0.34,
    },
    "dinosaur_giant": {
        "archetype": "giant_reptile_resonator",
        "vocal_tract_length_scale": 1.76,
        "formant_shift_ratio": 0.5,
        "formant_bandwidth_scale": 1.58,
        "pharynx_width": 0.9,
        "oral_frontness": 0.12,
        "lip_rounding": 0.86,
        "nasal_resonance": 0.08,
        "spectral_tilt_db": -12.0,
        "roughness": 0.78,
        "subharmonic_mix": 0.58,
        "jaw_opening": 0.28,
        "tongue_height": 0.18,
        "vowel_stability": 0.3,
    },
    "dinosaur_giant_clear": {
        "archetype": "giant_reptile_clear",
        "vocal_tract_length_scale": 1.46,
        "formant_shift_ratio": 0.66,
        "formant_bandwidth_scale": 1.3,
        "pharynx_width": 0.82,
        "oral_frontness": 0.2,
        "lip_rounding": 0.72,
        "nasal_resonance": 0.06,
        "spectral_tilt_db": -8.0,
        "roughness": 0.42,
        "subharmonic_mix": 0.28,
        "jaw_opening": 0.36,
        "tongue_height": 0.26,
        "vowel_stability": 0.5,
    },
    "dinosaur_giant_roar": {
        "archetype": "giant_reptile_roar",
        "vocal_tract_length_scale": 1.95,
        "formant_shift_ratio": 0.42,
        "formant_bandwidth_scale": 1.78,
        "pharynx_width": 1.0,
        "oral_frontness": 0.08,
        "lip_rounding": 0.94,
        "nasal_resonance": 0.08,
        "spectral_tilt_db": -14.0,
        "roughness": 0.92,
        "subharmonic_mix": 0.74,
        "jaw_opening": 0.24,
        "tongue_height": 0.14,
        "vowel_stability": 0.18,
    },
    "child_bright": {
        "archetype": "short_bright_childlike",
        "vocal_tract_length_scale": 0.76,
        "formant_shift_ratio": 1.25,
        "formant_bandwidth_scale": 0.9,
        "pharynx_width": 0.36,
        "oral_frontness": 0.76,
        "lip_rounding": 0.14,
        "nasal_resonance": 0.14,
        "spectral_tilt_db": 4.0,
        "roughness": 0.02,
        "subharmonic_mix": 0.0,
        "jaw_opening": 0.64,
        "tongue_height": 0.68,
        "vowel_stability": 0.72,
    },
}


def build_vocal_tract_design(
    role: str,
    *,
    identity_strength: float | None = None,
    intensity: float = 1.0,
) -> VocalTractVoiceDesign:
    preset = get_preset(role)
    role_data = preset.to_dict()
    base = VOCAL_TRACT_PRESETS.get(role, VOCAL_TRACT_PRESETS["calm_narrator"])
    clamped_intensity = _clamp(intensity, 0.0, 1.5)
    identity = _clamp(identity_strength if identity_strength is not None else preset.identity_strength)
    source = GlottalSource(
        pitch_ratio=round(2 ** (preset.pitch_shift / 12.0), 6),
        glottal_tension=round(_blend(0.5, 0.25 + preset.articulation_strength * 0.6, clamped_intensity), 6),
        breath_noise=round(_blend(0.08, preset.breathiness, clamped_intensity), 6),
        roughness=round(_blend(0.04, float(base["roughness"]), clamped_intensity), 6),
        subharmonic_mix=round(_blend(0.0, float(base["subharmonic_mix"]), clamped_intensity), 6),
    )
    tract = VocalTractFilter(
        vocal_tract_length_scale=round(_blend(1.0, float(base["vocal_tract_length_scale"]), clamped_intensity), 6),
        formant_shift_ratio=round(_blend(1.0, float(base["formant_shift_ratio"]), clamped_intensity), 6),
        formant_bandwidth_scale=round(_blend(1.0, float(base["formant_bandwidth_scale"]), clamped_intensity), 6),
        pharynx_width=round(_blend(0.5, float(base["pharynx_width"]), clamped_intensity), 6),
        oral_frontness=round(_blend(0.5, float(base["oral_frontness"]), clamped_intensity), 6),
        lip_rounding=round(_blend(0.3, float(base["lip_rounding"]), clamped_intensity), 6),
        nasal_resonance=round(_blend(0.08, float(base["nasal_resonance"]), clamped_intensity), 6),
        spectral_tilt_db=round(_blend(0.0, float(base["spectral_tilt_db"]), clamped_intensity), 6),
    )
    articulation = ArticulationModel(
        jaw_opening=round(_blend(0.5, float(base["jaw_opening"]), clamped_intensity), 6),
        tongue_height=round(_blend(0.5, float(base["tongue_height"]), clamped_intensity), 6),
        consonant_precision=round(_clamp(preset.articulation_strength), 6),
        vowel_stability=round(_blend(0.78, float(base["vowel_stability"]), clamped_intensity), 6),
    )
    performance = PerformanceModel(
        identity_anchor_strength=round(identity, 6),
        character_distance=round(1.0 - identity, 6),
        tempo_ratio=round(preset.speed, 6),
        pause_scale=round(preset.pause_scale, 6),
        intensity=round(clamped_intensity, 6),
    )
    formants = _formants(tract)
    filters = build_vocal_tract_filter_chain_from_parts(tract=tract, source=source, formants=formants)
    warnings: list[str] = []
    if identity < 0.35:
        warnings.append("low_identity_anchor_character_voice_may_no_longer_sound_like_source_speaker")
    return VocalTractVoiceDesign(
        role=role,
        archetype=str(base["archetype"]),
        source=source,
        filter=tract,
        articulation=articulation,
        performance=performance,
        formants=formants,
        filter_chain=filters,
        theory={
            "model": "source_filter_plus_actor_control",
            "source": "vocal-fold-like excitation: pitch, breath, roughness, subharmonics",
            "filter": "vocal-tract-like resonator: formant shift, bandwidth, spectral tilt, nasal resonance",
            "acting": {
                "emotion": role_data["emotion"],
                "ending_style": role_data["ending_style"],
                "formality": role_data["formality"],
            },
            "implementation_note": (
                "This v1 layer is a deterministic control model. WORLD or a neural "
                "speech-to-speech backend can later replace the renderer while keeping "
                "the same anatomy contract."
            ),
        },
        warnings=warnings,
    )


def build_vocal_tract_filter_chain(role: str, *, intensity: float = 1.0) -> list[str]:
    try:
        design = build_vocal_tract_design(role, intensity=intensity)
    except ValueError:
        return []
    return design.filter_chain


def build_vocal_tract_filter_chain_from_parts(
    *,
    tract: VocalTractFilter,
    source: GlottalSource,
    formants: list[dict[str, float | str]],
) -> list[str]:
    filters: list[str] = []
    highpass = 55 if tract.formant_shift_ratio < 0.85 else 90 if tract.formant_shift_ratio > 1.1 else 70
    lowpass = int(_clamp(9600 * tract.formant_shift_ratio, 4200, 12000))
    filters.extend([f"highpass=f={highpass}", f"lowpass=f={lowpass}"])

    for formant in formants:
        frequency = int(float(formant["frequency_hz"]))
        q = round(frequency / max(float(formant["bandwidth_hz"]), 1.0), 3)
        gain = round(float(formant["gain_db"]), 3)
        if abs(gain) >= 0.2:
            filters.append(f"equalizer=f={frequency}:t=q:w={q}:g={gain}")

    tilt = tract.spectral_tilt_db
    if tilt < -0.25:
        filters.append(f"equalizer=f=180:t=q:w=0.9:g={round(abs(tilt) * 0.55, 3)}")
        filters.append(f"equalizer=f=4200:t=q:w=0.8:g={round(tilt * 0.45, 3)}")
    elif tilt > 0.25:
        filters.append(f"equalizer=f=2600:t=q:w=0.9:g={round(tilt * 0.45, 3)}")
        filters.append(f"equalizer=f=6200:t=q:w=1.1:g={round(tilt * 0.3, 3)}")

    if tract.nasal_resonance >= 0.14:
        filters.append(f"equalizer=f=950:t=q:w=1.8:g={round(tract.nasal_resonance * 3.0, 3)}")
        filters.append(f"equalizer=f=2400:t=q:w=1.4:g={round(-tract.nasal_resonance * 2.0, 3)}")

    if source.roughness >= 0.5:
        filters.append(f"acrusher=bits=12:mix={round(_clamp(source.roughness * 0.22, 0.04, 0.28), 3)}:mode=1:aa=0.7")
    elif source.roughness >= 0.2:
        filters.append(f"acrusher=bits=14:mix={round(_clamp(source.roughness * 0.12, 0.03, 0.12), 3)}:mode=1:aa=0.8")

    if source.subharmonic_mix >= 0.2:
        filters.append(f"tremolo=f={round(_clamp(7.0 - source.subharmonic_mix * 5.0, 2.5, 7.0), 3)}:d={round(_clamp(source.subharmonic_mix * 0.25, 0.04, 0.18), 3)}")
    return filters


def _formants(tract: VocalTractFilter) -> list[dict[str, float | str]]:
    formants = []
    for name, frequency, bandwidth in BASE_FORMANTS:
        shifted = frequency * tract.formant_shift_ratio
        width = bandwidth * tract.formant_bandwidth_scale
        gain = _formant_gain(name, tract)
        formants.append(
            {
                "name": name,
                "frequency_hz": round(shifted, 3),
                "bandwidth_hz": round(width, 3),
                "gain_db": round(gain, 3),
            }
        )
    return formants


def _formant_gain(name: str, tract: VocalTractFilter) -> float:
    if name == "F1":
        return 1.5 + (tract.pharynx_width - 0.5) * 5.0 + (tract.formant_shift_ratio < 0.8) * 1.2
    if name == "F2":
        return 0.8 + (tract.oral_frontness - 0.5) * 4.0 - (tract.lip_rounding - 0.3) * 2.0
    if name == "F3":
        return 0.6 + (tract.oral_frontness - 0.5) * 2.5
    return 0.3 + tract.spectral_tilt_db * 0.15


def _blend(neutral: float, target: float, intensity: float) -> float:
    return neutral + (target - neutral) * intensity


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))
