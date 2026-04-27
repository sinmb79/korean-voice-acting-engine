# Release Quality Gates

[한국어 문서](RELEASE_QUALITY_GATES.ko.md)

KVAE is not complete just because code runs. A release must pass runtime, privacy, documentation, and audio-review gates.

## Required Commands

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src
python -m kva_engine doctor --voice-profile public:mms-tts-kor
```

## Privacy Gate

Do not release if any public file contains:

- private local usernames or absolute private voice paths
- private voice recordings
- private LoRA or model checkpoints
- generated WAV/MP3/FLAC/M4A files
- local token or API key strings

Recommended Windows check:

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.md,*.json,*.jsonl,*.txt -Path . |
  Where-Object { $_.FullName -notmatch '\\.git\\|\\outputs\\|\\__pycache__\\|default_voice\.local\.json$' } |
  Select-String -Pattern 'C:\Users\your-private-name','github_token_prefix' -SimpleMatch
```

## Runtime Gate

`kva doctor` should show:

- Python 3.11+
- public voice catalog available
- `ffmpeg` and `ffprobe` available for audio conversion/review workflows
- private voice profiles ignored by git
- optional Whisper availability when ASR review is expected

## Audio Gate

Generated audio should be reviewed with:

```powershell
python -m kva_engine review-audio `
  --audio outputs\sample.wav `
  --expected-file script.txt `
  --asr-model base `
  --role calm_narrator `
  --out outputs\sample.review.json
```

Minimum checks:

- WAV exists
- sample rate and channel count are expected
- peak is not clipping
- RMS is not too low
- silence ratio is not excessive
- CER/WER are acceptable for the chosen role

## Documentation Gate

Public documentation defaults to English. Korean documentation is provided as optional `.ko.md` files where helpful.

Every public AI voice entry must include:

- source URL
- license
- commercial-use flag
- attribution
- AI voice disclosure

## Known Imperfections

KVAE still needs deeper neural training integration, a user-facing app, and larger Korean acting datasets. Until those land, each release must be honest about current limits and preserve a clear path for users to customize roles, voices, and quality thresholds.
