# KVAE Review Engine

[한국어 문서](KVAE_REVIEW_ENGINE.ko.md)

KVAE records a review report after audio generation or conversion. The goal is to avoid stopping at "a file was created" and instead check whether the output is structurally valid before a human listens to it.

## review-audio

Review a generated or converted WAV file:

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf.wav `
  --expected-file outputs\script.txt `
  --asr-model base `
  --role wolf_growl `
  --out outputs\wolf.review.json
```

If Whisper is not installed, or if you already have a transcript, pass `--asr-text`:

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf.wav `
  --expected-text "This is a test." `
  --asr-text "This is a test." `
  --out outputs\wolf.review.json
```

The report includes:

- WAV existence, duration, sample rate, channels, RMS, peak, and silence ratio
- Whisper transcript or provided ASR text
- CER and WER
- clipping, long silence, low volume, and short-audio warnings
- voice profile privacy and redistribution boundaries

## recording-check

Check a raw recording before using it for training:

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

Current rules are conservative:

- Recordings shorter than 30 seconds are marked as too short for meaningful training.
- 44.1kHz or 48kHz mono WAV is recommended for production training.
- Long silence, possible clipping, very low peak, and very low RMS are flagged.

## Reading The Result

`ok: true` means the automatic review found no critical issue. It does not guarantee professional voice acting quality.

For character conversion, stronger creature effects can reduce ASR scores. Use clear roles for dialogue and heavy/fx/roar roles for performance texture.
