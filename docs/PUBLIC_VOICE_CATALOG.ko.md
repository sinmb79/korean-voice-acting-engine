# 공개 한국어 AI 음성 카탈로그

[English document](PUBLIC_VOICE_CATALOG.md)

KVAE에는 공개 한국어 음성 옵션을 기본 카탈로그로 넣습니다. 이 카탈로그는 모델 weight나 데이터셋을 직접 포함하지 않고, 출처 링크, 라이선스, 표기문, AI 음성 고지, 설치 힌트만 저장합니다.

이 저장소에는 공개 모델 weight, 공개 데이터셋, private 음성, 생성 WAV 파일을 번들로 넣지 않습니다.

## 왜 메타데이터만 넣는가

공개되어 있다고 해서 항상 상업적으로 사용할 수 있는 것은 아닙니다. 한국어 공개 음성 모델 중 상당수는 KSS 데이터셋에서 파생되며, KSS는 비상업/share-alike 조건을 가집니다.

그래서 KVAE는 이 음성들을 “설치 가능한 공개 음성 후보”로 제공하되, 라이선스 제한과 AI 음성 고지를 명확히 표시합니다.

## CLI

공개 음성 목록:

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine public-voices
```

특정 음성 보기:

```powershell
python -m kva_engine public-voices --id mms-tts-kor
```

KVAE voice profile 형태로 보기:

```powershell
python -m kva_engine public-voices --id mms-tts-kor --profile
python -m kva_engine voice-profile public:mms-tts-kor
```

라이선스 안전 설치 계획 만들기:

```powershell
python -m kva_engine public-voices `
  --id mms-tts-kor `
  --install-plan `
  --install-root C:\kvae-public-voices `
  --out outputs\mms-tts-kor.install-plan.json
```

KVAE는 외부 모델 파일을 자동 다운로드하지 않습니다. install plan에는 출처, 라이선스, 표기문, 고지문, target folder, 경고, 수동 명령 제안만 기록합니다.

수동 검토가 필요한 항목까지 보기:

```powershell
python -m kva_engine public-voices --include-experimental
```

## 기본 카탈로그 항목

| id | 출처 | 라이선스 | 기본 상태 |
| --- | --- | --- | --- |
| `mms-tts-kor` | Meta MMS-TTS Korean | CC-BY-NC-4.0 | 비상업 기본 후보 |
| `neurlang-piper-kss-korean` | Piper ONNX KSS Korean | CC-BY-NC-SA-4.0 | 비상업/share-alike 기본 후보 |
| `neurlang-coqui-vits-kss-korean` | Coqui VITS KSS Korean | CC-BY-NC-SA-4.0 | 비상업/share-alike 기본 후보 |
| `kss-dataset-reference` | KSS Dataset | NC-SA 4.0 | 데이터셋 출처, 번들 음성 아님 |
| `tensorspeech-fastspeech2-kss-ko` | TensorSpeech FastSpeech2 KSS | 모델 카드는 Apache-2.0, upstream KSS는 비상업/share-alike | 수동 검토 |
| `skytinstone-tacotron-minseok` | Full-Tuned Tacotron MinSeok | 모델 카드상 MIT | 실험 항목, 수동 검토 |

## 필수 고지

권장 생성물 고지:

```text
이 음성은 KVAE와 공개 한국어 AI 음성 모델을 사용해 생성 또는 보조 생성된 AI 음성입니다. 출처, 라이선스, 표기는 KVAE manifest를 확인하세요.
```

영문:

```text
This audio is AI-generated or AI-assisted speech produced with KVAE using a public Korean AI voice model. See the KVAE manifest for source, license, and attribution.
```

## 확인한 출처

- https://huggingface.co/facebook/mms-tts-kor
- https://huggingface.co/neurlang/piper-onnx-kss-korean
- https://huggingface.co/neurlang/coqui-vits-kss-korean
- https://huggingface.co/datasets/Bingsu/KSS_Dataset
- https://huggingface.co/tensorspeech/tts-fastspeech2-kss-ko
- https://huggingface.co/skytinstone/full-tuned-tacotron-minseok
