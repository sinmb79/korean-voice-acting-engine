# 가족 음성 레지스트리 기반 학습 기록

메타 설명: 가족 음성 레지스트리를 외부 전송 없이 분석해 한국어 성우 엔진 학습 입력으로 정리한 로컬 실행 기록.

태그: 한국어 TTS, 가족 음성 레지스트리, 성우 엔진, 로컬 학습, 보안 환경, 음성 프로필

## 왜 이 단계가 필요한가

가족의 목소리는 단순한 오디오 파일이 아니라 한 사람의 신체적 흔적입니다. 그래서 이 프로젝트의 첫 학습 단계는 모델을 무작정 돌리는 일이 아니라, 어떤 음성이 있고, 어떤 동의와 안전 장치가 필요하며, 어떤 프로필이 이미 LoRA 어댑터를 가지고 있는지 확인하는 일부터 시작합니다.

현재 보안 환경에는 `torch`, `torchaudio`, `numpy`, `soundfile`, `librosa`가 없습니다. 따라서 이번 실행에서 신경망 fine-tuning을 직접 수행하지는 않았습니다. 대신 표준 라이브러리만 사용해 로컬 음성 학습 매니페스트를 만들었습니다. 이 매니페스트는 나중에 GPU가 있는 안전한 환경에서 실제 학습기로 넘길 입력 계약입니다.

## 실행한 명령

레지스트리 검증:

```powershell
python D:\Workspace\22b-family-voice-registry\scripts\validate_registry.py
```

학습 매니페스트 생성:

```powershell
cd D:\Workspace\Korean-Voice-Acting-Engine
$env:PYTHONPATH = "src"
python -m kva_engine train-profile `
  --registry D:\Workspace\22b-family-voice-registry `
  --out outputs\family_voice_training\registry_training_manifest.json
```

테스트:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
python -m compileall -q src
```

## 생성된 산출물

`outputs\family_voice_training\registry_training_manifest.json`

이 파일은 `.gitignore` 정책상 공개 저장소에 포함되지 않습니다. 오디오 파일을 복사하지 않고, 원본 경로, SHA-256, WAV 메타데이터, RMS/peak/silence ratio, 기존 LoRA 어댑터 상태만 기록합니다.

## 이번 실행 요약

- 프로필: 12개
- 언어 프로필: 16개
- 분석된 오디오 클립: 44개
- 총 오디오 길이: 약 591.996초
- 기존 LoRA가 있는 언어 프로필: 12개
- 역할 분포: father 4개, daughter 4개, son 4개
- 신경망 학습 가능 여부: 현재 환경에서는 불가

## 역할별 상태

- father: 기본, shorts, anime, lecture 프로필이 있고 Korean LoRA 어댑터가 존재합니다.
- daughter: 기본, shorts, anime, lecture 프로필이 있고 Korean/English LoRA 어댑터가 존재합니다.
- son: 기본, shorts, anime, lecture 프로필이 있고 음성 참조는 준비되어 있으나 LoRA 어댑터는 아직 설정되지 않았습니다.

## 구현된 안전 원칙

- 오디오 파일을 프로젝트로 복사하지 않습니다.
- 네트워크 업로드를 하지 않습니다.
- 공개 배포 대상은 코드와 예시 스키마이며, 가족 음성 원본은 제외합니다.
- 가족 음성은 `biometric_sensitive`로 취급합니다.
- 실제 공개 샘플 생성 전에는 가족 구성원의 동의와 공개 범위를 별도 확인해야 합니다.

## 다음 학습 단계

1. 오프라인 GPU 환경에 필요한 패키지와 모델 가중치를 별도 반입합니다.
2. 이번 매니페스트를 입력으로 받아 `father`, `daughter`, `son` 별 학습 큐를 만듭니다.
3. `son` 프로필은 LoRA가 없으므로 우선순위를 높여 어댑터를 새로 학습합니다.
4. 한국어 엔진의 `speech_script`와 성우 엔진의 `role plan`을 함께 넣어, 같은 목소리에서 역할별 억양 차이가 생기는지 평가합니다.
5. 생성 음성은 ASR 재인식, 발음 사전 보정, 사람 리뷰를 거쳐 correction memory에 반영합니다.

## 현재 결론

이번 단계는 “신경망을 돌렸다”가 아니라 “가족 음성을 안전하게 학습 가능한 상태로 정리했다”가 정확합니다. 성급한 학습은 데이터의 윤리를 놓치기 쉽습니다. 목소리는 먼저 보호되어야 하고, 그 다음에 표현되어야 합니다.

작성자: **22B Labs · 제4의 길 (The 4th Path)**
