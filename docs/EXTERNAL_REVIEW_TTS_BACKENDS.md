# External Review: MOSS-TTS-Nano, VoxCPM, VibeVoice

[Korean document](EXTERNAL_REVIEW_TTS_BACKENDS.ko.md)

This review covers three voice AI repositories and how KVAE should use them.

## Decision

KVAE should keep VoxCPM2 as the current primary render backend, evaluate MOSS-TTS-Nano as a lightweight CPU/ONNX fallback candidate, and keep VibeVoice-Realtime as Korean research only. VibeVoice-ASR is useful as a separate future candidate for long-form transcript review.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine tts-backends
python -m kva_engine tts-backends --production-only
python -m kva_engine tts-backends --id moss_tts_nano --compact
```

## 1. MOSS-TTS-Nano

Repository: https://github.com/OpenMOSS/MOSS-TTS-Nano

Local review snapshot:

- Git commit: `64380f81651d89cc18741a247e3feb3ec33ba344`
- License: Apache-2.0

Observed traits:

- 0.1B parameter multilingual speech generation model.
- Korean is listed as one of 20 supported languages.
- CPU-friendly and streaming-oriented.
- ONNX CPU inference path is available and avoids PyTorch during inference.
- Voice cloning with prompt audio is the main workflow.
- Fine-tuning code is provided.

KVAE value:

- Good candidate for low-resource, offline, CPU-only Korean speech experiments.
- Useful fallback direction if users cannot run VoxCPM2 on a GPU.
- Its ONNX path is attractive for a future simpler Windows installer.

Boundary:

- Not yet wired into `kva render`.
- Korean quality must be tested with KVAE review reports before it is promoted.
- Dependency setup can still be non-trivial on Windows because text normalization packages may need extra handling.

## 2. VoxCPM / VoxCPM2

Repository: https://github.com/OpenBMB/VoxCPM

Local review snapshot:

- Git commit: `19b6bf7590025418821a86dcb817504e0ad7e5df`
- License: Apache-2.0

Observed traits:

- VoxCPM2 is the current major release.
- 2B parameters, 30 languages, and Korean is officially listed.
- Supports voice design, controllable voice cloning, prompt/audio continuation cloning, 48 kHz output, streaming, LoRA, and full fine-tuning.
- Repository describes code and weights as Apache-2.0 and commercial-ready.
- Normal local runtime expects a CUDA-class environment; the docs mention Python >=3.10,<3.13, PyTorch >=2.5, and CUDA >=12.

KVAE value:

- Already matches KVAE's existing `kva render --engine voxcpm` path.
- Best current open backend for Korean private reference-voice experiments in this repository.
- Should remain the default while MOSS and VibeVoice are evaluated.

Boundary:

- Voice cloning can be misused; every output needs consent, provenance, and AI disclosure.
- Voice design and controllable cloning can vary between runs, so KVAE should keep `kva review-audio` and human A/B listening in the loop.
- It should not be used to promise convincing child/creature/unrelated actor voices.

## 3. VibeVoice

Repository: https://github.com/microsoft/VibeVoice

Local review snapshot:

- Git commit: `e73d1e17c3754f046352014856a922f8208fb5d3`
- License: MIT

Observed traits:

- VibeVoice is a family of voice AI models covering ASR and TTS research.
- The repository says earlier VibeVoice-TTS code was removed after misuse concerns.
- VibeVoice-Realtime-0.5B is available as a lightweight streaming TTS model.
- Realtime TTS is primarily English; Korean is provided only as an experimental multilingual exploration voice.
- The docs do not recommend VibeVoice for commercial or real-world applications without further testing.
- VibeVoice-ASR supports 60-minute single-pass transcription, speaker/timestamp/content structure, hotwords, and over 50 languages.

KVAE value:

- VibeVoice-Realtime is useful as a research reference for streaming TTS architecture.
- VibeVoice-ASR is a useful candidate for long Korean recordings where chunked ASR loses speaker/context continuity.

Boundary:

- Do not make VibeVoice-Realtime the default Korean TTS backend.
- Do not use it as a commercial Korean production path without local testing and safety review.
- Treat ASR outputs as review drafts that still need human transcript correction.

## KVAE Changes

- Added `kva tts-backends` to expose reviewed backend candidates.
- Added `korean_tts_backend_selection` route to `kva capabilities`.
- Added `long_form_asr_and_diarization` route to `kva capabilities`.
- Kept VoxCPM2 as the production default.
- Marked MOSS-TTS-Nano and VibeVoice as candidates rather than shipped backends.
