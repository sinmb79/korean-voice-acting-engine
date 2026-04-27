# Voice Lab Workflow

[한국어 문서](VOICE_LAB_WORKFLOW.ko.md)

`kva voice-lab` is the product-style workflow for users who want to record once and generate multiple character voice candidates.

It wraps:

1. voice conversion
2. per-role manifest writing
3. optional audio review
4. playlist generation
5. summary report generation

## Quick Start

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-lab `
  --input my_performance.wav `
  --out-dir outputs\voice-lab-demo `
  --group default `
  --expected-file script.txt `
  --asr-model base
```

The output folder contains:

- `*.wav`
- `*.result.json`
- `*.manifest.json`
- `*.review.json`
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
  --dry-run
```

## Recommended Roles

Named groups:

- `default`: balanced starter set
- `dialogue`: narrator, teacher, storyteller, villain, child
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

## Remaining Development

`voice-lab` is intentionally built around a stable contract. The deterministic conversion engine can later be replaced or supplemented with:

- neural speech-to-speech conversion
- public voice model render adapters
- a local GUI
- per-role Korean intelligibility thresholds
- larger acting datasets
