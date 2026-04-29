# Capability Routing

[Korean document](CAPABILITY_ROUTING.ko.md)

KVAE now uses a stricter product boundary:

- **Do in KVAE** when the task is Korean script preparation, recording review, privacy-safe training preparation, or Korean voice polish that preserves the source speaker.
- **Route outside KVAE** when the task needs a different human speaker, a convincing child voice, creature/dinosaur sound design, heavy dialogue repair, or full video dubbing/editing.
- **Keep as research only** when a KVAE feature is useful for experiments but has not reached production quality.

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine capabilities --production-only
python -m kva_engine capabilities --task child_or_age_voice --compact
```

## Production KVAE Scope

KVAE should ship these as normal user-facing features:

- `kva normalize`, `kva ssml`, and `kva cast` for Korean speech-script preparation
- `kva recording-check`, `kva review-audio`, and training-data preparation commands
- `kva polish` for cleanup, announcer, shorts, drama, and documentary voice polish

These features preserve the speaker identity. They do not promise a new actor, child, monster, wolf, or dinosaur.

## External Replacement Scope

Some jobs need specialist tools:

- Different human speaker: speech-to-speech tools such as [Resemble AI Speech-to-Speech](https://www.resemble.ai/products/speech-to-speech) or [ElevenLabs Voice Changer](https://elevenlabs.io/voice-changer), with consented target voices.
- Child or age-transformed voice: licensed voice libraries or dubbing tools such as [NAVER Cloud CLOVA Dubbing](https://guide.ncloud-docs.com/docs/en/clovadubbing-overview) or [Vrew](https://vrew.ai/ko/).
- Creature, monster, or dinosaur: sound-design tools such as [Krotos Dehumaniser 2](https://www.krotosaudio.com/dehumaniser2/) plus a DAW and license-safe source layers.
- Heavy noise, echo, or reverb repair: [iZotope RX Dialogue Isolate](https://www.izotope.com/en/products/rx/features/dialogue-isolate), [Adobe Podcast Enhance Speech](https://podcast.adobe.com/en/enhance-speech-v2), or [Descript Studio Sound](https://help.descript.com/hc/en-us/articles/10327603613837-Studio-Sound).
- Local all-in-one experimentation: [Voice-Pro](https://github.com/abus-aikorea/voice-pro) can be used as a separate GPLv3 WebUI for ASR, subtitles, translation, TTS, and voice-cloning tests. KVAE should exchange artifacts with it, not copy its code.
- Final video assembly: Vrew, DaVinci Resolve/Fairlight, or another editor.

## Persona Dataset Scope

[NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) is useful for Korean persona diversity in script prompts and review cases. It is not an audio dataset and does not provide voice recordings, speaker embeddings, or child voices. KVAE can use it for text-only prompt coverage with attribution under CC-BY-4.0.

## Recommended Creator Flow

1. Prepare the Korean script in KVAE.
2. Record or import a clean source WAV.
3. Run `kva recording-check`.
4. Run `kva polish` with the right use-case preset.
5. If the request is outside KVAE's reliable scope, use the capability route to choose the replacement tool.
6. Bring the final audio back to `kva review-audio` and keep disclosure/provenance metadata.

This keeps KVAE honest: it does what it can do well, and it stops pretending when a specialist tool or a human actor is the right answer.
