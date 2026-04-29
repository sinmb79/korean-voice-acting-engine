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
            "Use VoxCPM2 as the current KVAE render default. Evaluate MOSS-TTS-Nano as a lightweight "
            "CPU fallback candidate. Keep VibeVoice-Realtime as Korean research only, and consider "
            "VibeVoice-ASR for future long-form transcript review."
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
