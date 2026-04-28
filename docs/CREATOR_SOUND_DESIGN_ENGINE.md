# Creator Sound Design Engine

[Korean document](CREATOR_SOUND_DESIGN_ENGINE.ko.md)

KVAE's creator sound design engine exists to translate major-studio voice and sound-effect workflows into a free, local-first tool for small creators.

The goal is not to copy famous movie or game sounds. KVAE should copy the method: acting direction, source collection, Foley, animal and synthetic layers, transformation, mix, review, provenance, license, and AI disclosure.

```mermaid
flowchart LR
  A["Major studio method"] --> B["KVAE technique catalog"]
  B --> C["License-safe source library"]
  C --> D["Performance controller"]
  D --> E["Layer recipe"]
  E --> F["Render and review"]
  F --> G["Creator export"]
```

## What Studios Do

Public interviews and professional sound-design material show a repeatable pattern:

- decide the story intent before choosing sounds
- record or license clean source material
- use actors or guide tracks for timing and emotional force
- layer animal, Foley, synthetic, mechanical, and ambience sources
- transform sources with pitch, time, EQ, saturation, reversal, morphing, filtering, and convolution
- mix the layers so they feel like one body in one space
- generate multiple candidates and judge them against the picture

For creatures, the human voice is usually not the whole final sound. It can be the performance controller, but animal recordings, Foley, physical props, synthesis, and heavy processing make the final creature feel nonhuman.

## What KVAE Implements Now

- `kva benchmarks` stores voice-acting theory, professional voice product lessons, bioacoustic research, and major-studio sound-design techniques.
- `kva source-library` exposes the source registry schema and license/privacy rules.
- `kva creature-design --role dinosaur_giant_roar` creates a layer recipe that removes audible human speech identity.
- `kva convert` and `kva voice-lab` remain the human-character workflow.
- `kva-bioacoustic-dinosaur-v3` renders dinosaur roles from performance envelope only, not from audible speech identity.

## Source Library Rules

Every source layer must keep:

- source id and display name
- source type
- origin and creator/provider
- license and attribution
- AI or synthetic disclosure
- permitted use
- privacy level
- tags and notes

Blocked sources:

- ripped movie or game sounds
- unlicensed commercial libraries
- a real person's voice without explicit consent
- private voice recordings committed to the public repository

## Current Creature Recipe Direction

Dinosaur roles should not leave weak human articulation hints. The actor recording can drive duration, energy, attack, release, and emotional contour, but the audible output should be built from non-speech body layers:

- performance envelope
- body rumble
- closed-mouth boom
- throat grit
- wideband roar air
- environment and scale

Wolf and monster roles can have clear variants when intelligibility is desired, but heavy FX variants should move toward layered creature design.

## Roadmap

Next implementation phases:

- `kva source-library add/scan/validate`
- waveform indexing and source tagging
- `kva creature-design render` to turn recipes into audio layers
- Foley and action spotting for video clips
- A/B/C candidate generation with human listening scores
- local UI with compare, bypass, source/license display, and export

## Reference Anchors

- Audubon on bird recordings in *Jurassic World*: https://www.audubon.org/magazine/jurassic-worlds-dinosaurs-roar-life-thanks-bird-calls
- Motion Picture Association interview on *Jurassic World: Fallen Kingdom*: https://www.motionpictures.org/2018/06/sound-designer-gives-voice-to-the-jurassic-world-fallen-kingdom-dinosaurs/
- Slashfilm on the *Jurassic Park* T-Rex composite roar: https://www.slashfilm.com/1310511/jurassic-park-got-t-rex-roar-from-combination-of-three-different-animals/
- Sound On Sound on sound design for visual media: https://www.soundonsound.com/techniques/sound-design-visual-media
- BOOM Library on animal sound recording: https://www.boomlibrary.com/blog/how-to-record-animal-sound-effects/
- Pro Sound Effects creature sound design tutorial: https://blog.prosoundeffects.com/creature-sound-design-tutorial?switchLanguage=ja
- StarWars.com Skywalker Sound interview: https://www.starwars.com/news/skeleton-crew-skywalker-sound-interview
- StarWars.com Ben Burtt interview: https://www.starwars.com/news/empire-at-40-ben-burtt-interview
- Backstage on *A Quiet Place Part II* sound: https://www.backstage.com/magazine/article/a-quiet-place-part-two-sound-editors-interview-73319/
- Space.com on *Project Hail Mary* alien voice design: https://www.space.com/entertainment/space-movies-shows/project-hail-mary-sound-designers-used-surprising-animal-sounds-to-create-rockys-musical-alien-voice-interview
- National Center for Voice and Speech: https://ncvs.org/
- SAG-AFTRA AI resources: https://www.sagaftra.org/contracts-industry-resources/member-resources/artificial-intelligence
