from __future__ import annotations

import copy
import datetime as dt
from typing import Any


CAPABILITY_ROUTES: list[dict[str, Any]] = [
    {
        "id": "korean_voice_polish",
        "name": "Korean voice polish and use-case presets",
        "user_intent": "Make the source Korean recording clearer, cleaner, and ready for a use case.",
        "production_policy": "kvae_supported",
        "kvae_status": "production_v1",
        "default_handler": "kva polish",
        "kvae_commands": [
            "kva polish --preset cleanup",
            "kva polish --preset announcer",
            "kva polish --preset shorts",
            "kva polish --preset drama",
            "kva polish --preset documentary",
        ],
        "what_kvae_should_do": [
            "preserve the source speaker identity",
            "reduce rough noise and harshness",
            "improve Korean speech clarity",
            "prepare loudness and tone for shorts, drama, documentary, announcements, and education",
            "write a manifest that states this is not a new speaker or child voice",
        ],
        "what_kvae_should_not_claim": [
            "new actor identity",
            "child voice from an adult recording",
            "convincing creature or dinosaur voice",
        ],
        "external_replacements": [],
    },
    {
        "id": "korean_script_preparation",
        "name": "Korean script normalization, SSML, and pronunciation planning",
        "user_intent": "Turn Korean text into speech-ready text with safer number, date, English, symbol, and particle handling.",
        "production_policy": "kvae_supported",
        "kvae_status": "production_v1",
        "default_handler": "kva normalize",
        "kvae_commands": [
            "kva normalize",
            "kva ssml",
            "kva cast",
        ],
        "what_kvae_should_do": [
            "normalize Korean numbers, dates, times, phone numbers, English, symbols, and particles",
            "produce inspectable speech_text, phoneme_text, and normalization traces",
            "prepare line-level delivery hints for later TTS or recording",
        ],
        "what_kvae_should_not_claim": [
            "human-level acting by text rules alone",
            "perfect Korean prosody without listening review",
        ],
        "external_replacements": [
            {
                "name": "NAVER Cloud CLOVA Dubbing",
                "best_for": "Korean-region AI dubbing with provided voices and editing UI",
                "source_url": "https://guide.ncloud-docs.com/docs/en/clovadubbing-overview",
                "handoff": "export KVAE-normalized script and use a licensed CLOVA voice when the target is a different speaker",
            },
            {
                "name": "Vrew",
                "best_for": "Korean creator video editing, subtitles, and built-in AI voices",
                "source_url": "https://vrew.ai/ko/",
                "handoff": "export KVAE-normalized script for video/subtitle/TTS assembly in Vrew",
            },
        ],
    },
    {
        "id": "audio_review_and_training_prep",
        "name": "Audio review and local training preparation",
        "user_intent": "Check recordings and prepare private Korean voice data without exposing it in the public repo.",
        "production_policy": "kvae_supported",
        "kvae_status": "production_v1",
        "default_handler": "kva recording-check",
        "kvae_commands": [
            "kva recording-check",
            "kva review-audio",
            "kva split-recording",
            "kva recording-plan",
            "kva transcript-review",
            "kva dataset-split",
            "kva train-profile",
        ],
        "what_kvae_should_do": [
            "check loudness, clipping, silence, and review metadata",
            "split long recordings into local segments",
            "prepare manifests for private local training assets",
            "keep private voice assets outside the public repository",
        ],
        "what_kvae_should_not_claim": [
            "automatic consent for third-party voices",
            "public redistribution rights for private voices",
        ],
        "external_replacements": [],
    },
    {
        "id": "persona_script_coverage",
        "name": "Korean persona-aware script and review coverage",
        "user_intent": "Use diverse Korean adult personas to make scripts, role prompts, and review cases less generic.",
        "production_policy": "kvae_supported",
        "kvae_status": "metadata_and_prompt_design",
        "default_handler": "kva recording-plan",
        "kvae_commands": [
            "kva recording-plan",
            "kva normalize",
            "kva review-audio",
        ],
        "what_kvae_should_do": [
            "use persona metadata to diversify Korean recording prompts and evaluation scripts",
            "cover age, region, occupation, family context, hobbies, and delivery situations",
            "keep it text-only unless separate consented voice recordings are provided",
            "cite the dataset when generated prompts are derived from it",
        ],
        "what_kvae_should_not_claim": [
            "voice data or speaker embeddings are available from the persona dataset",
            "minor or child voices, because the dataset is adult-only",
            "real-person identity, because the personas are synthetic",
        ],
        "external_replacements": [
            {
                "name": "NVIDIA Nemotron-Personas-Korea",
                "best_for": "synthetic Korean adult persona coverage for prompt and evaluation diversity",
                "source_url": "https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea",
                "handoff": "sample persona rows to generate Korean script prompts; do not treat it as audio training data",
                "license": "CC-BY-4.0",
            },
        ],
    },
    {
        "id": "heavy_noise_or_reverb_repair",
        "name": "Heavy noise, echo, and reverb repair",
        "user_intent": "Rescue recordings with strong background noise, room echo, or damaged dialogue.",
        "production_policy": "external_replacement",
        "kvae_status": "basic_cleanup_only",
        "default_handler": "external_audio_repair",
        "kvae_commands": [
            "kva recording-check",
            "kva polish --preset cleanup",
        ],
        "what_kvae_should_do": [
            "attempt light cleanup only when the source is already usable",
            "flag poor recordings for external repair rather than over-processing them",
        ],
        "what_kvae_should_not_claim": [
            "studio-grade dialogue isolation",
            "deep dereverb",
            "reconstruction of heavily masked speech",
        ],
        "external_replacements": [
            {
                "name": "iZotope RX Dialogue Isolate",
                "best_for": "professional dialogue denoise and dereverb in a DAW or RX workflow",
                "source_url": "https://www.izotope.com/en/products/rx/features/dialogue-isolate",
                "handoff": "repair the source WAV first, then bring the cleaned WAV back to kva polish",
            },
            {
                "name": "Adobe Podcast Enhance Speech",
                "best_for": "fast web-based speech cleanup for noisy or echoey voice recordings",
                "source_url": "https://podcast.adobe.com/en/enhance-speech-v2",
                "handoff": "enhance the source file, download the repaired WAV/MP3, then run kva recording-check and kva polish",
            },
            {
                "name": "Descript Studio Sound",
                "best_for": "one-click voice enhancement inside a video/podcast editing workflow",
                "source_url": "https://help.descript.com/hc/en-us/articles/10327603613837-Studio-Sound",
                "handoff": "use Studio Sound for strong noise/echo reduction, then archive the final export with KVAE metadata",
            },
            {
                "name": "Voice-Pro",
                "best_for": "external WebUI workflow that combines Whisper, Demucs, subtitles, translation, and TTS",
                "source_url": "https://github.com/abus-aikorea/voice-pro",
                "handoff": "keep Voice-Pro as a separate GPLv3 application and bring repaired/transcribed outputs back to KVAE",
                "license": "GPL-3.0",
            },
        ],
    },
    {
        "id": "different_human_speaker",
        "name": "Different human speaker or actor identity",
        "user_intent": "Use one performance but output it as a different adult speaker or a library voice.",
        "production_policy": "external_replacement",
        "kvae_status": "research_only",
        "default_handler": "external_speech_to_speech",
        "kvae_commands": [
            "kva normalize",
            "kva polish --preset cleanup",
            "kva review-audio",
        ],
        "what_kvae_should_do": [
            "prepare a clean Korean source performance",
            "preserve consent and ownership metadata",
            "review the returned audio for intelligibility and disclosure",
        ],
        "what_kvae_should_not_claim": [
            "production-grade voice identity conversion",
            "licensed access to a target voice",
            "permission to imitate a real person",
        ],
        "external_replacements": [
            {
                "name": "Resemble AI Speech-to-Speech",
                "best_for": "speech-to-speech conversion that preserves delivery while changing target voice",
                "source_url": "https://www.resemble.ai/products/speech-to-speech",
                "handoff": "send a clean, consented source WAV and a licensed target voice; import the returned WAV for KVAE review",
            },
            {
                "name": "ElevenLabs Voice Changer",
                "best_for": "cloud/API voice changing with broad language support including Korean",
                "source_url": "https://elevenlabs.io/voice-changer",
                "handoff": "use only with rights-cleared voices, then run KVAE review and disclosure manifest",
            },
            {
                "name": "Voice-Pro",
                "best_for": "local external experimentation with F5-TTS, E2-TTS, CosyVoice, RVC, and WebUI comparison",
                "source_url": "https://github.com/abus-aikorea/voice-pro",
                "handoff": "run as a separate GPLv3 tool; do not copy its code into KVAE's Apache-2.0 source tree",
                "license": "GPL-3.0",
            },
        ],
    },
    {
        "id": "child_or_age_voice",
        "name": "Child, elderly, or age-transformed acting voice",
        "user_intent": "Turn an adult source recording into a convincing child or strongly age-shifted character.",
        "production_policy": "external_replacement",
        "kvae_status": "not_productized",
        "default_handler": "licensed_voice_library_or_actor",
        "kvae_commands": [
            "kva normalize",
            "kva polish --preset cleanup",
            "kva review-audio",
        ],
        "what_kvae_should_do": [
            "prepare Korean script and a clean guide performance",
            "recommend licensed AI voices or a human actor instead of pretending the adult source can become a child",
            "document AI voice disclosure and usage rights",
        ],
        "what_kvae_should_not_claim": [
            "convincing child voice from a private adult voice",
            "safe imitation of a minor",
            "commercial rights for a generated age voice without checking the provider terms",
        ],
        "external_replacements": [
            {
                "name": "NAVER Cloud CLOVA Dubbing",
                "best_for": "licensed Korean dubbing voices by situation, age, language, and emotion",
                "source_url": "https://guide.ncloud-docs.com/docs/en/clovadubbing-overview",
                "handoff": "export the KVAE-normalized script and pick an appropriate licensed voice in CLOVA Dubbing",
            },
            {
                "name": "Vrew AI voices",
                "best_for": "Korean creator videos that need many selectable AI voices and subtitle editing",
                "source_url": "https://vrew.ai/ko/",
                "handoff": "assemble subtitles and licensed AI voice in Vrew, then archive source and disclosure metadata",
            },
            {
                "name": "Voice-Pro",
                "best_for": "external WebUI testing of open TTS and voice-cloning stacks",
                "source_url": "https://github.com/abus-aikorea/voice-pro",
                "handoff": "use only as a separate tool and verify every voice/model license before production use",
                "license": "GPL-3.0",
            },
        ],
    },
    {
        "id": "creature_or_dinosaur",
        "name": "Creature, monster, wolf, or dinosaur voice",
        "user_intent": "Create a nonhuman creature voice that should not leave audible human speech identity.",
        "production_policy": "external_replacement",
        "kvae_status": "recipe_and_review_only",
        "default_handler": "sound_design_workflow",
        "kvae_commands": [
            "kva source-library",
            "kva creature-design",
            "kva review-character",
        ],
        "what_kvae_should_do": [
            "create a license-safe source library schema",
            "generate sound-design recipes and provenance requirements",
            "review whether human speech traces remain too audible",
        ],
        "what_kvae_should_not_claim": [
            "finished cinematic dinosaur voices from one spoken WAV",
            "copying movie/game creature sounds",
            "production creature design without source layers, Foley, synthesis, and human review",
        ],
        "external_replacements": [
            {
                "name": "Krotos Dehumaniser 2",
                "best_for": "creature and monster vocal sound design with modular reactive processing",
                "source_url": "https://www.krotosaudio.com/dehumaniser2/",
                "handoff": "use KVAE for recipe/source metadata, then design the final creature voice in Dehumaniser or a DAW",
            },
            {
                "name": "REAPER, Pro Tools, Logic, Cubase, or another DAW",
                "best_for": "layering animal, Foley, synthetic body resonance, and performance-control tracks",
                "source_url": "https://www.reaper.fm/",
                "handoff": "use KVAE source-library metadata and build the final mix in a DAW with licensed source sounds",
            },
        ],
    },
    {
        "id": "video_dubbing_editing",
        "name": "Video dubbing, subtitles, and final creator assembly",
        "user_intent": "Put the polished or AI-generated voice into shorts, drama, education, or social video.",
        "production_policy": "external_replacement",
        "kvae_status": "audio_asset_preparation",
        "default_handler": "video_editor",
        "kvae_commands": [
            "kva normalize",
            "kva polish",
            "kva review-audio",
        ],
        "what_kvae_should_do": [
            "prepare the script and polished WAV",
            "emit review metadata and usage notes",
            "stay focused on Korean speech quality rather than becoming a full video editor",
        ],
        "what_kvae_should_not_claim": [
            "timeline video editing",
            "automatic lip-sync dubbing",
            "full subtitle and cut editing UI",
        ],
        "external_replacements": [
            {
                "name": "Vrew",
                "best_for": "Korean-friendly subtitle editing, AI voices, and creator video assembly",
                "source_url": "https://vrew.ai/ko/",
                "handoff": "bring in KVAE-polished WAV or KVAE-normalized script for subtitles and video editing",
            },
            {
                "name": "DaVinci Resolve Fairlight",
                "best_for": "professional video/audio timeline finishing and dialogue tools",
                "source_url": "https://www.blackmagicdesign.com/products/davinciresolve",
                "handoff": "mix KVAE-polished WAVs against picture, music, and effects in Fairlight",
            },
            {
                "name": "Voice-Pro",
                "best_for": "all-in-one external WebUI for YouTube download, ASR, translation, subtitles, and TTS tests",
                "source_url": "https://github.com/abus-aikorea/voice-pro",
                "handoff": "keep it outside KVAE; exchange WAV, SRT, TXT, and JSON artifacts only",
                "license": "GPL-3.0",
            },
        ],
    },
    {
        "id": "experimental_native_character",
        "name": "KVAE native character conversion experiments",
        "user_intent": "Research pitch/formant/source-filter character controls inside KVAE.",
        "production_policy": "research_only",
        "kvae_status": "experimental",
        "default_handler": "kva convert --engine native",
        "kvae_commands": [
            "kva convert --engine native",
            "kva voice-lab --engine native",
            "kva vocal-tract",
        ],
        "what_kvae_should_do": [
            "keep experiments inspectable and labeled",
            "avoid presenting candidates as production-grade character voices",
            "feed lessons back into polish, review, and external handoff workflows",
        ],
        "what_kvae_should_not_claim": [
            "production-ready child, wolf, monster, or dinosaur conversion",
            "replacement for professional speech-to-speech models",
            "replacement for creature sound-design plugins",
        ],
        "external_replacements": [
            {
                "name": "Resemble AI or ElevenLabs",
                "best_for": "production speech-to-speech target speaker conversion",
                "source_url": "https://www.resemble.ai/products/speech-to-speech",
                "handoff": "use KVAE only for script prep, source cleanup, and review metadata",
            },
            {
                "name": "Krotos Dehumaniser 2 or DAW sound design",
                "best_for": "nonhuman creature sound design",
                "source_url": "https://www.krotosaudio.com/dehumaniser2/",
                "handoff": "use KVAE source-library and recipe reports as the planning layer",
            },
            {
                "name": "Voice-Pro",
                "best_for": "external GPLv3 WebUI benchmark for open TTS, ASR, translation, and cloning workflows",
                "source_url": "https://github.com/abus-aikorea/voice-pro",
                "handoff": "use as a separate application; KVAE should adopt workflow ideas, not copy GPL code",
                "license": "GPL-3.0",
            },
        ],
    },
]


CAPABILITY_TASK_IDS = tuple(route["id"] for route in CAPABILITY_ROUTES)


def list_capability_routes(*, production_only: bool = False) -> list[dict[str, Any]]:
    routes = [
        route
        for route in CAPABILITY_ROUTES
        if not production_only or route["production_policy"] in {"kvae_supported", "external_replacement"}
    ]
    return copy.deepcopy(routes)


def get_capability_route(task_id: str) -> dict[str, Any]:
    for route in CAPABILITY_ROUTES:
        if route["id"] == task_id:
            return copy.deepcopy(route)
    raise KeyError(f"Unknown capability task: {task_id}")


def build_capability_report(
    *,
    task_id: str | None = None,
    production_only: bool = False,
) -> dict[str, Any]:
    if task_id:
        routes = [get_capability_route(task_id)]
    else:
        routes = list_capability_routes(production_only=production_only)
    return {
        "schema_version": "kva.capability_router.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "product_promise": (
            "KVAE is a Korean-first voice preparation and polish engine. It should do the parts it can "
            "own reliably, and route unrelated speaker conversion, child voices, creature voices, heavy "
            "repair, and video finishing to specialist tools."
        ),
        "routing_policy": {
            "kvae_supported": "ship inside KVAE as a normal user-facing feature",
            "external_replacement": "prepare inputs and metadata in KVAE, then use a specialist program for production output",
            "research_only": "keep available only as labeled experimentation; do not use as a public product promise",
        },
        "recommended_creator_flow": [
            "write or import Korean script",
            "run kva normalize / kva ssml if text is involved",
            "record or import a clean source WAV",
            "run kva recording-check",
            "run kva polish for cleanup, announcer, shorts, drama, or documentary delivery",
            "use external tools only for tasks outside KVAE's honest scope",
            "bring finished audio back to kva review-audio and keep disclosure/provenance metadata",
        ],
        "counts": _count_routes(routes),
        "routes": routes,
    }


def _count_routes(routes: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"kvae_supported": 0, "external_replacement": 0, "research_only": 0}
    for route in routes:
        policy = route.get("production_policy")
        if policy in counts:
            counts[policy] += 1
    return counts
