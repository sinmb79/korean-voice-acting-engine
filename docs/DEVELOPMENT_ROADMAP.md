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
- practical Korean voice polish through `kva polish`
- capability routing through `kva capabilities`
- reviewed TTS/ASR backend registry through `kva tts-backends`
- VoxCPM2 set as the current render default with MOSS-TTS-Nano and VibeVoice tracked as candidates
- Korean evaluation suite through `kva eval-suite`
- top-tier release gates through `kva product-quality`
- persona-script coverage route for NVIDIA Nemotron-Personas-Korea
- external Voice-Pro route as a separate GPLv3 WebUI, not vendored code
- external Quark SFX, Narrator AI CLI Skill, and Open Generative AI reviews with safe routing boundaries
- experimental deterministic recorded-voice conversion through `kva convert`
- experimental multi-role candidate generation through `kva voice-lab`
- research source-filter vocal tract voice design through `kva vocal-tract`
- professional voice product benchmark reporting through `kva benchmarks`
- major-studio voice acting and sound-design technique catalog through `kva benchmarks`
- license-safe source-library schema through `kva source-library`
- creature sound-design recipes through `kva creature-design`
- experimental nonhuman bioacoustic dinosaur rendering
- named Voice Lab role groups: `default`, `dialogue`, `creature`, `narration`, `shorts`
- audio review through `kva review-audio`
- raw recording check through `kva recording-check`
- long recording segmentation through `kva split-recording`
- Korean recording session scripts through `kva recording-plan`
- TSV transcript correction workflow through `kva transcript-review`
- deterministic train/validation/test split manifests through `kva dataset-split`
- runtime and safety diagnostics through `kva doctor`
- release quality gates and GitHub Actions CI

In short: KVAE now has a usable local CLI engine, safety metadata, review reports, voice polish presets, capability routing, and CI.

## Product Scope Correction

The current public KVAE product should not promise that one adult recording can become a convincing child, creature, dinosaur, or unrelated professional actor. Those remain research directions.

The practical product promise is:

- take a Korean voice recording or generated Korean narration,
- keep the speaker identity,
- improve clarity, tonal balance, loudness, and delivery readiness,
- provide presets for announcer, shorts, drama, documentary, and cleanup use cases,
- keep private voice assets local.

Requests outside that promise should be routed:

- different human speaker: external speech-to-speech or licensed target voice provider
- child or age-transformed voice: licensed Korean AI voice library or human actor
- creature/dinosaur/monster: sound-design tool, DAW, Foley, animal/synthetic layers, and KVAE source metadata
- heavy noise/echo/reverb repair: specialist dialogue repair tool
- final video dubbing/subtitle assembly: video editor
- local all-in-one open-source experiments: Voice-Pro as a separate GPLv3 tool with WAV/SRT/TXT/JSON artifact exchange only
- reviewed TTS candidates: VoxCPM2 as current default, MOSS-TTS-Nano as CPU/ONNX fallback candidate, VibeVoice as research-only for Korean TTS and candidate long-form ASR
- Korean persona diversity: NVIDIA Nemotron-Personas-Korea as text-only persona coverage, not voice data

## Remaining Development Process

### Phase 0. Backend And External Tool Registry

Status: v1 implemented through `kva capabilities` and `kva tts-backends`.

Goal:

- prevent KVAE from confusing shipped features with interesting external tools
- track license, runtime, Korean support, and safety boundaries before integration
- keep VoxCPM2 as the default until another backend passes Korean quality review

Next refinements:

- add benchmark score fields for Korean intelligibility, speaker similarity, latency, and stability
- add local machine feasibility checks for each backend
- add a backend smoke-test harness that can render one private test sentence without committing the audio
- run the full `kva eval-suite` against VoxCPM2, MOSS-TTS-Nano, and CosyVoice3 on this machine
- collect human listening scores and promote only candidates that pass `kva product-quality`

### Phase 1. Korean Voice Polish Product Workflow

Status: usable v1 implemented.

Goal:

- make one Korean voice recording more usable without pretending it is a different speaker
- provide practical presets for announcer, shorts, drama, documentary, education, and cleanup
- write WAV and manifest files with explicit safety boundaries
- make output easy to review and compare

Next refinements:

- add loudness targets by platform
- add optional transcript-aware pronunciation review
- add denoise and room-tone profiling
- add batch polish for project folders

### Phase 2. Voice Lab Product Workflow

Status: research-only v1 implemented.

Goal:

- make one input recording produce multiple practical voice-treatment candidates
- write WAV, manifest, review JSON, playlist, and summary automatically
- keep unrealistic child/creature/actor conversion clearly marked as experimental

Next refinements:

- add per-role intelligibility thresholds
- add side-by-side comparison reports
- add listening-score fields for human review

### Phase 3. Public Voice Install And Render Adapters

Status: metadata catalog and install plans implemented; actual render adapters still missing.

Goal:

- let users install approved public Korean AI voices intentionally
- require license acknowledgement before downloading external models
- keep source, license, attribution, and AI voice disclosure in every manifest

Needed:

- provider adapters for MMS, Piper, Coqui, and other license-safe models
- offline cache layout under a user-selected local folder

### Phase 4. Neural Speech-To-Speech Backend

Status: external-routed for production; internal neural backend not complete.

Research goal:

- preserve a user's acting timing, pauses, and emotion
- change voice identity into selected character voices
- outperform deterministic pitch/EQ conversion
- reuse the vocal-tract design contract for controllable source/filter and neural rendering
- model the actor-proven variability of one human voice as programmable source, filter, articulation, and performance controls
- separate human character conversion from fully nonhuman bioacoustic rendering when the target should not retain speech identity

Needed:

- backend interface for RVC/FreeVC/so-vits-svc/KVAE-STS
- WORLD/pyworld analysis-synthesis adapter for F0, spectral envelope, and aperiodicity
- local model registry
- training/evaluation split
- objective review plus human listening review

### Phase 5. Korean Acting Dataset Expansion

Status: recording-check, recording-plan, split-recording, transcript-review, and dataset-split v1 exist; reviewed larger datasets still needed.

Goal:

- collect 30-120 minutes of clean Korean voice per speaker
- include role-specific acting data
- cover Korean numbers, dates, English abbreviations, endings, particles, and difficult pronunciation

Needed:

- backend-specific dataset export formats

### Phase 6. Creator Sound Design Engine

Status: benchmark catalog, source-library scan/validation, recipe CLI, and dinosaur render entrypoint started; full source-library manager and multi-creature layer renderer still missing.

Goal:

- benchmark how major studios build voices and sound effects
- turn those methods into a free Korean-friendly creator workflow
- keep every source layer license-safe and attributable
- separate human character conversion from fully nonhuman creature design
- let one private performance guide timing and energy without leaking identity when the target is nonhuman

Needed:

- `kva source-library add`
- waveform indexing, tags, and source provenance checks
- broader `kva creature-design` render support for wolf, monster, alien, and Foley-heavy roles
- Foley and action spotting for video clips
- A/B/C candidate generation plus human listening score
- local UI for compare, bypass, source/license display, and export

### Phase 7. Local App UI

Status: CLI only.

Goal:

- make KVAE usable by non-developers
- drag in a WAV
- choose polish/use-case presets
- listen, compare, and export
- show source/license/AI voice disclosure clearly

Needed:

- local desktop or web UI
- waveform preview
- polish/use-case preset editor
- review dashboard

### Phase 8. Release Packaging

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
5. generate polished use-case candidates,
6. inspect review reports,
7. see source/license/AI disclosure,
8. keep private voice data out of public repos,
9. refine roles and thresholds to their own taste.
