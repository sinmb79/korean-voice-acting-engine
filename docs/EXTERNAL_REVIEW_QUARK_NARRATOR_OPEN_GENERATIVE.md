# External Review: Quark SFX, Narrator AI CLI Skill, Open Generative AI

[Korean document](EXTERNAL_REVIEW_QUARK_NARRATOR_OPEN_GENERATIVE.ko.md)

This review fixes the boundary between what KVAE should absorb and what should remain an external tool or a license-gated source.

## 1. Quark Shared Sound-Effects Library

Source: https://pan.quark.cn/s/86e913fbb254

Observed share metadata:

- Share title: `百万剪辑狮的音效库`
- Approximate share size: 2.98 GB
- Total files/folders observed: 2,368
- Audio-file count observed: 2,125
- Top-level categories include animal sounds, network sounds, scene sounds, effect sounds, sports sounds, instrument sounds, weapon sounds, and action sounds.

License finding:

- No clear redistribution or commercial-use license was visible in the inspected share metadata.
- KVAE must not vendor or redistribute these sounds.

Useful ideas for KVAE:

- The category structure is useful as a source-library taxonomy reference.
- Creature and Foley workflows should separate animal, body, impact, ambience, mechanical, synthetic, and voice-controller layers.
- A sound library is only usable when every file has source, license, attribution, and redistribution metadata.

Safe application:

- Add `sound_effect_library_intake` to `kva capabilities`.
- Use `kva source-library --scan-dir <licensed-sfx-folder>` only after the user has a legally downloaded/licensed local copy.
- Treat the Quark share as reference taxonomy until license evidence is available.
- Keep third-party SFX outside the public KVAE repository.

## 2. Narrator AI CLI Skill

Repository: https://github.com/NarratorAI-Studio/narrator-ai-cli-skill

Local review snapshot:

- Clone reviewed outside this repository.
- Git commit: `32076844614836812cedbffd1b69010b1e8c26e8`
- License: MIT

What it is:

- A machine-readable AI-agent skill for the external `narrator-ai-cli`.
- It targets movie, drama, and video narration workflows.
- It requires `narrator-ai-cli` and a `NARRATOR_APP_KEY`.
- The external pipeline covers source selection, BGM, dubbing voice, narration template, script generation, clip data, video composing, and optional visual-template generation.

Useful ideas for KVAE:

- Keep resource choices explicit. Do not auto-select source material, BGM, dubbing voice, or templates.
- Keep the language chain consistent between dubbing voice, writing task, and visual template text.
- Paginate resource lists fully before search; do not trust truncated terminal output.
- Poll external asynchronous tasks until completion.
- Preserve exact task/order identifiers in handoff manifests.

Safe application:

- Add `external_video_narration_api` to `kva capabilities`.
- Add Narrator AI CLI Skill as an external replacement for `video_dubbing_editing`.
- KVAE should prepare Korean script/audio assets and review returned outputs.
- KVAE should not claim to provide the hosted material library, paid task submission, or video-composition API itself.

## 3. Open Generative AI

Repository: https://github.com/Anil-matcha/Open-Generative-AI

Local review snapshot:

- Clone reviewed outside this repository.
- Git commit: `894b520516ca5c87d62ec5bfd840d13ec71e3a04`
- License finding: README says MIT, but the reviewed snapshot did not expose a root `LICENSE` file and GitHub license metadata was not confirmed.

What it is:

- A separate image, video, cinema, workflow, and lip-sync studio.
- It supports hosted API workflows through Muapi and local desktop inference paths for some models.
- Its lip-sync studio can use audio to animate a portrait image or synchronize lips in existing video.

Useful ideas for KVAE:

- KVAE can hand off polished Korean WAV, transcript, timing notes, and disclosure metadata to a visual or lip-sync stage.
- The lip-sync/video stage should be separate from the Korean voice-quality engine.
- Local/remote model selection, hardware notes, and output provenance should be visible to users.

Safety and license boundary:

- The project advertises unrestricted or no-filter generation. KVAE should not adopt that posture.
- KVAE must keep consent, likeness rights, source provenance, AI disclosure, and publication review.
- Do not copy code into KVAE until the repository license is clarified.

Safe application:

- Add `visual_generation_lipsync` to `kva capabilities`.
- Add Open Generative AI as an external replacement for final visual/lip-sync assembly.
- Exchange only artifacts: WAV, TXT, SRT, JSON, timing notes, and reviewed output paths.
