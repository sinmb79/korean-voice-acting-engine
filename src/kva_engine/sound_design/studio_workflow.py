from __future__ import annotations

import datetime as dt
from typing import Any

from kva_engine.benchmarks.pro_voice_products import (
    CREATOR_SOUND_DESIGN_MISSION,
    STUDIO_SOUND_DESIGN_REFERENCES,
    STUDIO_SOUND_DESIGN_TECHNIQUES,
    VOICE_ACTING_TECHNIQUES,
)


SOURCE_LIBRARY_SCHEMA: dict[str, Any] = {
    "schema_version": "kva.source_library.v1",
    "required_fields": [
        "source_id",
        "display_name",
        "source_type",
        "origin",
        "creator_or_provider",
        "license",
        "attribution",
        "ai_or_synthetic_disclosure",
        "permitted_use",
        "privacy_level",
        "tags",
        "notes",
    ],
    "privacy_levels": ["public", "licensed", "local_private"],
    "allowed_license_examples": ["CC0", "CC-BY", "public-domain", "self-recorded", "commercial-license"],
    "blocked_sources": [
        "ripped movie or game creature sounds",
        "unlicensed commercial sound libraries",
        "a real person's voice without explicit consent",
        "private voice recordings committed to the public repository",
    ],
}


SOURCE_CATEGORIES: list[dict[str, Any]] = [
    {
        "id": "animal_vocal",
        "name": "animal vocal source",
        "purpose": "natural emotional cues, calls, growls, breaths, chirps, and threat signals",
        "examples": ["bird call", "dog growl", "horse breath", "frog croak", "whale tone"],
        "program_role": "raw identity material for nonhuman creatures after heavy transformation",
    },
    {
        "id": "foley_body",
        "name": "Foley body and movement",
        "purpose": "skin, weight, joints, mouth wetness, claws, cloth, impact, and gait",
        "examples": ["leather creak", "celery snap", "wet towel slap", "sand step", "stone scrape"],
        "program_role": "timed movement layer that makes a character feel physically present",
    },
    {
        "id": "human_performance",
        "name": "human performance controller",
        "purpose": "timing, intention, attack, release, emotional arc, and phrase energy",
        "examples": ["private actor guide track", "loop-group style crowd bed", "breath-only performance"],
        "program_role": "control signal; may be audible for human roles and must be hidden for fully nonhuman roles",
    },
    {
        "id": "synthetic_body",
        "name": "synthetic body resonance",
        "purpose": "large-body scale, impossible anatomy, pressure, subharmonics, and controlled non-speech tone",
        "examples": ["sub-bass oscillator", "formant resonator", "granular breath", "filtered noise"],
        "program_role": "safe way to create dangerous or impossible sounds without vocal strain",
    },
    {
        "id": "environment_space",
        "name": "environment and space",
        "purpose": "distance, room, cave, forest, city, broadcast, and small-speaker translation",
        "examples": ["short room impulse", "cave reverb", "forest ambience", "distant slapback"],
        "program_role": "mix layer that places the character in a believable scene",
    },
    {
        "id": "mechanical_texture",
        "name": "mechanical and material texture",
        "purpose": "robots, armor, huge bones, machinery, alien biology, and hybrid creature surfaces",
        "examples": ["servo", "chain drag", "metal door groan", "engine slowdown"],
        "program_role": "non-organic layer for fantasy, sci-fi, and stylized monsters",
    },
]


def build_source_library_report() -> dict[str, Any]:
    return {
        "schema_version": SOURCE_LIBRARY_SCHEMA["schema_version"],
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "mission": CREATOR_SOUND_DESIGN_MISSION,
        "source_library_schema": SOURCE_LIBRARY_SCHEMA,
        "source_categories": SOURCE_CATEGORIES,
        "studio_reference_ids": [reference["id"] for reference in STUDIO_SOUND_DESIGN_REFERENCES],
        "technique_ids": [technique["id"] for technique in STUDIO_SOUND_DESIGN_TECHNIQUES],
        "implementation_status": {
            "implemented": [
                "license and privacy schema",
                "source category taxonomy",
                "studio technique mapping",
                "CLI report for creators and future UI",
            ],
            "not_yet_implemented": [
                "automatic external source download",
                "source waveform indexing",
                "DAW-style timeline editor",
            ],
        },
    }


def build_creature_design_recipe(
    role: str,
    *,
    intent: str = "cinematic",
    intensity: float = 1.0,
) -> dict[str, Any]:
    normalized_intensity = max(0.1, min(float(intensity), 2.0))
    family = _role_family(role)
    generic_review_targets = [
        "source_provenance_complete=true",
        "license_and_attribution_complete=true",
        "ai_or_synthetic_disclosure_present=true",
        "loudness_safe_for_small_speakers=true",
        "human_listening_score_required=true",
    ]
    base = {
        "schema_version": "kva.creator_sound_design.recipe.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "role": role,
        "intent": intent,
        "intensity": normalized_intensity,
        "mission": CREATOR_SOUND_DESIGN_MISSION["goal"],
        "technique_catalog": {
            "voice_acting": [technique["id"] for technique in VOICE_ACTING_TECHNIQUES],
            "studio_sound_design": [technique["id"] for technique in STUDIO_SOUND_DESIGN_TECHNIQUES],
        },
        "source_policy": {
            "must_keep_provenance": True,
            "must_disclose_ai_or_synthetic_sources": True,
            "must_not_copy_copyrighted_studio_sounds": True,
            "private_voice_default": "local_private",
        },
        "review_targets": generic_review_targets,
    }
    if family == "dinosaur":
        role_recipe = _dinosaur_recipe(role, normalized_intensity)
    elif family == "wolf":
        role_recipe = _wolf_recipe(role, normalized_intensity)
    elif family == "monster":
        role_recipe = _monster_recipe(role, normalized_intensity)
    else:
        role_recipe = _human_character_recipe(role, normalized_intensity)
    role_review_targets = role_recipe.pop("review_targets", [])
    base.update(role_recipe)
    base["review_targets"] = generic_review_targets + role_review_targets
    return base


def _role_family(role: str) -> str:
    if role.startswith("dinosaur"):
        return "dinosaur"
    if role.startswith("wolf"):
        return "wolf"
    if role.startswith("monster"):
        return "monster"
    return "human_character"


def _dinosaur_recipe(role: str, intensity: float) -> dict[str, Any]:
    return {
        "design_goal": "make a giant nonhuman creature with no audible human speech identity",
        "source_voice_identity_retained": False,
        "source_speech_audible": False,
        "performance_policy": {
            "source_voice_usage": "duration, energy envelope, attack/release, and emotional contour only",
            "spoken_words_policy": "must be removed or masked; no weak articulation hints should remain",
            "recommended_engine": "kva-bioacoustic-dinosaur-v3",
        },
        "layer_chain": [
            {
                "slot": "performance_envelope",
                "source_type": "human_performance",
                "audible": False,
                "purpose": "actor timing and emotional force",
                "transforms": ["amplitude_follow", "phrase_attack_detect", "remove_speech_identity"],
                "mix": 0.0,
            },
            {
                "slot": "body_rumble",
                "source_type": "synthetic_body",
                "audible": True,
                "purpose": "large chest, neck, and air-sac mass",
                "transforms": ["subharmonic_oscillator", "slow_pressure_wobble", "soft_saturation"],
                "mix": round(0.34 * intensity, 3),
            },
            {
                "slot": "closed_mouth_boom",
                "source_type": "synthetic_body",
                "audible": True,
                "purpose": "archosaur-inspired boom/hoot carrier",
                "transforms": ["low_formant_resonance", "throat_pulse_modulation", "long_decay"],
                "mix": round(0.46 * intensity, 3),
            },
            {
                "slot": "throat_grit",
                "source_type": "animal_vocal_or_synthetic_noise",
                "audible": True,
                "purpose": "irregular pressure, danger, and living texture",
                "transforms": ["bandpass", "aperiodic_noise", "wavefold_or_saturation"],
                "mix": round(0.28 * intensity, 3),
            },
            {
                "slot": "wideband_roar_air",
                "source_type": "synthetic_body",
                "audible": True,
                "purpose": "speaker translation and roar edge without speech",
                "transforms": ["filtered_noise", "transient_gate", "small_speaker_presence_eq"],
                "mix": round(0.18 * intensity, 3),
            },
            {
                "slot": "space",
                "source_type": "environment_space",
                "audible": True,
                "purpose": "scale and distance",
                "transforms": ["short_early_reflections", "cave_or_forest_tail", "low_frequency_management"],
                "mix": round(0.16 * intensity, 3),
            },
        ],
        "review_targets": [
            "source_speech_audible=false",
            "source_voice_identity_retained=false",
            "low_frequency_body_present=true",
            "attack_matches_actor_performance=true",
            "small_speaker_roar_edge_present=true",
        ],
    }


def _wolf_recipe(role: str, intensity: float) -> dict[str, Any]:
    return {
        "design_goal": "create an animal warning voice that can remain semi-performative but not clearly human",
        "source_voice_identity_retained": role.endswith("_clear"),
        "source_speech_audible": role.endswith("_clear"),
        "performance_policy": {
            "source_voice_usage": "timing, growl gesture, breath pressure, and optional rough consonant contour",
            "spoken_words_policy": "clear variant may keep intelligibility; heavy variant should favor animal texture",
            "recommended_engine": "kva-convert-plus-layered-animal-v1",
        },
        "layer_chain": [
            {
                "slot": "growl_base",
                "source_type": "human_performance_or_animal_vocal",
                "audible": True,
                "purpose": "low warning intent",
                "transforms": ["pitch_lower", "roughness", "low_formant_shift"],
                "mix": round(0.5 * intensity, 3),
            },
            {
                "slot": "breath_teeth",
                "source_type": "foley_body",
                "audible": True,
                "purpose": "air, jaw, and threat texture",
                "transforms": ["highpass_breath", "transient_shaper", "stereo_narrow"],
                "mix": round(0.22 * intensity, 3),
            },
            {
                "slot": "space",
                "source_type": "environment_space",
                "audible": True,
                "purpose": "close animal perspective",
                "transforms": ["short_room", "low_mid_control"],
                "mix": round(0.1 * intensity, 3),
            },
        ],
        "review_targets": ["threat_intent_clear=true", "human_articulation_controlled=true"],
    }


def _monster_recipe(role: str, intensity: float) -> dict[str, Any]:
    return {
        "design_goal": "make a fantasy monster that may keep actor intention but hides ordinary human scale",
        "source_voice_identity_retained": role.endswith("_clear"),
        "source_speech_audible": role.endswith("_clear"),
        "performance_policy": {
            "source_voice_usage": "actor emotion, consonant timing, pressure, and breath",
            "spoken_words_policy": "clear variant can speak; FX variant should prioritize nonhuman texture",
            "recommended_engine": "kva-convert-plus-layered-creature-v1",
        },
        "layer_chain": [
            {
                "slot": "actor_core",
                "source_type": "human_performance",
                "audible": role.endswith("_clear"),
                "purpose": "meaning and acting intention",
                "transforms": ["pitch_lower", "formant_lower", "tempo_slow"],
                "mix": round((0.42 if role.endswith("_clear") else 0.16) * intensity, 3),
            },
            {
                "slot": "creature_body",
                "source_type": "synthetic_body",
                "audible": True,
                "purpose": "scale and impossible anatomy",
                "transforms": ["subharmonic", "ring_mod_low", "saturation"],
                "mix": round(0.36 * intensity, 3),
            },
            {
                "slot": "mouth_and_skin",
                "source_type": "foley_body",
                "audible": True,
                "purpose": "wetness, contact, jaw, and organic movement",
                "transforms": ["cut_to_phrases", "pitch_randomize", "transient_shape"],
                "mix": round(0.18 * intensity, 3),
            },
        ],
        "review_targets": ["ordinary_human_scale_removed=true", "acting_intent_preserved=true"],
    }


def _human_character_recipe(role: str, intensity: float) -> dict[str, Any]:
    return {
        "design_goal": "create a human character voice through acting controls before sound-effect layering",
        "source_voice_identity_retained": True,
        "source_speech_audible": True,
        "performance_policy": {
            "source_voice_usage": "speech content, timing, emotion, and identity with consent",
            "spoken_words_policy": "must stay intelligible for dialogue and Korean narration",
            "recommended_engine": "kva-convert-or-neural-sts",
        },
        "layer_chain": [
            {
                "slot": "actor_voice",
                "source_type": "human_performance",
                "audible": True,
                "purpose": "dialogue meaning and character identity",
                "transforms": ["role_pitch", "role_formant", "tempo", "articulation"],
                "mix": round(0.82 * intensity, 3),
            },
            {
                "slot": "room_and_polish",
                "source_type": "environment_space",
                "audible": True,
                "purpose": "broadcast, room, or scene perspective",
                "transforms": ["eq", "compress", "short_reverb"],
                "mix": round(0.08 * intensity, 3),
            },
        ],
        "review_targets": ["korean_intelligibility_high=true", "consent_metadata_present=true"],
    }
