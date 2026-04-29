# Character Review Engine

[Korean document](CHARACTER_REVIEW_ENGINE.ko.md)

`kva review-character` checks whether a rendered WAV has the acoustic shape expected for a KVAE role. It is not a replacement for human listening, but it gives the engine a repeatable way to say why a result does not yet sound like the requested character.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine review-character `
  --audio outputs\dinosaur.wav `
  --role dinosaur_giant_roar `
  --out outputs\dinosaur.character-review.json
```

## Why This Exists

Advanced voice products are not just renderers. They also have review loops: target speaker similarity, clarity checks, artifact checks, and human approval. Creature tools such as Dehumaniser-style workflows also focus on whether the voice has a large nonhuman body, enough throat grit, and few clean human speech traces.

KVAE needs the same idea in a local, inspectable form. The character review engine measures coarse acoustic features and turns them into role-specific warnings.

## Metrics

The review uses deterministic WAV analysis:

- `body_index`: low-frequency body and chest/creature resonance
- `brightness_index`: high-frequency presence, air, and small-vocal-tract cues
- `grit_index`: roughness, pressure, noisy throat texture, and envelope movement
- `human_speech_trace_index`: clean human speech-formant residue
- `stability_index`: delivery-envelope stability

The role family decides what is good or bad:

- `dinosaur`: high body, low human speech trace, controlled brightness, enough throat pressure
- `monster`: high body and grit, less clean source-speaker residue
- `wolf`: body plus growl texture without excessive boom
- `child`: brighter tract and reduced adult body
- `female_lead`: brighter, lighter body, stable dialogue
- `male_lead`: composed body and controlled presence
- `narration`: balanced clarity, warmth, and stability

## Output

The JSON includes:

- `score`: 0 to 100 character-fit proxy
- `status`: `pass`, `warn`, or `fail`
- `warnings`: compact issue labels
- `features`: measured acoustic values
- `target_metrics`: role-family thresholds
- `findings`: concrete metric failures
- `development_actions`: renderer changes to try next

## Voice Lab Integration

`kva voice-lab` now writes `*.character-review.json` for each rendered candidate when review is enabled. The summary and README include a character score so users can compare candidates without opening every manifest.

## Limits

This engine does not prove a voice is artistically convincing. It catches obvious mismatches and makes regressions visible. The next step is to train role-likeness evaluators from human A/B judgments and Korean acting datasets.
