from __future__ import annotations

import datetime as dt
from typing import Any


BENCHMARK_PRODUCTS: list[dict[str, Any]] = [
    {
        "id": "vocaltractlab",
        "name": "VocalTractLab",
        "category": "articulatory_synthesis",
        "source_url": "https://www.vocaltractlab.de/",
        "benchmarked_capability": "articulation, acoustics, and control through an explicit vocal-tract model",
        "kvae_adoption": "source-filter vocal tract controls, formant design, future articulatory backend contract",
        "status": "implemented_contract",
    },
    {
        "id": "praat",
        "name": "Praat",
        "category": "speech_analysis_source_filter",
        "source_url": "https://praat.org/manual/Source-filter_synthesis.html",
        "benchmarked_capability": "separate source and filter manipulation with formants",
        "kvae_adoption": "vocal-tract design JSON and formant filter chain for every role",
        "status": "implemented_v1",
    },
    {
        "id": "world",
        "name": "WORLD Vocoder",
        "category": "analysis_synthesis_vocoder",
        "source_url": "https://github.com/mmorise/World",
        "benchmarked_capability": "F0, spectral envelope, aperiodicity analysis and resynthesis",
        "kvae_adoption": "reserved backend interface for higher-quality controllable rendering",
        "status": "planned_backend",
    },
    {
        "id": "elevenlabs_voice_changer",
        "name": "ElevenLabs Voice Changer",
        "category": "speech_to_speech_product",
        "source_url": "https://elevenlabs.io/docs/eleven-creative/playground/voice-changer",
        "benchmarked_capability": "preserve emotion, timing, and delivery while changing voice identity",
        "kvae_adoption": "conversion manifests preserve performance metadata and role controls",
        "status": "partially_implemented",
    },
    {
        "id": "altered_studio",
        "name": "Altered Studio",
        "category": "professional_voice_morphing",
        "source_url": "https://help.altered.ai/en/articles/32-morphing-your-voice-in-altered-studio",
        "benchmarked_capability": "import or record audio, choose target voice/model, tune voice controls, generate sample",
        "kvae_adoption": "voice-lab batch workflow, role groups, playlist, manifests, and review reports",
        "status": "partially_implemented",
    },
    {
        "id": "voicemod",
        "name": "Voicemod",
        "category": "real_time_voice_changer",
        "source_url": "https://support.voicemod.net/hc/en-us/articles/5397862236434-What-are-our-AI-Voices",
        "benchmarked_capability": "one-click character presets, sliders, real-time UX, easy disable-to-myself mode",
        "kvae_adoption": "role presets, clear/FX role pairs, future local UI with bypass/compare controls",
        "status": "planned_ui",
    },
    {
        "id": "openvoice",
        "name": "OpenVoice",
        "category": "open_source_style_control",
        "source_url": "https://github.com/myshell-ai/OpenVoice",
        "benchmarked_capability": "granular style control for emotion, accent, rhythm, pauses, and intonation",
        "kvae_adoption": "acting controls for speed, pause scale, emotion, formality, and ending style",
        "status": "partially_implemented",
    },
    {
        "id": "respeecher",
        "name": "Respeecher",
        "category": "professional_ethics_voice_conversion",
        "source_url": "https://www.respeecher.com/faq",
        "benchmarked_capability": "professional voice conversion workflow, acoustic-domain conversion, safety defenses",
        "kvae_adoption": "voice consent metadata, AI disclosure, privacy boundaries, review manifest",
        "status": "implemented_safety_layer",
    },
]


BIOACOUSTIC_REFERENCES: list[dict[str, Any]] = [
    {
        "id": "riede_eliason_miller_goller_clarke_2016",
        "name": "Coos, Booms, and Hoots: The Evolution of Closed-Mouth Vocal Behavior in Birds",
        "source_url": "https://academic.oup.com/evolut/article-abstract/70/8/1734/6851892",
        "kvae_adoption": "nonhuman dinosaur voices use closed-mouth boom and body-resonance synthesis rather than audible human speech identity",
    },
    {
        "id": "ut_jackson_closed_mouth_dinosaur_vocalization",
        "name": "Bird research suggests calling dinosaurs may have been tight-lipped",
        "source_url": "https://www.jsg.utexas.edu/news/2016/07/bird-research-suggests-calling-dinosaurs-may-have-been-tight-lipped",
        "kvae_adoption": "archosaur-inspired low throaty boom design for giant dinosaur roles",
    },
]


VOICE_ACTING_REFERENCES: list[dict[str, Any]] = [
    {
        "id": "ncvs_voice_science",
        "name": "National Center for Voice and Speech",
        "source_url": "https://ncvs.org/",
        "benchmarked_method": "treat voice as physiology, acoustics, breath, source, filter, and communication",
        "kvae_adoption": "voice roles are represented as controllable source, filter, articulation, and performance fields",
    },
    {
        "id": "ncvs_voice_production_tutorial",
        "name": "Principles of Voice Production tutorial topics",
        "source_url": "https://ncvs.org/archive/ncvs/tutorials/voiceprod/testing/index.html",
        "benchmarked_method": "break voice into laryngeal anatomy, airflow, oscillation, source-filter vowels, F0, intensity, and registers",
        "kvae_adoption": "role design exposes pitch, breath, roughness, formants, intensity, and register-like controls",
    },
    {
        "id": "source_filter_theory",
        "name": "Source-filter theory of voice production",
        "source_url": "https://www.voicescience.org/2025/05/lexicon/source-filter-theory/",
        "benchmarked_method": "separate vocal-fold sound generation from vocal-tract shaping and formants",
        "kvae_adoption": "human character voices use source/filter controls before heavier neural backends are added",
    },
    {
        "id": "british_voice_association_voice_ageing",
        "name": "British Voice Association: The Voice and Ageing",
        "source_url": "https://old.britishvoiceassociation.org.uk/voicecare_the-voice-and-ageing.htm",
        "benchmarked_method": "age changes breathing, phrase length, laryngeal freedom, teeth/dentures, and articulation",
        "kvae_adoption": "old/child roles should change breath, pace, articulation clarity, formants, and phrase energy together",
    },
    {
        "id": "sag_aftra_ai_voice_consent",
        "name": "SAG-AFTRA Artificial Intelligence resources",
        "source_url": "https://www.sagaftra.org/contracts-industry-resources/member-resources/artificial-intelligence",
        "benchmarked_method": "digital voice replicas require consent, control, and compensation norms",
        "kvae_adoption": "private voice profiles and generated manifests carry consent, ownership, and disclosure metadata",
    },
]


VOICE_ACTING_TECHNIQUES: list[dict[str, Any]] = [
    {
        "id": "script_intent",
        "name": "Script intent and playable action",
        "what_actors_do": "decide what the character wants and how each line changes the listener",
        "kvae_program_shape": "role prompts should store intention, relationship, emotional turn, and target audience",
    },
    {
        "id": "breath_support",
        "name": "Breath support and phrase energy",
        "what_actors_do": "control inhalation, pressure, phrase length, and release so speech stays alive",
        "kvae_program_shape": "breathiness, pause scale, pressure drive, phrase-length, and Korean punctuation timing controls",
    },
    {
        "id": "source_quality",
        "name": "Glottal source quality",
        "what_actors_do": "vary pitch, creak, rasp, breath, pressed voice, and register without injuring the voice",
        "kvae_program_shape": "pitch shift, pitch variance, roughness, subharmonics, breath noise, and pressure drive",
    },
    {
        "id": "resonance_shape",
        "name": "Resonance and vocal-tract shape",
        "what_actors_do": "move perceived size, age, warmth, nasal/oral color, and body placement through tract shape",
        "kvae_program_shape": "formant shift, bandwidth, nasal mix, oral/chest/head resonance, and role-specific anatomy design",
    },
    {
        "id": "articulation_diction",
        "name": "Articulation and diction",
        "what_actors_do": "shape jaw, tongue, lips, consonants, vowels, and Korean endings for clarity or character",
        "kvae_program_shape": "articulation strength, vowel stability, consonant sharpness, ending style, and Korean G2P review",
    },
    {
        "id": "tempo_rhythm",
        "name": "Tempo, rhythm, and pause",
        "what_actors_do": "use speed, silence, attack, sustain, and timing to create personality and tension",
        "kvae_program_shape": "speed, pause scale, micro-pause plan, sentence-ending contour, and performance envelope preservation",
    },
    {
        "id": "emotional_range",
        "name": "Emotional range and consistency",
        "what_actors_do": "keep a character emotionally consistent while allowing line-by-line variation",
        "kvae_program_shape": "emotion tags, role strength, candidate generation, and human listening score fields",
    },
    {
        "id": "vocal_safety",
        "name": "Vocal safety",
        "what_actors_do": "avoid harmful strain, especially for screams, monsters, and prolonged rough voices",
        "kvae_program_shape": "generate dangerous effects through synthesis/layering instead of forcing the source speaker to perform them",
    },
]


CREATOR_SOUND_DESIGN_MISSION: dict[str, Any] = {
    "goal": (
        "Benchmark how major studios build voices and sound effects, then turn those methods "
        "into a free, local-first tool for small creators making Korean videos, shorts, games, "
        "animations, and educational media."
    ),
    "boundary": (
        "KVAE should not copy copyrighted studio sounds. It should implement the workflow: "
        "source collection, legal attribution, layering, transformation, performance control, "
        "mixing, and listening review."
    ),
    "creator_promise": [
        "one recorded performance can direct many human character voices",
        "fully nonhuman creatures use sound-design engines rather than audible human speech identity",
        "every source layer keeps provenance, license, and AI/synthetic disclosure",
        "beginners can generate, compare, and refine candidates without owning a studio",
    ],
}


STUDIO_SOUND_DESIGN_REFERENCES: list[dict[str, Any]] = [
    {
        "id": "jurassic_world_bird_calls",
        "name": "Jurassic World dinosaur voices from bird recordings",
        "source_url": "https://www.audubon.org/magazine/jurassic-worlds-dinosaurs-roar-life-thanks-bird-calls",
        "benchmarked_method": "record birds and transform their tonal, expressive calls into dinosaur language",
        "kvae_adoption": "license-safe animal-source registry and species/mood layer mapping",
    },
    {
        "id": "jurassic_world_fallen_kingdom_creature_blends",
        "name": "Jurassic World: Fallen Kingdom creature vocal blends",
        "source_url": "https://www.motionpictures.org/2018/06/sound-designer-gives-voice-to-the-jurassic-world-fallen-kingdom-dinosaurs/",
        "benchmarked_method": "combine field recordings, household sounds, props, and animal layers per creature",
        "kvae_adoption": "creature recipes should accept animal, Foley, synthetic, and performance-control layers",
    },
    {
        "id": "jurassic_park_trex_composite_roar",
        "name": "Jurassic Park T-Rex composite roar method",
        "source_url": "https://www.slashfilm.com/1310511/jurassic-park-got-t-rex-roar-from-combination-of-three-different-animals/",
        "benchmarked_method": "build one iconic creature voice by blending different animal roles across the spectrum",
        "kvae_adoption": "cinematic creature presets need low body, threat, breath, attack, and scream layers",
    },
    {
        "id": "foley_sound_design_visual_media",
        "name": "Foley and visual-media sound design",
        "source_url": "https://www.soundonsound.com/techniques/sound-design-visual-media",
        "benchmarked_method": "replace or enhance visible action with carefully timed Foley and ambience",
        "kvae_adoption": "future video workflow should spot actions, generate aligned Foley, and mix subtly",
    },
    {
        "id": "animal_field_recording",
        "name": "Animal recording for professional sound libraries",
        "source_url": "https://www.boomlibrary.com/blog/how-to-record-animal-sound-effects/",
        "benchmarked_method": "capture clean animal recordings as source material for creature creation",
        "kvae_adoption": "source registry must track species, environment, noise, license, and permitted use",
    },
    {
        "id": "creature_layer_processing",
        "name": "Creature sound design tutorial",
        "source_url": "https://blog.prosoundeffects.com/creature-sound-design-tutorial?switchLanguage=ja",
        "benchmarked_method": "select, layer, pitch/time-shift, reverse, cut, and shape source sounds against picture",
        "kvae_adoption": "recipe engine should expose layer roles and deterministic transforms for each character",
    },
    {
        "id": "skywalker_sound_creature_loop_group",
        "name": "Skywalker Sound creature and loop-group workflow",
        "source_url": "https://www.starwars.com/news/skeleton-crew-skywalker-sound-interview",
        "benchmarked_method": "blend vocal performance, archived animal recordings, pitch/filter processing, and loop-group acting",
        "kvae_adoption": "separate performance-control tracks from animal/source layers and keep recipe transforms explicit",
    },
    {
        "id": "ben_burtt_thousand_recordings",
        "name": "Ben Burtt field-recording and transformation method",
        "source_url": "https://www.starwars.com/news/empire-at-40-ben-burtt-interview",
        "benchmarked_method": "collect many field recordings and transform recognizable sources into new cinematic identities",
        "kvae_adoption": "source-library workflow should encourage broad original recording before synthesis and layer selection",
    },
    {
        "id": "a_quiet_place_animal_vocals",
        "name": "A Quiet Place creature and silence sound rules",
        "source_url": "https://www.backstage.com/magazine/article/a-quiet-place-part-two-sound-editors-interview-73319/",
        "benchmarked_method": "define story sound rules and manipulate animal vocals for creature terror",
        "kvae_adoption": "role briefs should include world rules, danger thresholds, silence, and environment masking",
    },
    {
        "id": "project_hail_mary_alien_language_layers",
        "name": "Project Hail Mary alien language layering",
        "source_url": "https://www.space.com/entertainment/space-movies-shows/project-hail-mary-sound-designers-used-surprising-animal-sounds-to-create-rockys-musical-alien-voice-interview",
        "benchmarked_method": "combine animals, instruments, designed language, physical resonance, and character emotion",
        "kvae_adoption": "future alien/creature presets need communicative grammar plus physical resonator layers",
    },
]


STUDIO_SOUND_DESIGN_TECHNIQUES: list[dict[str, Any]] = [
    {
        "id": "spotting_and_intent",
        "name": "Spotting and intent",
        "what_studios_do": "define what the audience should feel before choosing sounds",
        "kvae_program_shape": "role briefs: creature size, threat, emotion, motion, realism level, and target medium",
    },
    {
        "id": "source_collection",
        "name": "Source collection",
        "what_studios_do": "record or license animals, props, voices, ambiences, and mechanical textures",
        "kvae_program_shape": "local source library with provenance, license, tags, and AI/synthetic disclosure",
    },
    {
        "id": "performance_control",
        "name": "Performance control",
        "what_studios_do": "use actor intent, picture timing, and director notes to shape the sound",
        "kvae_program_shape": "use the user's voice for timing, energy, and emotional contour without leaking identity when needed",
    },
    {
        "id": "layer_roles",
        "name": "Layer roles",
        "what_studios_do": "split a creature into body, throat, breath, attack, scream, texture, and movement layers",
        "kvae_program_shape": "creature recipes with named layer slots and per-layer transforms",
    },
    {
        "id": "transformation",
        "name": "Transformation",
        "what_studios_do": "use pitch shift, time stretch, EQ, saturation, reversal, morphing, and convolution creatively",
        "kvae_program_shape": "deterministic transform chain first; neural/WORLD backends later behind the same recipe contract",
    },
    {
        "id": "mix_and_space",
        "name": "Mix and space",
        "what_studios_do": "make layers feel like one body in one place through dynamics, reverb, perspective, and loudness",
        "kvae_program_shape": "automatic bus mix: close, body, room, impact, and small-speaker safety checks",
    },
    {
        "id": "candidate_review",
        "name": "Candidate review",
        "what_studios_do": "iterate many candidates against picture and keep what feels alive",
        "kvae_program_shape": "generate A/B/C candidates, objective reports, and human listening score fields",
    },
]


IMPLEMENTATION_LANES: list[dict[str, Any]] = [
    {
        "lane": "anatomy_controls",
        "inspired_by": ["VocalTractLab", "Praat", "WORLD Vocoder"],
        "implemented": [
            "source/filter vocal-tract design",
            "formant shift and bandwidth controls",
            "glottal roughness and subharmonic controls",
        ],
        "next": ["WORLD/pyworld analysis-synthesis adapter", "articulator trajectory editor"],
    },
    {
        "lane": "performance_preservation",
        "inspired_by": ["ElevenLabs Voice Changer", "Altered Studio", "OpenVoice"],
        "implemented": [
            "recorded-performance conversion contract",
            "speed/pause/emotion role controls",
            "voice-lab multi-role candidate workflow",
        ],
        "next": ["neural speech-to-speech backend", "side-by-side candidate listening score"],
    },
    {
        "lane": "nonhuman_bioacoustic_conversion",
        "inspired_by": [
            "Riede et al. closed-mouth vocalization research",
            "archosaur low-frequency body resonance",
            "major-studio creature sound design",
        ],
        "implemented": [
            "dinosaur roles remove audible source-speaker identity",
            "source performance drives duration, energy envelope, and dynamics only",
            "bioacoustic low-frequency boom, body rumble, throat grit, and pressure noise renderer",
        ],
        "next": [
            "license-safe animal/Foley source registry",
            "species-specific presets",
            "cinematic creature recipe engine",
            "spectral target review for nonhuman roles",
            "human listening score workflow",
        ],
    },
    {
        "lane": "creator_sound_design_engine",
        "inspired_by": ["Skywalker Sound creature workflows", "Foley stages", "field recording libraries"],
        "implemented": [
            "benchmark report stores studio workflow lessons",
            "public/private source boundaries are explicit",
            "nonhuman roles no longer rely on human voice identity",
            "kva source-library command",
            "kva source-library scan/validation",
            "kva creature-design command",
            "kva creature-design dinosaur render entrypoint",
        ],
        "next": [
            "curated kva source-library add command",
            "multi-creature creature-design render command",
            "Foley/action spotting for video clips",
            "beginner local UI with compare/export controls",
        ],
    },
    {
        "lane": "product_ux",
        "inspired_by": ["Voicemod", "Altered Studio"],
        "implemented": ["role groups", "clear/FX role variants", "playlist output"],
        "next": ["local UI", "bypass/original compare button", "real-time preview mode"],
    },
    {
        "lane": "safety_and_release",
        "inspired_by": ["Respeecher", "ElevenLabs"],
        "implemented": ["voice consent metadata", "AI voice disclosure", "private asset gitignore", "doctor checks"],
        "next": ["watermark hook", "synthetic speech detector hook", "release checklist automation"],
    },
]


def build_professional_benchmark_report() -> dict[str, Any]:
    return {
        "schema_version": "kva.professional_voice_benchmark.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "summary": {
            "product_count": len(BENCHMARK_PRODUCTS),
            "implementation_lane_count": len(IMPLEMENTATION_LANES),
            "bioacoustic_reference_count": len(BIOACOUSTIC_REFERENCES),
            "voice_acting_reference_count": len(VOICE_ACTING_REFERENCES),
            "voice_acting_technique_count": len(VOICE_ACTING_TECHNIQUES),
            "studio_sound_design_reference_count": len(STUDIO_SOUND_DESIGN_REFERENCES),
            "studio_sound_design_technique_count": len(STUDIO_SOUND_DESIGN_TECHNIQUES),
            "principle": (
                "A human voice is actor-capable: one speaker can vary anatomy-like resonance, "
                "source quality, articulation, timing, and emotion. KVAE should combine research-grade vocal-tract control, "
                "speech-to-speech performance preservation, creator-friendly UX, "
                "major-studio sound-design workflows, and explicit consent/safety metadata."
            ),
        },
        "creator_sound_design_mission": CREATOR_SOUND_DESIGN_MISSION,
        "voice_acting_references": VOICE_ACTING_REFERENCES,
        "voice_acting_techniques": VOICE_ACTING_TECHNIQUES,
        "actor_theory": {
            "claim": "Voice acting proves that one human voice can intentionally produce many perceived identities.",
            "program_model": [
                "source variation: pitch, breath, roughness, pressure",
                "filter variation: vocal tract length, formants, nasal/oral resonance",
                "articulation variation: jaw, tongue, consonant precision, vowel stability",
                "performance variation: tempo, pause, emotion, ending style",
                "identity anchoring: decide how much of the source speaker remains",
            ],
        },
        "bioacoustic_references": BIOACOUSTIC_REFERENCES,
        "studio_sound_design_references": STUDIO_SOUND_DESIGN_REFERENCES,
        "studio_sound_design_techniques": STUDIO_SOUND_DESIGN_TECHNIQUES,
        "products": BENCHMARK_PRODUCTS,
        "implementation_lanes": IMPLEMENTATION_LANES,
    }


def build_voice_conversion_benchmark_alignment() -> dict[str, Any]:
    return {
        "schema_version": "kva.voice_conversion_benchmark_alignment.v1",
        "adopted": [
            "source_filter_anatomy_controls",
            "voice_acting_technique_catalog",
            "performance_preserving_speech_to_speech_contract",
            "nonhuman_bioacoustic_conversion_without_audible_source_identity",
            "studio_sound_design_technique_catalog",
            "source_library_schema_cli",
            "source_library_scan_validation_cli",
            "creature_design_recipe_cli",
            "creature_design_dinosaur_render_entrypoint",
            "role_preset_and_variant_workflow",
            "review_manifest_and_safety_metadata",
        ],
        "inspired_by": [
            "VocalTractLab",
            "Praat",
            "WORLD Vocoder",
            "ElevenLabs Voice Changer",
            "Altered Studio",
            "Voicemod",
            "OpenVoice",
            "Respeecher",
        ],
        "remaining": [
            "neural speech-to-speech backend",
            "WORLD analysis-synthesis backend",
            "full license-safe animal and Foley source library manager",
            "multi-creature sound-design render CLI",
            "local UI with compare/bypass controls",
            "human listening score workflow",
        ],
    }
