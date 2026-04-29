# Product Excellence Plan

[Korean document](PRODUCT_EXCELLENCE_PLAN.ko.md)

KVAE's next goal is not to pretend that every voice transformation is solved. The goal is to become a top-tier Korean-first voice production engine by making every output measurable, reviewable, safe, and easy to improve.

## Research Summary

Reviewed external directions:

- [VoxCPM2](https://github.com/OpenBMB/VoxCPM): strongest current local default for KVAE because it is Apache-2.0, officially supports Korean, and includes voice design, controllable cloning, LoRA, and 48 kHz output.
- [MOSS-TTS-Nano](https://github.com/OpenMOSS/MOSS-TTS-Nano): important CPU/ONNX fallback candidate for lightweight local use.
- [CosyVoice](https://github.com/FunAudioLLM/CosyVoice): Apache-2.0 multilingual zero-shot candidate with Korean coverage and streaming-oriented design.
- [F5-TTS](https://github.com/SWivid/F5-TTS): useful research benchmark, but the repository states pretrained models are CC-BY-NC, so it is not a production default.
- [IndexTTS2](https://github.com/index-tts/index-tts): important reference for duration and emotion control, but it uses a custom model license and requires careful legal review.
- [Fish Speech / Fish Audio S2](https://github.com/fishaudio/fish-speech): strong quality benchmark, but commercial use requires a separate Fish Audio license.
- [Resemble AI Speech-to-Speech](https://www.resemble.ai/products/speech-to-speech): production external answer for preserving performance while changing target voice.
- [ElevenLabs Korean TTS / voice cloning](https://elevenlabs.io/text-to-speech/korean): cloud external fallback for polished creator workflows.
- [iZotope RX Dialogue Isolate](https://www.izotope.com/en/products/rx/features/dialogue-isolate) and [Adobe Enhance Speech](https://podcast.adobe.com/en/enhance-speech-v2): specialist repair tools for audio that KVAE should not over-process.

## Product Principle

Top-tier KVAE means:

- Korean-first script normalization and pronunciation planning.
- Source voice privacy by default.
- Multiple backend candidates, but only promoted after Korean evidence.
- Objective review plus human listening review.
- Clear separation between local engine, external cloud service, and research-only models.
- Every public output includes consent, provenance, license, and AI disclosure metadata.

## New Product Gates

KVAE now exposes:

```powershell
python -m kva_engine eval-suite --out-dir outputs\korean-eval-suite
python -m kva_engine product-quality --backend voxcpm2 --use-case shorts --review outputs\sample.review.json --human-scores outputs\sample.human.json
```

The release state can be:

- `ready`: all gates pass.
- `conditional`: no hard failures, but a warning remains.
- `needs_evidence`: audio review or human listening review is missing.
- `blocked`: a hard gate fails, such as non-commercial backend status for a product release.

## Evaluation Suite

The Korean evaluation suite includes prompts for:

- dates, times, numbers, money, phone numbers, and addresses
- Korean-English model names and acronyms
- shorts one-take narration
- drama breath and emotional softness
- documentary pacing
- final consonant pronunciation pairs
- consent and AI disclosure wording
- backend repeatability

Every backend candidate should render the same prompts before promotion.

## Human Listening Score

Top-tier release requires a human score file:

```json
{
  "korean_pronunciation": 4.5,
  "naturalness": 4.4,
  "emotion_fit": 4.2,
  "artifact_control": 4.5,
  "use_case_fit": 4.3,
  "overall": 4.4
}
```

Scale:

- 1: unusable
- 2: poor
- 3: acceptable draft
- 4: production usable
- 5: excellent

## Road To Top-Tier Product

1. Run VoxCPM2 against the evaluation suite with the user's private voice, storing outputs outside git.
2. Run `kva review-audio` for every sample.
3. Add human listening scores after the user listens.
4. Run `kva product-quality` to decide whether the release candidate is ready.
5. Repeat with MOSS-TTS-Nano and CosyVoice3 only after installing them in separate local environments.
6. Keep F5-TTS, IndexTTS2, and Fish Audio S2 behind non-commercial/license gates unless their production rights are cleared.
7. Build a local UI only after the backend quality gates produce reliable results.
