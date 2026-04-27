# KVAE Convert Engine

[한국어 문서](KVAE_CONVERT_ENGINE.ko.md)

`kva convert` takes a recorded voice performance as input and turns it into a KVAE role or character voice.

```powershell
python -m kva_engine convert `
  --input my_acting.wav `
  --role monster_deep `
  --out outputs\monster.wav
```

## Current Engine

The current implementation is `kva-convert-ffmpeg-v1`.

- It preserves the original performance timing and breath.
- It applies role-specific pitch, tempo, EQ, roughness, and echo controls.
- It applies loudness normalization.
- It writes a WAV file and a manifest.

This is the deterministic local conversion layer. It gives users an immediate offline character-voice workflow while KVAE keeps the same CLI contract for future neural speech-to-speech backends.

## Future Neural Backends

The same command contract can later be backed by:

- RVC-style voice conversion
- FreeVC-style speech-to-speech conversion
- so-vits-svc-style singing/speech conversion
- KVAE's own Korean speech-to-speech model

## Examples

```powershell
python -m kva_engine convert --input voice.wav --role wolf_growl --out wolf.wav
python -m kva_engine convert --input voice.wav --role wolf_growl_clear --out wolf-clear.wav
python -m kva_engine convert --input voice.wav --role wolf_growl_heavy --out wolf-heavy.wav
python -m kva_engine convert --input voice.wav --role monster_deep --out monster.wav
python -m kva_engine convert --input voice.wav --role monster_deep_clear --out monster-clear.wav
python -m kva_engine convert --input voice.wav --role monster_deep_fx --out monster-fx.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant --out dinosaur.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant_clear --out dinosaur-clear.wav
python -m kva_engine convert --input voice.wav --role dinosaur_giant_roar --out dinosaur-roar.wav
python -m kva_engine convert --input voice.wav --role child_bright --out child.wav
```

## Review After Conversion

Run `review-audio` after conversion:

```powershell
python -m kva_engine review-audio `
  --audio wolf.wav `
  --expected-file script.txt `
  --asr-model base `
  --role wolf_growl `
  --out wolf.review.json
```

Strong character effects such as `monster_deep_fx` and `dinosaur_giant_roar` may reduce intelligibility. For dialogue, prefer `*_clear` roles first and keep heavy/fx/roar roles as performance options.
