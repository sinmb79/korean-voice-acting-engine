# Public Korean AI Voice Catalog

[한국어 문서](PUBLIC_VOICE_CATALOG.ko.md)

KVAE includes a small built-in catalog of public Korean voice options. The catalog stores metadata only: source links, licenses, attribution text, AI voice disclosure, and install hints.

KVAE does not bundle public model weights, public datasets, private voices, or generated WAV files in this repository.

## Why Metadata Only

Public does not always mean commercially usable. Several Korean voice models are trained from KSS, whose license is non-commercial/share-alike. For that reason, KVAE treats these voices as installable references and marks license limits explicitly.

Every generated output from these voices should disclose that it is AI-generated or AI-assisted speech.

## CLI

List public voice options:

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine public-voices
```

Show one voice:

```powershell
python -m kva_engine public-voices --id mms-tts-kor
```

Return a KVAE voice profile:

```powershell
python -m kva_engine public-voices --id mms-tts-kor --profile
python -m kva_engine voice-profile public:mms-tts-kor
```

Include entries that require manual review:

```powershell
python -m kva_engine public-voices --include-experimental
```

## Default Catalog Entries

| id | source | license | default status |
| --- | --- | --- | --- |
| `mms-tts-kor` | Meta MMS-TTS Korean | CC-BY-NC-4.0 | non-commercial default candidate |
| `neurlang-piper-kss-korean` | Piper ONNX KSS Korean | CC-BY-NC-SA-4.0 | non-commercial/share-alike default candidate |
| `neurlang-coqui-vits-kss-korean` | Coqui VITS KSS Korean | CC-BY-NC-SA-4.0 | non-commercial/share-alike default candidate |
| `kss-dataset-reference` | KSS Dataset | NC-SA 4.0 | dataset source, not a bundled voice |
| `tensorspeech-fastspeech2-kss-ko` | TensorSpeech FastSpeech2 KSS | model card says Apache-2.0; upstream KSS is non-commercial/share-alike | manual review |
| `skytinstone-tacotron-minseok` | Full-Tuned Tacotron MinSeok | model card says MIT | experimental manual review |

## Required Disclosure

Recommended generated-output notice:

```text
This audio is AI-generated or AI-assisted speech produced with KVAE using a public Korean AI voice model. See the KVAE manifest for source, license, and attribution.
```

Korean:

```text
이 음성은 KVAE와 공개 한국어 AI 음성 모델을 사용해 생성 또는 보조 생성된 AI 음성입니다. 출처, 라이선스, 표기는 KVAE manifest를 확인하세요.
```

## Sources Checked

- https://huggingface.co/facebook/mms-tts-kor
- https://huggingface.co/neurlang/piper-onnx-kss-korean
- https://huggingface.co/neurlang/coqui-vits-kss-korean
- https://huggingface.co/datasets/Bingsu/KSS_Dataset
- https://huggingface.co/tensorspeech/tts-fastspeech2-kss-ko
- https://huggingface.co/skytinstone/full-tuned-tacotron-minseok
