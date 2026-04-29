# Korean Voice Polish Engine

[Korean document](KOREAN_VOICE_POLISH_ENGINE.ko.md)

KVAE's practical product direction is Korean voice polish, not magical transformation into unrelated actors, children, monsters, or dinosaurs.

`kva polish` keeps the source speaker identity and prepares the recording for a real use case:

- `cleanup`: light natural cleanup
- `announcer`: clear Korean announcer-style speech
- `shorts`: tighter and louder short-form narration
- `drama`: softer dialogue polish that preserves acting breath
- `documentary`: warm long-form narration

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine polish `
  --input my_voice.wav `
  --preset announcer `
  --out outputs\my_voice.announcer.wav `
  --manifest-out outputs\my_voice.announcer.json
```

## What It Does

The engine applies KVAE-owned deterministic DSP:

- DC removal
- high-pass and low-pass cleanup
- warmth, clarity, presence, and air EQ
- de-essing
- soft noise-floor control
- speech compression
- peak normalization
- safety manifest explaining that the speaker identity is preserved

## What It Does Not Claim

The polish engine does not claim to create a new speaker, a child voice, a creature voice, or a professional actor from one adult source recording.

Those transformations may become possible with larger Korean datasets, consented target voices, neural speech-to-speech models, and human A/B review. They are not the default product promise for KVAE's current public engine.

## Product Promise

KVAE should help Korean creators make their own voice usable:

- clearer pronunciation delivery
- cleaner narration
- more stable loudness
- use-case presets for shorts, drama, documentary, announcements, and education
- local-first handling of private voice assets

This is a smaller promise, but it is honest and useful.
