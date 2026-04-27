# Codex 기반 학습 워크플로

[English document](CODEX_TRAINING_WORKFLOW.md)

KVAE는 Codex가 보스 PC에서 로컬 학습과 검증 루프를 직접 실행할 수 있도록 설계합니다.

저장소는 공개 가능한 엔진으로 유지하고, 보스의 음성 데이터는 로컬 private 폴더에 둡니다.

## 설계 원칙

Codex는 private 녹음 파일을 GitHub나 공개 데이터셋에 올릴 필요가 없습니다. Codex는 로컬 작업자 역할을 합니다.

1. 로컬 음성 프로필 확인
2. 녹음 품질 점검
3. 학습 manifest 생성
4. KVA 네이티브 음성 모델 기록 생성
5. 샘플 렌더 또는 변환
6. 오디오 리뷰와 전사 정확도 측정
7. 재사용 가능한 코드, 문서, 테스트, 공개 예제만 커밋

## 폴더 계약

권장 private 음성 위치:

```text
C:\Users\you\workspace\shared-voices\my-voice-profile
```

권장 public 엔진 위치:

```text
C:\Users\you\workspace\KVAE
```

public 저장소는 ignored local config로 private 경로를 참조할 수 있습니다.

```text
configs/default_voice.local.json
```

이 파일은 커밋하면 안 됩니다.

## 1. 음성 프로필 확인

```powershell
$env:PYTHONPATH = "src"
python -m kva_engine voice-profile
```

KVAE가 어떤 로컬 private 음성 프로필을 사용할지 확인합니다.

## 2. 원본 녹음 품질 점검

```powershell
python -m kva_engine recording-check `
  --audio C:\Users\you\workspace\shared-voices\my-voice-profile\references\voice_ko_reference.wav `
  --out outputs\recording-check.json
```

길이, 샘플레이트, 채널, peak, RMS, silence ratio, 학습 적합성 경고를 확인합니다.

## 3. 로컬 학습 모델 기록 생성

```powershell
python -m kva_engine train-native `
  --registry C:\Users\you\workspace\shared-voices `
  --profile-id my-voice-profile `
  --out outputs\family_voice_training\kva_native_voice_model.json
```

이 명령은 KVA 네이티브 통계 음성 모델 기록을 준비합니다. KVAE가 학습 seed로 사용할 수 있는 로컬 메타데이터와 acoustic profile 계층입니다.

## 4. 텍스트에서 렌더

```powershell
python -m kva_engine render `
  --file script.txt `
  --role calm_narrator `
  --out outputs\calm_narrator.wav `
  --json-out outputs\calm_narrator.result.json `
  --manifest-out outputs\calm_narrator.manifest.json
```

로컬 VoxCPM 런타임이 설정되어 있으면 한국어 텍스트에서 음성을 생성합니다.

## 5. 녹음 연기 변환

```powershell
python -m kva_engine convert `
  --input my_performance.wav `
  --role wolf_growl_clear `
  --out outputs\wolf_growl_clear.wav `
  --json-out outputs\wolf_growl_clear.result.json `
  --manifest-out outputs\wolf_growl_clear.manifest.json
```

원본 연기의 타이밍과 호흡은 유지하면서 선택한 역할 프리셋을 적용합니다.

## 6. 결과 리뷰

```powershell
python -m kva_engine review-audio `
  --audio outputs\wolf_growl_clear.wav `
  --expected-file script.txt `
  --asr-model base `
  --role wolf_growl_clear `
  --out outputs\wolf_growl_clear.review.json
```

오디오 품질, 선택적 Whisper ASR, CER, WER, 경고를 기록합니다.

## 7. 공개 가능한 파일만 커밋

커밋 전 확인:

```powershell
git status --short
python -m unittest discover -s tests
python -m compileall -q src
```

커밋하지 않을 것:

- private 음성 녹음
- local config 파일
- 개인 음성이 들어간 dataset
- LoRA checkpoint
- 생성된 WAV/MP3/FLAC/M4A 파일
- private model weight

커밋할 것:

- 소스 코드
- 공개 예제
- 테스트
- 영어 문서
- 선택 한국어 문서

## 현재 한계

현재 로컬 학습 명령은 KVA 네이티브 통계 음성 모델 기록을 준비합니다. 완전한 신경망 음성 합성 학습에는 PyTorch, 한국어 acoustic model, duration/pitch/energy predictor, vocoder 같은 로컬 ML 스택이 필요합니다.

KVAE는 CLI 계약을 안정적으로 유지하여 나중에 neural backend를 붙여도 사용자 워크플로가 바뀌지 않게 합니다.
