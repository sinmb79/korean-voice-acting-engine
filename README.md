# Korean Voice Acting Engine

[Korean README](README.ko.md)

Korean Voice Acting Engine, or KVAE, is a local-first voice acting toolkit for Korean speech. It is designed to turn Korean text and recorded voice performances into reusable voice acting outputs while keeping private voice data on the user's own machine.

The long-term goal is simple: a user records their own Korean voice, Codex helps prepare and refine the local training assets, and KVAE expands that voice into narrator, teacher, villain, child, wolf, monster, dinosaur, and other character performances.

## Why This Exists

Most text-to-speech systems can read text. KVAE is trying to do something more specific: understand Korean first, preserve the speaker's consent and ownership, and then apply voice acting roles in a repeatable local workflow.

Korean speech needs careful handling of numbers, dates, English abbreviations, particles, punctuation, sentence endings, rhythm, and pronunciation. If those details are wrong, the result sounds foreign or mechanical even when the base voice is good.

KVAE therefore treats Korean normalization, voice profiles, role design, local training, conversion, and review as one engine.

## Current Capabilities

- Korean text normalization for numbers, English, symbols, dates, times, phone numbers, and particles
- `speech_text`, `phoneme_text`, and normalization trace generation
- SSML generation
- Voice acting presets for narration, documentary, news, teaching, old storyteller, villain, AI assistant, child, wolf, monster, and dinosaur voices
- Local voice profile resolution through `configs/default_voice.local.json`
- Local render path for VoxCPM-based Korean voice generation
- Recorded voice conversion through `kva convert`
- Multi-role voice candidate workflow through `kva voice-lab`
- Source-filter vocal tract voice designs through `kva vocal-tract`
- Audio review with quality gates, optional Whisper ASR, CER, and WER
- Long recording segmentation through `kva split-recording`
- Korean recording script generation, transcript review TSVs, and deterministic dataset splits
- Built-in public Korean AI voice catalog with source, license, attribution, and AI-voice disclosure metadata
- Local training manifest and KVA-native statistical voice model preparation
- Safety-oriented manifests for consent, privacy, and redistribution boundaries

## Install

```powershell
git clone https://github.com/sinmb79/korean-voice-acting-engine.git
cd korean-voice-acting-engine
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

KVAE currently uses only the Python standard library for its core tests. Audio rendering and conversion workflows may use local tools such as `ffmpeg`, Whisper, and a local VoxCPM environment when available.

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

Convert a recorded performance into a character voice:

```powershell
python -m kva_engine convert `
  --input my_voice.wav `
  --role monster_deep_clear `
  --out outputs\monster.wav
```

Generate multiple voice candidates from one recording:

```powershell
python -m kva_engine voice-lab `
  --input my_voice.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --expected-file script.txt `
  --asr-model base
```

Inspect the anatomical source-filter design for a character voice:

```powershell
python -m kva_engine vocal-tract --role dinosaur_giant_roar --compact
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
- [KVAE Convert Engine](docs/KVAE_CONVERT_ENGINE.md)
- [Vocal Tract Voice Design](docs/VOCAL_TRACT_ENGINE.md)
- [Voice Lab Workflow](docs/VOICE_LAB_WORKFLOW.md)
- [Recording Segmentation Workflow](docs/RECORDING_SEGMENTATION.md)
- [KVAE Review Engine](docs/KVAE_REVIEW_ENGINE.md)
- [Professional Voice Product Benchmark Plan](docs/PRO_VOICE_BENCHMARK_PLAN.md)
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
