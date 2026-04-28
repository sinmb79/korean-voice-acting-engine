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
        "inspired_by": ["Riede et al. closed-mouth vocalization research", "archosaur low-frequency body resonance"],
        "implemented": [
            "dinosaur roles remove audible source-speaker identity",
            "source performance drives duration, energy envelope, and dynamics only",
            "bioacoustic low-frequency boom, body rumble, throat grit, and pressure noise renderer",
        ],
        "next": ["species-specific presets", "spectral target review for nonhuman roles", "human listening score workflow"],
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
            "principle": (
                "A human voice is actor-capable: one speaker can vary anatomy-like resonance, "
                "source quality, articulation, timing, and emotion. KVAE should combine research-grade vocal-tract control, "
                "speech-to-speech performance preservation, creator-friendly UX, "
                "and explicit consent/safety metadata."
            ),
        },
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
        "products": BENCHMARK_PRODUCTS,
        "implementation_lanes": IMPLEMENTATION_LANES,
    }


def build_voice_conversion_benchmark_alignment() -> dict[str, Any]:
    return {
        "schema_version": "kva.voice_conversion_benchmark_alignment.v1",
        "adopted": [
            "source_filter_anatomy_controls",
            "performance_preserving_speech_to_speech_contract",
            "nonhuman_bioacoustic_conversion_without_audible_source_identity",
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
            "local UI with compare/bypass controls",
            "human listening score workflow",
        ],
    }
