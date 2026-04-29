# External Review: Voice-Pro And Nemotron-Personas-Korea

[Korean document](EXTERNAL_REVIEW_VOICE_PRO_NEMOTRON.ko.md)

## Voice-Pro

Repository: https://github.com/abus-aikorea/voice-pro

Local review clone: outside this repository, under the user's workspace external-review area.

License finding:

- GitHub reports GNU GPLv3.
- The cloned `LICENSE` file is GNU GPL v3.
- KVAE is Apache-2.0, so Voice-Pro code should not be copied into KVAE.

Useful ideas for KVAE:

- Treat ASR, subtitle, translation, demixing, TTS, and voice-cloning as separate tabs/stages.
- Exchange artifacts between tools through WAV, SRT, TXT, JSON, and manifests.
- Keep model-heavy tools optional and external.
- Use a WebUI for creators, but keep KVAE's core CLI small and testable.

How to apply safely:

- Add Voice-Pro as an external replacement in `kva capabilities`.
- Use Voice-Pro for separate experiments with Whisper, Demucs, Edge-TTS, F5-TTS, CosyVoice, RVC, subtitles, and translation.
- Bring outputs back to KVAE for `kva review-audio`, provenance notes, and use-case polish.
- Do not vendor Voice-Pro source files into KVAE.

## NVIDIA Nemotron-Personas-Korea

Dataset: https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea

License: CC-BY-4.0.

Observed dataset traits:

- Korean text dataset.
- Synthetic personas.
- 1,000,000 rows.
- 26 fields including persona fields, attributes, demographic/geographic context, and UUID.
- Adult personas only, age 19 and older.
- No audio, no voice embeddings, no speaker recordings.

Useful ideas for KVAE:

- Generate more diverse Korean recording prompts.
- Create persona-aware drama, shorts, education, documentary, and announcement scripts.
- Improve evaluation coverage for age, region, occupation, family context, hobbies, and speaking situations.
- Avoid generic Seoul-only, young-only, office-only examples.

How to apply safely:

- Add a `persona_script_coverage` route in `kva capabilities`.
- Use the dataset as a text prompt source, not as voice training data.
- Cite NVIDIA Nemotron-Personas-Korea when prompts or evaluation cases are derived from it.
- Do not claim it provides child voices or real-person identities.
