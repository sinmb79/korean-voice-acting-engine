from __future__ import annotations

import copy
import datetime as dt
from typing import Any


TTS_BACKENDS: list[dict[str, Any]] = [
    {
        "id": "voxcpm2",
        "name": "VoxCPM2",
        "provider": "OpenBMB",
        "source_url": "https://github.com/OpenBMB/VoxCPM",
        "model_url": "https://huggingface.co/openbmb/VoxCPM2",
        "license": "Apache-2.0",
        "kvae_status": "integrated_default",
        "backend_role": "primary_korean_tts",
        "parameters": "2B",
        "runtime": "Python >=3.10,<3.13; PyTorch >=2.5; CUDA >=12 recommended",
        "korean_support": "Korean is officially supported as one of 30 languages",
        "strengths": [
            "multilingual TTS including Korean",
            "voice design from text descriptions",
            "controllable voice cloning from reference audio",
            "48 kHz output",
            "LoRA and full fine-tuning paths",
            "commercial-ready Apache-2.0 code and weights according to the repository",
        ],
        "limitations": [
            "requires GPU-class runtime for normal local use",
            "voice design and controllable cloning can vary between generations",
            "needs safety review because realistic voice cloning can be misused",
        ],
        "kvae_use": [
            "default backend for kva render --engine voxcpm",
            "best current target for private Korean reference-voice experiments",
            "always pair generated WAV with kva review-audio and disclosure metadata",
        ],
    },
    {
        "id": "moss_tts_nano",
        "name": "MOSS-TTS-Nano",
        "provider": "OpenMOSS",
        "source_url": "https://github.com/OpenMOSS/MOSS-TTS-Nano",
        "model_url": "https://huggingface.co/OpenMOSS-Team/MOSS-TTS-Nano",
        "license": "Apache-2.0",
        "kvae_status": "research_candidate",
        "backend_role": "lightweight_local_fallback_candidate",
        "parameters": "0.1B",
        "runtime": "CPU-friendly; ONNX Runtime CPU path available",
        "korean_support": "listed as one of 20 supported languages",
        "strengths": [
            "tiny model for low-footprint local speech generation",
            "ONNX CPU inference without PyTorch during inference",
            "voice cloning workflow with prompt audio",
            "streaming and long-text oriented workflow",
            "fine-tuning code is provided",
        ],
        "limitations": [
            "quality must be tested with Korean before production use",
            "not yet wired into KVAE render",
            "dependency stack includes text normalization packages that can be difficult on Windows",
        ],
        "kvae_use": [
            "evaluate as a CPU/offline fallback after VoxCPM2",
            "use KVAE Korean normalization before handing text to MOSS",
            "use kva review-audio to compare Korean clarity, similarity, and stability",
        ],
    },
    {
        "id": "cosyvoice3",
        "name": "Fun-CosyVoice 3.0",
        "provider": "FunAudioLLM",
        "source_url": "https://github.com/FunAudioLLM/CosyVoice",
        "model_url": "https://huggingface.co/FunAudioLLM",
        "license": "Apache-2.0",
        "kvae_status": "research_candidate",
        "backend_role": "multilingual_zero_shot_candidate",
        "parameters": "0.5B family",
        "runtime": "Python/CUDA stack; repository provides inference, training, deployment, and streaming paths",
        "korean_support": "Korean is listed among the common supported languages in the repository",
        "strengths": [
            "zero-shot multilingual voice generation including Korean",
            "bi-streaming text-in and audio-out design",
            "claims low latency around 150 ms in project highlights",
            "Apache-2.0 repository license",
            "useful benchmark for production-oriented controllability and deployment packaging",
        ],
        "limitations": [
            "not yet wired into KVAE render",
            "must be tested locally for Korean pronunciation and model setup stability",
            "model and deployment terms should be checked per downloaded checkpoint",
        ],
        "kvae_use": [
            "evaluate beside VoxCPM2 for Korean zero-shot and streaming quality",
            "compare naturalness, pronunciation, and latency with KVAE product-quality gates",
            "do not promote until Korean smoke tests pass",
        ],
    },
    {
        "id": "f5_tts",
        "name": "F5-TTS v1",
        "provider": "SWivid",
        "source_url": "https://github.com/SWivid/F5-TTS",
        "model_url": "https://huggingface.co/SWivid/F5-TTS",
        "license": "Code MIT; pretrained models CC-BY-NC according to the repository",
        "kvae_status": "research_noncommercial_candidate",
        "backend_role": "flow_matching_tts_research_candidate",
        "parameters": "not tracked in KVAE registry",
        "runtime": "Python >=3.10; PyTorch; Docker and Triton/TensorRT-LLM deployment examples exist",
        "korean_support": "Korean support is not treated as production-ready until tested locally",
        "strengths": [
            "widely used open research implementation",
            "fast flow-matching TTS architecture",
            "Docker and package paths are available",
            "good benchmark candidate for zero-shot voice cloning behavior",
        ],
        "limitations": [
            "pretrained model license is non-commercial in the reviewed repository text",
            "not yet wired into KVAE render",
            "Korean production quality must be proven separately",
        ],
        "kvae_use": [
            "research benchmark only unless a commercial-safe checkpoint is selected",
            "compare against VoxCPM2 and MOSS-TTS-Nano on Korean intelligibility",
            "do not ship as a default backend for creator production",
        ],
    },
    {
        "id": "indextts2",
        "name": "IndexTTS2",
        "provider": "bilibili Index Team",
        "source_url": "https://github.com/index-tts/index-tts",
        "model_url": "https://huggingface.co/IndexTeam/IndexTTS-2",
        "license": "bilibili Model Use License Agreement",
        "kvae_status": "license_gated_research_candidate",
        "backend_role": "duration_and_emotion_control_benchmark",
        "parameters": "not tracked in KVAE registry",
        "runtime": "uv-managed Python environment; CUDA recommended for practical use",
        "korean_support": "cross-lingual capability must be tested for Korean before production use",
        "strengths": [
            "duration-control direction is highly relevant for dubbing and lip-sync",
            "decouples speaker timbre and emotional style in its stated design",
            "strong reference for expressive control and audio-visual synchronization",
        ],
        "limitations": [
            "custom model license is not Apache/MIT",
            "commercial and redistribution rights require careful review",
            "repository warns against unauthorized voice synthesis and misuse",
            "not yet wired into KVAE render",
        ],
        "kvae_use": [
            "benchmark its duration-control product idea, not its code, unless license review passes",
            "route production use through explicit legal/license approval",
            "use as a design reference for KVAE timing-control gates",
        ],
    },
    {
        "id": "fish_audio_s2",
        "name": "Fish Audio S2 Pro",
        "provider": "Fish Audio",
        "source_url": "https://github.com/fishaudio/fish-speech",
        "model_url": "https://speech.fish.audio/",
        "license": "Fish Audio Research License; commercial use requires a separate written license",
        "kvae_status": "research_noncommercial_candidate",
        "backend_role": "sota_quality_benchmark_candidate",
        "parameters": "not tracked in KVAE registry",
        "runtime": "Fish Audio docs provide install, CLI, WebUI, server, Docker, and SGLang guidance",
        "korean_support": "multilingual support is claimed; Korean must be checked locally for KVAE use",
        "strengths": [
            "strong public benchmark claims for multilingual TTS quality",
            "official docs cover CLI, WebUI, server, and Docker operation",
            "useful ceiling benchmark for naturalness and emotional richness",
        ],
        "limitations": [
            "commercial use requires a separate license",
            "not yet wired into KVAE render",
            "do not redistribute weights or derivative outputs as KVAE assets without license review",
        ],
        "kvae_use": [
            "quality benchmark and research comparison only by default",
            "promote only if licensing and Korean evaluation are both cleared",
            "use product-quality gates to compare with VoxCPM2",
        ],
    },
    {
        "id": "vibevoice_realtime_tts",
        "name": "VibeVoice-Realtime-0.5B",
        "provider": "Microsoft",
        "source_url": "https://github.com/microsoft/VibeVoice",
        "model_url": "https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B",
        "license": "MIT",
        "kvae_status": "research_candidate",
        "backend_role": "streaming_tts_research_candidate",
        "parameters": "0.5B",
        "runtime": "NVIDIA PyTorch container recommended; Mac M4 Pro and NVIDIA T4 mentioned in docs",
        "korean_support": "Korean is offered only as an experimental exploration voice; English is the primary target",
        "strengths": [
            "low-latency first audible speech for streaming text",
            "long-form single-speaker generation around the 10 minute range",
            "useful design reference for live narration or voice-agent flows",
        ],
        "limitations": [
            "not recommended by the project for commercial or real-world applications without more testing",
            "non-English output may be unpredictable",
            "voice prompts are embedded to reduce deepfake risk, limiting custom voice control",
            "not yet wired into KVAE render",
        ],
        "kvae_use": [
            "treat as research-only for Korean until local A/B tests prove quality",
            "borrow the streaming architecture idea, not production promises",
            "keep AI disclosure and anti-impersonation review enabled",
        ],
    },
    {
        "id": "resemble_sts",
        "name": "Resemble AI Speech-to-Speech",
        "provider": "Resemble AI",
        "source_url": "https://www.resemble.ai/products/speech-to-speech",
        "model_url": "https://docs.resemble.ai/",
        "license": "commercial service terms",
        "kvae_status": "external_production_service",
        "backend_role": "speech_to_speech_target_voice_service",
        "parameters": "cloud service",
        "runtime": "API/service integration",
        "korean_support": "provider/language support must be checked per project and target voice",
        "strengths": [
            "speech-to-speech preserves source performance timing and delivery",
            "target voice identity is converted through licensed service voices",
            "good external answer for the exact task KVAE should not fake internally yet",
        ],
        "limitations": [
            "requires service account and target voice rights",
            "private voice data leaves local machine unless on-prem deployment is arranged",
            "not an open KVAE backend",
        ],
        "kvae_use": [
            "external replacement for different human speaker conversion",
            "KVAE prepares clean Korean source WAV and reviews returned audio",
            "require consent, terms review, and AI disclosure",
        ],
    },
    {
        "id": "elevenlabs_voice",
        "name": "ElevenLabs Korean TTS and Voice Cloning",
        "provider": "ElevenLabs",
        "source_url": "https://elevenlabs.io/text-to-speech/korean",
        "model_url": "https://elevenlabs.io/voice-cloning",
        "license": "commercial service terms",
        "kvae_status": "external_production_service",
        "backend_role": "cloud_korean_tts_and_voice_clone_service",
        "parameters": "cloud service",
        "runtime": "web/API service integration",
        "korean_support": "official Korean TTS product page exists",
        "strengths": [
            "production cloud UX and broad creator adoption",
            "Korean TTS is offered as a product path",
            "voice cloning and professional voice workflows are available through the service",
        ],
        "limitations": [
            "requires service terms, account, and potentially paid usage",
            "not local-first and not open-source",
            "private voice data may be uploaded to a third-party service",
        ],
        "kvae_use": [
            "external fallback when the user needs polished cloud Korean voices quickly",
            "KVAE should still normalize Korean scripts and review returned WAVs",
            "require consent, privacy review, and disclosure metadata",
        ],
    },
    {
        "id": "vibevoice_asr",
        "name": "VibeVoice-ASR",
        "provider": "Microsoft",
        "source_url": "https://github.com/microsoft/VibeVoice",
        "model_url": "https://huggingface.co/microsoft/VibeVoice-ASR",
        "license": "MIT",
        "kvae_status": "external_review_candidate",
        "backend_role": "long_form_asr_and_diarization_candidate",
        "parameters": "7B",
        "runtime": "GPU container recommended; Transformers integration is available according to project docs",
        "korean_support": "supports over 50 languages and reports Korean evaluation results",
        "strengths": [
            "60-minute single-pass transcription",
            "speaker, timestamp, and content structure",
            "customized hotword support",
            "useful for long Korean recording review and transcript alignment",
        ],
        "limitations": [
            "heavy 7B ASR runtime",
            "external to KVAE's current standard-library core",
            "requires separate accuracy testing on the user's Korean recordings",
        ],
        "kvae_use": [
            "candidate for future kva review-audio long-form backend",
            "use for diarized transcript review when Whisper chunking loses global context",
            "keep transcript outputs local when private voices are involved",
        ],
    },
]


TTS_BACKEND_IDS = tuple(backend["id"] for backend in TTS_BACKENDS)


def list_tts_backends(*, production_only: bool = False) -> list[dict[str, Any]]:
    backends = [
        backend
        for backend in TTS_BACKENDS
        if not production_only or backend["kvae_status"] == "integrated_default"
    ]
    return copy.deepcopy(backends)


def get_tts_backend(backend_id: str) -> dict[str, Any]:
    for backend in TTS_BACKENDS:
        if backend["id"] == backend_id:
            return copy.deepcopy(backend)
    raise KeyError(f"Unknown TTS backend: {backend_id}")


def build_tts_backend_report(
    *,
    backend_id: str | None = None,
    production_only: bool = False,
) -> dict[str, Any]:
    if backend_id:
        backends = [get_tts_backend(backend_id)]
    else:
        backends = list_tts_backends(production_only=production_only)
    return {
        "schema_version": "kva.tts_backends.v1",
        "created_at": dt.datetime.now(dt.UTC).isoformat(),
        "decision": (
            "Use VoxCPM2 as the current KVAE render default. Evaluate MOSS-TTS-Nano and CosyVoice3 as "
            "open local candidates. Keep F5-TTS, IndexTTS2, Fish Audio S2, and VibeVoice-Realtime behind "
            "research/license gates until Korean quality and usage rights are proven. Use cloud services "
            "only as explicit external handoffs."
        ),
        "privacy_policy": (
            "Private reference voices, generated private-speaker WAV files, and model checkpoints stay "
            "outside the public repository."
        ),
        "counts": _count_backends(backends),
        "backends": backends,
    }


def _count_backends(backends: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for backend in backends:
        status = backend["kvae_status"]
        counts[status] = counts.get(status, 0) + 1
    return counts
