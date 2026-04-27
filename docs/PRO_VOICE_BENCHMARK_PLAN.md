# Professional Voice Product Benchmark Plan

[한국어 문서](PRO_VOICE_BENCHMARK_PLAN.ko.md)

Created: 2026-04-27  
Updated: 2026-04-28

## Conclusion

KVAE should not be just a text-to-speech wrapper. It should become a Korean-first voice acting engine with three product layers:

1. Text-to-Speech: generate natural Korean speech from text.
2. Speech-to-Speech: transform a user's recorded performance into another role while preserving timing, pauses, and acting intent.
3. Character Voice Design: create reusable character voices such as wolf, monster, dinosaur, child, villain, narrator, teacher, and news anchor.

A short private voice profile can prove the local path, but it is too short for professional-quality cloning. Production-quality training needs more clean data.

## Official Product Signals Checked On 2026-04-28

- ElevenLabs Professional Voice Clone recommends at least 30 minutes of high-quality audio and says the best results come closer to 2-3 hours. It also recommends using the same language as the intended generated speech and avoiding mixed styles in one clone.
- Supertone Shift focuses on real-time voice changing. KVAE's `convert` workflow should learn from that immediate performance-to-character user experience.
- Humelo DIVE and Prosody show the importance of Korean enterprise voice cloning, TTS APIs, and Korean-first quality expectations.
- NAVER CLOVA Dubbing shows that the final product should connect voice generation to video/dubbing workflows, not stop at WAV export.

References:

- https://elevenlabs.io/docs/product-guides/voices/voice-cloning/professional-voice-cloning
- https://www.supertone.ai/ko/shift
- https://humelo.com/dive
- https://console.humelo.com/
- https://help.naver.com/service/23823?lang=en

## Training Data Target

### Base Speaker Voice

- Minimum: 10 minutes
- Practical professional minimum: 30 minutes
- Preferred target: 60-120 minutes
- Format: clean mono WAV, 44.1kHz or 48kHz
- Recording condition: same room, same microphone, stable distance, low noise

### Korean Pronunciation Coverage

The dataset should cover:

- numbers, dates, times, phone numbers, amounts, percentages
- English abbreviations such as AI, API, TTS, JSON, GPT, LoRA, KVAE
- tense consonants, aspirated consonants, nasal sounds, liaison, and final consonants
- polite speech, casual speech, news style, narration, and storytelling
- short sentences and long connected sentences

### Role Acting Data

For each major role, collect at least 20 sentences and preferably 50+ sentences:

- calm_narrator
- documentary
- news_anchor
- bright_teacher
- old_storyteller
- villain_low
- wolf_growl
- monster_deep
- dinosaur_giant
- child_bright

### Speech-to-Speech Data

For speech-to-speech conversion, the same sentence should be recorded with different acting intentions:

- neutral actor
- whisper
- anger
- smiling speech
- fear
- creature-like roughness
- fast and bright childlike delivery

This teaches the engine how the same content changes when the performance changes.

## Product Lessons

### ElevenLabs

Lessons:

- Separate quick clone from professional clone.
- Make data requirements explicit.
- Separate text-to-speech from speech-to-speech.
- Provide voice design as a first-class workflow.

KVAE application:

- Keep `train-native`, `render`, `convert`, and `review-audio` as separate commands.
- Make 30 minutes a real threshold for professional training readiness.
- Store review reports with every generated sample.

### Supertone Shift

Lessons:

- Real-time or near-real-time voice changing is a product experience, not just a model feature.
- Character voice choice, pitch, timbre, and performance strength should be adjustable.

KVAE application:

- Separate identity strength and role strength.
- Keep `*_clear`, default, heavy/fx/roar role families.
- Make character roles reusable presets, not one-off effects.

### Humelo DIVE / Prosody

Lessons:

- Korean-first quality, API use, and SSML/pronunciation control matter.
- Enterprise voice products need repeatable review and quality reports.

KVAE application:

- Keep Korean normalization and pronunciation dictionaries as core features.
- Record CER/WER, loudness, clipping, and sample-rate checks in review manifests.
- Provide a local API or app layer later.

### NAVER CLOVA Dubbing

Lessons:

- Many users need voice generation inside a video/dubbing workflow.
- Licensing, consent, and commercial-use boundaries must be clear.

KVAE application:

- The long-term product should support shorts/video editing pipelines.
- Voice profiles must record consent and redistribution boundaries.

## Implementation Priority

### Phase A. Training Data Expansion

- 30-minute Korean recording script
- recording-check CLI
- automatic silence and segment checks
- Whisper reverse transcription
- train/validation/test split

### Phase B. Speech-to-Speech Conversion

```powershell
python -m kva_engine convert --input my_acting.wav --role wolf_growl --out wolf.wav
```

This is the core feature for users who want to act once and generate multiple character voices from the same performance.

### Phase C. Character Preset Refinement

- `wolf_growl_clear` and `wolf_growl_heavy`
- `monster_deep_clear` and `monster_deep_fx`
- `dinosaur_giant_clear` and `dinosaur_giant_roar`
- child voice controls beyond pitch: articulation, speed, sentence length, and clarity

### Phase D. Professional Review Reports

Every sample should store:

- source script
- ASR transcript
- WER/CER
- loudness
- clipping risk
- intelligibility warning
- character consistency notes
- speaker identity preservation notes

## Product Definition

KVAE's target product statement:

> A local Korean voice acting engine where a user records their own Korean performance, and the engine preserves the acting intent while transforming the voice identity into reusable character and actor roles.
