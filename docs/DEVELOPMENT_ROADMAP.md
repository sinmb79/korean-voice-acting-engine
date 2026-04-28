# Development Roadmap

[Korean document](DEVELOPMENT_ROADMAP.ko.md)

This roadmap exists so KVAE reports what is done and what is still missing honestly.

## Current Completion State

Done:

- Korean text normalization for numbers, English, symbols, dates, times, phone numbers, particles, and pronunciation traces
- SSML and manifest generation
- voice profile resolution for private local voices and public AI voices
- public Korean AI voice catalog with source, license, attribution, and AI disclosure metadata
- license-safe public voice install plans through `kva public-voices --install-plan`
- deterministic recorded-voice conversion through `kva convert`
- multi-role candidate generation through `kva voice-lab`
- named Voice Lab role groups: `default`, `dialogue`, `creature`, `narration`, `shorts`
- audio review through `kva review-audio`
- raw recording check through `kva recording-check`
- long recording segmentation through `kva split-recording`
- Korean recording session scripts through `kva recording-plan`
- deterministic train/validation/test split manifests through `kva dataset-split`
- runtime and safety diagnostics through `kva doctor`
- release quality gates and GitHub Actions CI

In short: KVAE now has a usable local CLI engine, safety metadata, review reports, and CI.

## Remaining Development Process

### Phase 1. Voice Lab Product Workflow

Status: in progress, usable v1 implemented.

Goal:

- make one input recording produce multiple character voice candidates
- write WAV, manifest, review JSON, playlist, and summary automatically
- keep the contract stable so deterministic conversion can be replaced by neural speech-to-speech later

Next refinements:

- add per-role intelligibility thresholds
- add side-by-side comparison reports
- add listening-score fields for human review

### Phase 2. Public Voice Install And Render Adapters

Status: metadata catalog and install plans implemented; actual render adapters still missing.

Goal:

- let users install approved public Korean AI voices intentionally
- require license acknowledgement before downloading external models
- keep source, license, attribution, and AI voice disclosure in every manifest

Needed:

- provider adapters for MMS, Piper, Coqui, and other license-safe models
- offline cache layout under a user-selected local folder

### Phase 3. Neural Speech-To-Speech Backend

Status: CLI contract ready; neural backend not complete.

Goal:

- preserve a user's acting timing, pauses, and emotion
- change voice identity into selected character voices
- outperform deterministic pitch/EQ conversion

Needed:

- backend interface for RVC/FreeVC/so-vits-svc/KVAE-STS
- local model registry
- training/evaluation split
- objective review plus human listening review

### Phase 4. Korean Acting Dataset Expansion

Status: recording-check, recording-plan, split-recording, and dataset-split v1 exist; reviewed larger datasets still needed.

Goal:

- collect 30-120 minutes of clean Korean voice per speaker
- include role-specific acting data
- cover Korean numbers, dates, English abbreviations, endings, particles, and difficult pronunciation

Needed:

- transcript correction workflow
- backend-specific dataset export formats

### Phase 5. Local App UI

Status: CLI only.

Goal:

- make KVAE usable by non-developers
- drag in a WAV
- choose roles
- listen, compare, and export
- show source/license/AI voice disclosure clearly

Needed:

- local desktop or web UI
- waveform preview
- role preset editor
- review dashboard

### Phase 6. Release Packaging

Status: wheel build smoke passed; full release workflow still needed.

Goal:

- install cleanly
- run `kva doctor`
- pass CI
- ship docs in English by default and Korean as optional docs

Needed:

- release checklist automation
- signed release artifacts
- versioned changelog
- beginner examples that do not contain private voice data

## Definition Of Done

KVAE is not "done" until a user can:

1. install it,
2. run `kva doctor`,
3. select a private or public Korean voice profile,
4. provide Korean text or a recorded performance,
5. generate multiple voice candidates,
6. inspect review reports,
7. see source/license/AI disclosure,
8. keep private voice data out of public repos,
9. refine roles and thresholds to their own taste.
