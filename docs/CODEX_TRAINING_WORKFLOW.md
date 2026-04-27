# Codex Training Workflow

[한국어 문서](CODEX_TRAINING_WORKFLOW.ko.md)

KVAE is designed so Codex can operate the local training and review loop on the user's own computer.

The repository should stay public and reusable. The user's voice data should stay private and local.

## Design Principle

Codex does not need to upload private recordings to GitHub or to any public dataset. Instead, Codex acts as the local operator:

1. Inspect the local voice profile.
2. Check recording quality.
3. Build a training manifest.
4. Prepare a KVA-native voice model record.
5. Render or convert sample voices.
6. Run audio review and transcript metrics.
7. Commit only reusable code, documentation, tests, and public examples.

## Folder Contract

Recommended private voice location:

```text
C:\Users\you\workspace\shared-voices\my-voice-profile
```

Recommended public engine location:

```text
C:\Users\you\workspace\KVAE
```

The public repository may reference local paths through ignored local config files:

```text
configs/default_voice.local.json
```

That file must not be committed.

## Step 1. Check The Voice Profile

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-profile
```

This confirms which local private voice profile KVAE will use.

## Step 2. Check Raw Recording Quality

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice-profile\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

The review checks duration, sample rate, channels, peak, RMS, silence ratio, and training-readiness warnings.

## Step 3. Prepare A Local Training Model Record

```powershell
python -m kva_engine train-native `
  --registry C:\Users\you\workspace\shared-voices `
  --profile-id my-voice-profile `
  --out outputs\family_voice_training\kva_native_voice_model.json
```

This command prepares a KVA-native statistical voice model record. It is the local metadata and acoustic-profile layer that KVAE can use as a training seed.

## Step 4. Render From Text

```powershell
python -m kva_engine render `
  --file script.txt `
  --role calm_narrator `
  --out outputs\calm_narrator.wav `
  --json-out outputs\calm_narrator.result.json `
  --manifest-out outputs\calm_narrator.manifest.json
```

When a local VoxCPM runtime is configured, this path generates Korean speech from text.

## Step 5. Convert A Recorded Performance

```powershell
python -m kva_engine convert `
  --input my_performance.wav `
  --role wolf_growl_clear `
  --out outputs\wolf_growl_clear.wav `
  --json-out outputs\wolf_growl_clear.result.json `
  --manifest-out outputs\wolf_growl_clear.manifest.json
```

This keeps the original timing and performance while applying the selected role controls.

## Step 6. Review The Output

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf_growl_clear.wav `
  --expected-file script.txt `
  --asr-model base `
  --role wolf_growl_clear `
  --out outputs\wolf_growl_clear.review.json
```

The review report records audio quality, optional Whisper ASR, CER, WER, and warnings.

## Step 7. Commit Only Public-Safe Files

Before committing:

```powershell
git status --short
python -m unittest discover -s tests
python -m compileall -q src
```

Do not commit:

- private voice recordings
- local config files
- datasets with personal speech
- LoRA checkpoints
- generated WAV/MP3/FLAC/M4A files
- private model weights

Commit:

- source code
- public examples
- tests
- English documentation
- optional Korean documentation

## Current Limitation

The current local training command prepares a KVA-native statistical voice model record. Full neural speech synthesis training still requires a configured local ML stack such as PyTorch, a Korean acoustic model, duration/pitch/energy prediction, and a vocoder.

KVAE keeps the CLI contract stable so the neural backend can be added without changing the user workflow.
