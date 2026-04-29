# Korean Voice Acting Engine

[Korean README](README.ko.md)

Korean Voice Acting Engine, or KVAE, is a local-first toolkit for Korean speech. Its practical product promise is to help users record or generate Korean voice, polish it for clarity, and prepare it for real creator use cases while keeping private voice data on the user's own machine.

KVAE no longer treats "one adult voice becomes any child, creature, or unrelated actor" as the default public promise. Those directions remain research experiments. The current useful path is Korean voice cleanup, announcer-style clarity, and presets for shorts, drama, documentary, announcements, education, and narration.

KVAE also aims to turn major-studio voice and sound-design workflows into a free creator tool. The engine should not copy copyrighted studio sounds; it should reproduce the method: acting direction, source collection, Foley, animal/synthetic layers, transformation, mixing, review, attribution, and disclosure.

## Why This Exists

Most text-to-speech systems can read text. KVAE is trying to do something more specific: understand Korean first, preserve the speaker's consent and ownership, and then apply voice acting roles in a repeatable local workflow.

Korean speech needs careful handling of numbers, dates, English abbreviations, particles, punctuation, sentence endings, rhythm, and pronunciation. If those details are wrong, the result sounds foreign or mechanical even when the base voice is good.

KVAE therefore treats Korean normalization, voice profiles, local training preparation, voice polish, render, and review as one engine.

## Current Production Capabilities

- Korean text normalization for numbers, English, symbols, dates, times, phone numbers, and particles
- `speech_text`, `phoneme_text`, normalization trace, and SSML generation
- Korean voice polish through `kva polish`
- Use-case presets for cleanup, announcer, shorts, drama, and documentary audio
- Audio review with quality gates, optional Whisper ASR, CER, and WER
- Long recording segmentation, Korean recording scripts, transcript review TSVs, and deterministic dataset splits
- Built-in public Korean AI voice catalog with source, license, attribution, and AI-voice disclosure metadata
- Local voice profile resolution through `configs/default_voice.local.json`
- Safety-oriented manifests for consent, privacy, and redistribution boundaries
- Capability routing through `kva capabilities`
- Persona-aware Korean prompt coverage route for NVIDIA Nemotron-Personas-Korea
- Reviewed TTS/ASR backend registry through `kva tts-backends`

## External-Routed Or Research Workflows

KVAE no longer presents child, wolf, monster, dinosaur, or unrelated-actor conversion as normal product capability. Those requests are routed:

- Different human speaker: external speech-to-speech tools with consented target voices
- Child or age-transformed voice: licensed Korean AI voice libraries or a human actor
- Creature, monster, wolf, or dinosaur: sound-design tools, DAWs, Foley, animal/synthetic layers, and license-safe source libraries
- Heavy noise, echo, or reverb repair: specialist dialogue repair tools
- Final video dubbing and subtitle assembly: video/audio editors
- Voice-Pro: external GPLv3 WebUI for experiments and artifact exchange, not vendored code
- MOSS-TTS-Nano: Apache-2.0 CPU/ONNX research candidate for lightweight local Korean TTS fallback
- VibeVoice: MIT research candidate; Realtime TTS is not production Korean, while ASR may help long-form transcript review
- Narrator AI CLI Skill and Open Generative AI: external video narration, visual generation, and lip-sync tools, not KVAE core dependencies

The older `kva convert`, `kva voice-lab`, `kva vocal-tract`, and `kva creature-design` commands remain available as inspectable research and planning tools, not as the default product promise.

## Install

```powershell
git clone https://github.com/sinmb79/korean-voice-acting-engine.git
cd korean-voice-acting-engine
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

KVAE currently uses only the Python standard library for its core tests. The production path is Korean preparation, recording review, and voice polish. Optional workflows may still use `ffmpeg`, Whisper, and a local VoxCPM environment when explicitly selected.

## Quick Start

Normalize Korean text into a speech script:

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine normalize --file data\sample_input.txt --out outputs\sample.speech.json
```

Apply a voice acting role:

```powershell
python -m kva_engine cast --file data\sample_input.txt --role old_storyteller --out outputs\sample.cast.json
```

Create SSML and a generation manifest:

```powershell
python -m kva_engine ssml --file data\sample_input.txt --out outputs\sample.ssml.json
python -m kva_engine manifest --script outputs\sample.speech.json --role old_storyteller --out outputs\sample.manifest.json
```

Check whether a request belongs inside KVAE or should be routed to a specialist program:

```powershell
python -m kva_engine capabilities --production-only
python -m kva_engine capabilities --task child_or_age_voice --compact
```

Inspect reviewed TTS and ASR backend candidates:

```powershell
python -m kva_engine tts-backends --production-only
python -m kva_engine tts-backends --id moss_tts_nano --compact
python -m kva_engine tts-backends --id vibevoice_asr --compact
```

Polish a Korean voice recording for a practical use case:

```powershell
python -m kva_engine polish `
  --input my_voice.wav `
  --preset announcer `
  --out outputs\my_voice.announcer.wav `
  --manifest-out outputs\my_voice.announcer.json
```

Research-only: generate multiple experimental candidates from one recording:

```powershell
python -m kva_engine voice-lab `
  --input my_voice.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --engine native `
  --expected-file script.txt `
  --asr-model base
```

Research-only: inspect the anatomical source-filter design for a character voice:

```powershell
python -m kva_engine vocal-tract --role dinosaur_giant_roar --compact
```

Show benchmark lessons adopted from professional voice tools:

```powershell
python -m kva_engine benchmarks --compact
```

Planning-only: inspect the source-library policy and a creature sound-design recipe:

```powershell
python -m kva_engine source-library --compact
python -m kva_engine source-library --scan-dir sources\creature --out outputs\source-library.scan.json
python -m kva_engine creature-design --role dinosaur_giant_roar --compact
```

Review the generated audio:

```powershell
python -m kva_engine review-audio `
  --audio outputs\monster.wav `
  --expected-file script.txt `
  --asr-model base `
  --role monster_deep_clear `
  --out outputs\monster.review.json
```

Review whether the audio actually matches the requested character role:

```powershell
python -m kva_engine review-character `
  --audio outputs\monster.wav `
  --role monster_deep_clear `
  --out outputs\monster.character-review.json
```

List public Korean AI voice options:

```powershell
python -m kva_engine public-voices
python -m kva_engine voice-profile public:mms-tts-kor
```

Check the local runtime and safety setup:

```powershell
python -m kva_engine doctor --voice-profile public:mms-tts-kor
```

## Codex Training Workflow

KVAE is intended to be developed and refined through Codex running local commands on the user's machine.

The intended loop is:

1. Record private Korean voice data locally.
2. Store the private voice profile outside the public repository.
3. Use Codex to run KVAE training, conversion, render, and review commands.
4. Inspect generated WAV files and review JSON reports.
5. Improve Korean normalization, role presets, and training data.
6. Commit only source code, public examples, and documentation to GitHub.

Prepare a local KVA-native voice model from a private registry:

```powershell
python -m kva_engine train-native `
  --registry C:\Users\you\workspace\shared-voices `
  --profile-id my-voice-profile `
  --out outputs\family_voice_training\kva_native_voice_model.json
```

Check a raw recording before training:

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

Split a long recording into auditable training segments:

```powershell
python -m kva_engine split-recording `
  --audio C:\Users\you\workspace\shared-voices\my-voice\sessions\session.wav `
  --transcript-file C:\Users\you\workspace\shared-voices\my-voice\sessions\session.txt `
  --out-dir outputs\segments
```

Create a Korean recording session script and a stable dataset split:

```powershell
python -m kva_engine recording-plan --out-dir outputs\recording-plan --target-minutes 30
python -m kva_engine transcript-review --manifest outputs\segments\segments_manifest.json --out outputs\segments\transcript_review.tsv
python -m kva_engine dataset-split --manifest outputs\segments\segments_manifest.json --out outputs\dataset_split.json
```

Private recordings, datasets, LoRA checkpoints, and generated WAV files are intentionally excluded from git.

## Documentation

- [Codex Training Workflow](docs/CODEX_TRAINING_WORKFLOW.md)
- [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)
- [Dataset Preparation Workflow](docs/DATASET_PREP_WORKFLOW.md)
- [KVAE Render Engine](docs/KVAE_RENDER_ENGINE.md)
- [Korean Voice Polish Engine](docs/KOREAN_VOICE_POLISH_ENGINE.md)
- [Capability Routing](docs/CAPABILITY_ROUTING.md)
- [External Review: Voice-Pro And Nemotron-Personas-Korea](docs/EXTERNAL_REVIEW_VOICE_PRO_NEMOTRON.md)
- [External Review: Quark SFX, Narrator AI CLI Skill, Open Generative AI](docs/EXTERNAL_REVIEW_QUARK_NARRATOR_OPEN_GENERATIVE.md)
- [External Review: MOSS-TTS-Nano, VoxCPM, VibeVoice](docs/EXTERNAL_REVIEW_TTS_BACKENDS.md)
- [KVAE Convert Engine](docs/KVAE_CONVERT_ENGINE.md)
- [Vocal Tract Voice Design](docs/VOCAL_TRACT_ENGINE.md)
- [Voice Lab Workflow](docs/VOICE_LAB_WORKFLOW.md)
- [Recording Segmentation Workflow](docs/RECORDING_SEGMENTATION.md)
- [KVAE Review Engine](docs/KVAE_REVIEW_ENGINE.md)
- [Character Review Engine](docs/CHARACTER_REVIEW_ENGINE.md)
- [Professional Voice Product Benchmark Plan](docs/PRO_VOICE_BENCHMARK_PLAN.md)
- [Professional Voice Benchmark Implementation](docs/PRO_VOICE_BENCHMARK_IMPLEMENTATION.md)
- [Creator Sound Design Engine](docs/CREATOR_SOUND_DESIGN_ENGINE.md)
- [Public Korean AI Voice Catalog](docs/PUBLIC_VOICE_CATALOG.md)
- [Release Quality Gates](docs/RELEASE_QUALITY_GATES.md)
- [Native Training Direction](docs/KVA_NATIVE_TRAINING.md)
- [Family Voice Training](docs/FAMILY_VOICE_TRAINING.md)
- [Safety Policy](docs/SAFETY_POLICY.md)
- [Secure Development](docs/SECURE_DEVELOPMENT.md)

## Privacy And Safety

KVAE is a public engine repository, not a public voice dataset.

The repository should contain:

- source code
- public examples
- documentation
- tests

The repository should not contain:

- private voice recordings
- personal voice datasets
- LoRA checkpoints
- trained private model weights
- generated voice outputs that identify a private speaker
- local config files such as `configs/*.local.json`

Voice is not just sample data. It is personal identity. KVAE's default workflow keeps the engine public and the person private.

## Verification

Current local verification command:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src
python -m kva_engine doctor --voice-profile public:mms-tts-kor
```

## License

Apache-2.0
