# Voice Lab Workflow

[Korean document](VOICE_LAB_WORKFLOW.ko.md)

`kva voice-lab` is the product-style workflow for users who want to record once and generate multiple character voice candidates.

It wraps:

1. voice conversion
2. per-role manifest writing
3. optional audio review
4. per-role character-fit review
5. playlist generation
6. summary report generation

The default conversion engine is `kva-native-character-v1`, KVAE's in-engine WAV renderer. Use `--engine ffmpeg` only when deliberately choosing the legacy filter path.

## Quick Start

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --engine native `
  --expected-file script.txt `
  --asr-model base
```

The output folder contains:

- `*.wav`
- `*.result.json`
- `*.manifest.json`
- `*.review.json`
- `*.character-review.json`
- `playlist.m3u`
- `voice_lab_summary.json`
- `README.md`

## Dry Run

Use dry run to inspect plans without creating audio:

```powershell
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-plan `
  --roles wolf_growl_clear,monster_deep_clear `
  --engine native `
  --dry-run
```

## Recommended Roles

Named groups:

- `default`: balanced starter set
- `dialogue`: narrator, teacher, storyteller, villain, child, original drama leads
- `drama`: original prince/lady leads plus grounded supporting roles
- `creature`: wolf, monster, dinosaur clear/heavy/fx/roar variants
- `narration`: calm, documentary, news, storyteller
- `shorts`: compact creator-oriented set

Default group roles:

- `calm_narrator`
- `wolf_growl_clear`
- `monster_deep_clear`
- `dinosaur_giant_clear`
- `child_bright`

Clear roles are preferred for dialogue. Heavy, FX, and roar roles are better treated as performance texture.

## Character Review

When review is enabled, `voice-lab` also runs `kva review-character` for each rendered candidate. The summary includes `character_score`, `character_status`, and character warnings, so a weak dinosaur or child candidate is visible even when the WAV is technically valid.

## Remaining Development

`voice-lab` is intentionally built around a stable contract. The deterministic native conversion engine can later be replaced or supplemented with:

- stronger KVAE-native neural speech-to-speech conversion
- public voice model render adapters
- a local GUI
- learned per-role Korean intelligibility and role-likeness thresholds
- larger acting datasets
