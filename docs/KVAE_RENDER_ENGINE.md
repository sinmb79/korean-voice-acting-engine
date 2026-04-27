# KVAE Render Engine

KVAE now owns the full local render path:

```text
UTF-8 Korean text file
  -> Korean normalization
  -> voice profile resolution
  -> VoxCPM LoRA generation
  -> role pitch/speed transform
  -> loudness normalization
  -> WAV + manifest
```

## Quick Start

On Windows, use a UTF-8 text file for Korean input. Passing Korean directly as a PowerShell argument can be affected by console encoding.

```powershell
cd C:\Users\you\workspace\KVAE
$env:PYTHONPATH = "src"

python -m kva_engine render `
  --file script.txt `
  --role old_storyteller `
  --out outputs\old_storyteller.wav
```

The default local voice is read from:

```text
configs/default_voice.local.json
```

That file is intentionally ignored by git because it points to private voice assets.

For recorded voice input instead of text input, use `kva convert`.

```powershell
python -m kva_engine convert --input my_acting.wav --role monster_deep --out monster.wav
```

## Useful Roles

```powershell
python -m kva_engine render --file script.txt --role calm_narrator --out outputs\calm.wav
python -m kva_engine render --file script.txt --role documentary --out outputs\documentary.wav
python -m kva_engine render --file script.txt --role news_anchor --out outputs\news.wav
python -m kva_engine render --file script.txt --role old_storyteller --out outputs\old.wav
python -m kva_engine render --file script.txt --role villain_low --out outputs\villain.wav
python -m kva_engine render --file script.txt --role childlike_fast --out outputs\child.wav
python -m kva_engine render --file script.txt --role wolf_growl --out outputs\wolf.wav
python -m kva_engine render --file script.txt --role monster_deep --out outputs\monster.wav
python -m kva_engine render --file script.txt --role dinosaur_giant --out outputs\dinosaur.wav
python -m kva_engine render --file script.txt --role child_bright --out outputs\child-bright.wav
```

Each role writes its controls into the manifest under:

```text
synthesis.role_controls
synthesis.role_postprocess
```

## Dry Run

Use dry run to check which voice, model, LoRA, and output path KVAE will use.

```powershell
python -m kva_engine render `
  --file script.txt `
  --role old_storyteller `
  --out outputs\old.wav `
  --json-out outputs\old.plan.json `
  --dry-run
```

## Current Limit

A very short LoRA or reference voice can prove that the KVAE-owned path works, but production-quality Korean voice acting needs more clean recordings and a larger reviewed transcript set.
